"""
TFG: Motor de Análisis de Sentimiento de Mercado v3.0
=====================================================
Microservicio NLP institucional que:
1. Descarga titulares de noticias crypto en tiempo real (RSS feeds)
2. Detecta qué criptomoneda menciona cada titular (NER - Named Entity Recognition)
3. Analiza su sentimiento con FinBERT (Positive/Negative/Neutral)
4. Almacena resultados PER-COIN en TimescaleDB para consumo del bot

MEJORAS v3.0 vs v2.0:
- NER per-coin: Sentimiento separado por moneda (BTC, ETH, SOL...) en vez de global
- Tabla coin_sentiment: Nueva tabla con granularidad por par de trading
- MLOps logging: Tracking de métricas del pipeline NLP (latencia, distribución)
- Fallback inteligente: Usa sentimiento global si no hay match de moneda
- Mayor robustez: Reintentos con backoff exponencial

Fuentes de datos:
- CoinDesk RSS
- CoinTelegraph RSS
- Bitcoin.com News RSS

Ciclo: cada 5 minutos analiza los titulares más recientes.
Fallback: si todos los feeds fallan, usa titulares por defecto.
"""

import os
import re
import time
import logging
import gc
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

# ─── MEJORA v3.0: NER (Named Entity Recognition) para criptomonedas ────
# Mapeo de nombres/alias → símbolo del par en Binance Futures
COIN_ALIASES = {
    "BTC": ["bitcoin", "btc", "₿"],
    "ETH": ["ethereum", "eth", "ether", "vitalik"],
    "SOL": ["solana", "sol"],
    "BNB": ["bnb", "binance coin", "binance"],
    "ADA": ["cardano", "ada"],
    "XRP": ["ripple", "xrp"],
    "DOT": ["polkadot", "dot"],
    "LINK": ["chainlink", "link"],
    "AVAX": ["avalanche", "avax"],
    "DOGE": ["dogecoin", "doge", "shiba"],
    "NEAR": ["near protocol", "near"],
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
    """
    Crea las tablas de sentimientos y las convierte en hypertables.
    v3.0: Añadida tabla coin_sentiment para sentimiento per-coin.
    """
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        # Tabla original (sentimiento global, retrocompatible)
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
            logger.debug(f"Hypertable market_sentiment ya existe: {e}")

        # MEJORA v3.0: Tabla de sentimiento por moneda (NER)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS coin_sentiment (
                time TIMESTAMPTZ NOT NULL,
                coin VARCHAR(10) NOT NULL,
                pair VARCHAR(30),
                sentiment_score FLOAT,
                label VARCHAR(20),
                headline TEXT,
                source VARCHAR(50)
            );
        """))
        try:
            conn.execute(text(
                "SELECT create_hypertable('coin_sentiment', 'time', if_not_exists => TRUE);"
            ))
        except Exception as e:
            logger.debug(f"Hypertable coin_sentiment ya existe: {e}")

        conn.commit()
    return engine


def clean_html(raw_text: str) -> str:
    """Elimina etiquetas HTML de un string (los RSS a veces incluyen HTML)."""
    return BeautifulSoup(raw_text, "html.parser").get_text(separator=" ", strip=True)


def detect_coins(title: str) -> list[str]:
    """
    MEJORA v3.0: NER (Named Entity Recognition) para criptomonedas.
    Detecta qué monedas menciona un titular usando un diccionario de aliases.
    
    Ejemplo:
        "Ethereum fees drop after upgrade" → ["ETH"]
        "Bitcoin and Solana surge" → ["BTC", "SOL"]
        "Crypto market drops" → [] (no se detecta ninguna moneda específica)
    
    Returns:
        Lista de símbolos de monedas detectadas (puede estar vacía).
    """
    title_lower = title.lower()
    detected = []
    for coin, aliases in COIN_ALIASES.items():
        for alias in aliases:
            # Buscar la palabra completa para evitar falsos positivos
            # (ej: "link" dentro de "hyperlink")
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, title_lower):
                if coin not in detected:
                    detected.append(coin)
                break  # No buscar más aliases del mismo coin
    return detected


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
    """Guarda los registros de sentimiento en TimescaleDB (tabla global)."""
    df = pd.DataFrame(records)
    df.to_sql("market_sentiment", engine, if_exists="append", index=False)
    logger.info(f"💾 {len(records)} registros guardados en market_sentiment")


def save_coin_sentiment(engine, records: list[dict]):
    """
    MEJORA v3.0: Guarda sentimiento per-coin en la tabla coin_sentiment.
    Para cada titular, detecta las monedas mencionadas y crea un registro
    por cada moneda detectada.
    """
    coin_records = []
    for record in records:
        coins = detect_coins(record["headline"])
        if coins:
            for coin in coins:
                coin_records.append({
                    "time": record["time"],
                    "coin": coin,
                    "pair": f"{coin}/USDT:USDT",
                    "sentiment_score": record["sentiment_score"],
                    "label": record["label"],
                    "headline": record["headline"],
                    "source": record["source"],
                })
        else:
            # Si no se detecta moneda, guardar como "GLOBAL"
            coin_records.append({
                "time": record["time"],
                "coin": "GLOBAL",
                "pair": "GLOBAL",
                "sentiment_score": record["sentiment_score"],
                "label": record["label"],
                "headline": record["headline"],
                "source": record["source"],
            })

    if coin_records:
        df = pd.DataFrame(coin_records)
        df.to_sql("coin_sentiment", engine, if_exists="append", index=False)

        # Log de distribución por moneda (MLOps)
        coin_dist = {}
        for r in coin_records:
            coin_dist[r["coin"]] = coin_dist.get(r["coin"], 0) + 1
        logger.info(f"🪙 Sentimiento per-coin: {coin_dist}")
        logger.info(f"💾 {len(coin_records)} registros guardados en coin_sentiment")


def log_pipeline_metrics(records: list[dict], cycle_start: float):
    """
    MEJORA v3.0 (MLOps): Logging de métricas del pipeline NLP.
    Registra latencia, distribución de sentimiento y estadísticas
    para monitorización y debugging en producción.
    """
    elapsed = time.time() - cycle_start
    if not records:
        return

    scores = [r["sentiment_score"] for r in records]
    avg_score = sum(scores) / len(scores)
    positive_count = sum(1 for r in records if r["label"] == "positive")
    negative_count = sum(1 for r in records if r["label"] == "negative")
    neutral_count = sum(1 for r in records if r["label"] == "neutral")

    logger.info(f"📊 SENTIMIENTO PROMEDIO: {avg_score:+.4f}")
    logger.info(
        f"📈 Distribución: ✅ {positive_count} positivos | "
        f"❌ {negative_count} negativos | ⚪ {neutral_count} neutrales"
    )
    logger.info(f"⏱️ Pipeline completado en {elapsed:.2f}s")


def main():
    """
    Ciclo principal del motor de sentimiento v3.0.
    Mejoras: NER per-coin, MLOps metrics, backoff exponencial.
    """
    logger.info("=" * 60)
    logger.info("🧠 MOTOR DE SENTIMIENTO NLP v3.0 (FinBERT + NER) — TFG")
    logger.info("=" * 60)

    # 1. Cargar modelo FinBERT (primera vez descarga ~400MB)
    logger.info(f"📥 Cargando modelo {MODEL_NAME}...")
    classifier = pipeline("sentiment-analysis", model=MODEL_NAME)
    logger.info("✅ Modelo cargado correctamente")

    # 2. Configurar base de datos (ahora con tabla coin_sentiment)
    engine = setup_database()
    logger.info("✅ Base de datos configurada (market_sentiment + coin_sentiment)")

    # 3. Ciclo de análisis con backoff exponencial en caso de error
    cycle_count = 0
    consecutive_errors = 0
    while True:
        cycle_count += 1
        cycle_start = time.time()
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

            # Guardar en DB (tabla global — retrocompatible)
            save_to_db(engine, records)

            # MEJORA v3.0: Guardar sentimiento per-coin
            save_coin_sentiment(engine, records)

            # MEJORA v3.0: Log de métricas MLOps
            log_pipeline_metrics(records, cycle_start)

            # Reset contador de errores consecutivos
            consecutive_errors = 0

            # Forzar Garbage Collection para evitar fuga de memoria de Pytorch/Transformers
            gc.collect()

            # Esperar 5 minutos
            logger.info("⏳ Esperando 5 minutos para el siguiente ciclo...")
            time.sleep(300)

        except Exception as e:
            consecutive_errors += 1
            # Backoff exponencial: 60s, 120s, 240s... hasta 15min máx
            wait_time = min(60 * (2 ** (consecutive_errors - 1)), 900)
            logger.error(f"❌ Error en ciclo #{cycle_count}: {e}")
            logger.warning(f"⏳ Reintentando en {wait_time}s (error #{consecutive_errors})")
            time.sleep(wait_time)


if __name__ == "__main__":
    # Esperar a que TimescaleDB arranque
    logger.info("⏳ Esperando 15 segundos para que TimescaleDB arranque...")
    time.sleep(15)
    main()
