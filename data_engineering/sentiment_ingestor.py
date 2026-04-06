"""
TFG: Motor de Análisis de Sentimiento de Mercado
================================================
Microservicio NLP que:
1. Descarga titulares de noticias crypto en tiempo real (RSS feeds)
2. Analiza su sentimiento con FinBERT (Positive/Negative/Neutral)
3. Almacena los resultados en TimescaleDB para consumo del bot

Fuentes de datos:
- CoinDesk RSS
- CoinTelegraph RSS
- Bitcoin.com News RSS

Ciclo: cada 5 minutos analiza los titulares más recientes.
Fallback: si todos los feeds fallan, usa titulares por defecto.
"""

import os
import time
import logging
from datetime import datetime, timezone

import pandas as pd
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline
from sqlalchemy import create_engine, text

# ─── CONFIGURACIÓN ──────────────────────────────────────────────────────
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
DB_NAME = os.environ.get("POSTGRES_DB", "freqtrade")
DB_URL = f"postgresql://postgres:{DB_PASSWORD}@timescaledb:5432/{DB_NAME}"

MODEL_NAME = "ProsusAI/finbert"

# Fuentes RSS de noticias crypto (gratuitas, sin API key)
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Bitcoin.com": "https://news.bitcoin.com/feed/",
}

# Titulares de emergencia (fallback si todos los feeds fallan)
FALLBACK_HEADLINES = [
    "Bitcoin breaks resistance levels, analysts predict bull run",
    "Regulatory crackdown on crypto exchanges continues",
    "Ethereum fees drop significantly after upgrade",
    "Panic selling observed in altcoins market",
]

# Máximo de titulares a analizar por ciclo (para no saturar FinBERT)
MAX_HEADLINES_PER_CYCLE = 20

# ─── LOGGING ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def setup_database():
    """Crea la tabla de sentimientos y la convierte en hypertable si no existe."""
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_sentiment (
                time TIMESTAMPTZ NOT NULL,
                sentiment_score FLOAT,
                label VARCHAR(20),
                headline TEXT,
                source VARCHAR(50)
            );
        """))
        try:
            conn.execute(text(
                "SELECT create_hypertable('market_sentiment', 'time', if_not_exists => TRUE);"
            ))
        except Exception as e:
            logger.debug(f"Hypertable ya existe o error menor: {e}")
        conn.commit()
    return engine


def clean_html(raw_text: str) -> str:
    """Elimina etiquetas HTML de un string (los RSS a veces incluyen HTML)."""
    return BeautifulSoup(raw_text, "html.parser").get_text(strip=True)


def fetch_headlines() -> list[dict]:
    """
    Descarga titulares de todos los feeds RSS configurados.
    Retorna lista de {'title': str, 'source': str}.
    Si todos los feeds fallan, retorna titulares de fallback.
    """
    headlines = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"⚠️ Feed '{source_name}' devolvió error: {feed.bozo_exception}")
                continue

            for entry in feed.entries[:10]:  # Máximo 10 por fuente
                title = clean_html(entry.get("title", ""))
                if title and len(title) > 10:  # Filtrar títulos vacíos o muy cortos
                    headlines.append({"title": title, "source": source_name})

            logger.info(f"✅ {source_name}: {min(len(feed.entries), 10)} titulares descargados")

        except Exception as e:
            logger.error(f"❌ Error descargando {source_name}: {e}")

    # Fallback si no se obtuvo ningún titular
    if not headlines:
        logger.warning("⚠️ Todos los feeds fallaron. Usando titulares de fallback.")
        headlines = [{"title": h, "source": "fallback"} for h in FALLBACK_HEADLINES]

    # Limitar cantidad total
    return headlines[:MAX_HEADLINES_PER_CYCLE]


def analyze_sentiment(classifier, headlines: list[dict]) -> list[dict]:
    """
    Analiza el sentimiento de una lista de titulares con FinBERT.
    Retorna lista de dicts con score normalizado (-1 a +1).
    """
    titles = [h["title"] for h in headlines]
    results = classifier(titles, truncation=True)

    analyzed = []
    for i, res in enumerate(results):
        score = res["score"]
        if res["label"] == "negative":
            score *= -1
        elif res["label"] == "neutral":
            score = 0

        analyzed.append({
            "time": datetime.now(timezone.utc),
            "sentiment_score": round(score, 4),
            "label": res["label"],
            "headline": headlines[i]["title"],
            "source": headlines[i]["source"],
        })

    return analyzed


def save_to_db(engine, records: list[dict]):
    """Guarda los registros de sentimiento en TimescaleDB."""
    df = pd.DataFrame(records)
    df.to_sql("market_sentiment", engine, if_exists="append", index=False)
    logger.info(f"💾 {len(records)} registros guardados en TimescaleDB")


def main():
    """Ciclo principal del motor de sentimiento."""
    logger.info("=" * 60)
    logger.info("🧠 MOTOR DE SENTIMIENTO NLP (FinBERT) — TFG")
    logger.info("=" * 60)

    # 1. Cargar modelo FinBERT (primera vez descarga ~400MB)
    logger.info(f"📥 Cargando modelo {MODEL_NAME}...")
    classifier = pipeline("sentiment-analysis", model=MODEL_NAME)
    logger.info("✅ Modelo cargado correctamente")

    # 2. Configurar base de datos
    engine = setup_database()
    logger.info("✅ Base de datos configurada")

    # 3. Ciclo de análisis
    cycle_count = 0
    while True:
        cycle_count += 1
        try:
            logger.info(f"─── Ciclo #{cycle_count} ───")

            # Descargar titulares reales
            headlines = fetch_headlines()

            # Contar fuentes
            sources = {}
            for h in headlines:
                sources[h["source"]] = sources.get(h["source"], 0) + 1
            logger.info(f"📰 Titulares por fuente: {sources}")

            # Analizar con FinBERT
            records = analyze_sentiment(classifier, headlines)

            # Calcular sentimiento promedio
            avg_score = sum(r["sentiment_score"] for r in records) / len(records)
            logger.info(f"📊 SENTIMIENTO PROMEDIO: {avg_score:+.4f}")

            # Guardar en DB
            save_to_db(engine, records)

            # Esperar 5 minutos
            logger.info("⏳ Esperando 5 minutos para el siguiente ciclo...")
            time.sleep(300)

        except Exception as e:
            logger.error(f"❌ Error en ciclo de análisis: {e}")
            time.sleep(60)


if __name__ == "__main__":
    # Esperar a que TimescaleDB arranque
    logger.info("⏳ Esperando 15 segundos para que TimescaleDB arranque...")
    time.sleep(15)
    main()
