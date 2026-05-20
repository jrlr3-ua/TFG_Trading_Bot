"""
TFG: Motor de Datos On-Chain v3.0
==================================
Microservicio que descarga métricas on-chain y macroeconómicas
desde APIs públicas gratuitas y las almacena en TimescaleDB
para consumo del bot de trading.

Métricas monitorizadas:
1. Fear & Greed Index (alternative.me) — Sentimiento del mercado basado en
   múltiples fuentes (volatilidad, momentum, social media, encuestas)
2. BTC Dominance (CoinGecko) — % del mercado que representa Bitcoin
3. Total Market Cap (CoinGecko) — Capitalización total del mercado crypto
4. DXY Proxy (via Gold/USD) — Correlación inversa con crypto

Ciclo: cada 15 minutos (APIs públicas tienen rate limits estrictos).
"""

import os
import time
import logging
from datetime import datetime, timezone

import requests
import pandas as pd
from sqlalchemy import create_engine, text

# ─── CONFIGURACIÓN ──────────────────────────────────────────────────────
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
DB_NAME = os.environ.get("POSTGRES_DB", "freqtrade")
DB_URL = f"postgresql://postgres:{DB_PASSWORD}@timescaledb:5432/{DB_NAME}"

# APIs Públicas Gratuitas (sin key)
FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"
COINGECKO_GLOBAL_URL = "https://api.coingecko.com/api/v3/global"
DEFILLAMA_TVL_URL = "https://api.llama.fi/charts"

# ─── LOGGING ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def setup_database():
    """
    Crea las tablas para almacenar datos on-chain y macroeconómicos.
    """
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS onchain_metrics (
                time TIMESTAMPTZ NOT NULL,
                metric_name VARCHAR(50) NOT NULL,
                metric_value FLOAT,
                metadata_json TEXT
            );
        """))
        try:
            conn.execute(text(
                "SELECT create_hypertable('onchain_metrics', 'time', if_not_exists => TRUE);"
            ))
        except Exception as e:
            logger.debug(f"Hypertable onchain_metrics ya existe: {e}")
        conn.commit()
    return engine


def fetch_fear_greed_index() -> dict | None:
    """
    Descarga el Fear & Greed Index desde alternative.me.
    Retorna: {'value': int (0-100), 'classification': str}
    
    Interpretación:
    - 0-25: Extreme Fear (pánico → históricamente buena compra)
    - 25-50: Fear (mercado cauteloso)
    - 50-75: Greed (codicia → mercado caliente)
    - 75-100: Extreme Greed (euforia → posible techo)
    """
    try:
        response = requests.get(FEAR_GREED_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("data"):
            item = data["data"][0]
            return {
                "value": int(item["value"]),
                "classification": item.get("value_classification", "unknown")
            }
    except Exception as e:
        logger.error(f"❌ Error obteniendo Fear & Greed Index: {e}")
    return None


def fetch_market_globals() -> dict | None:
    """
    Descarga métricas globales del mercado crypto desde CoinGecko.
    Retorna: {
        'btc_dominance': float,
        'total_market_cap_usd': float,
        'total_volume_24h': float,
        'active_cryptocurrencies': int
    }
    """
    try:
        response = requests.get(COINGECKO_GLOBAL_URL, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {})
        return {
            "btc_dominance": round(data.get("market_cap_percentage", {}).get("btc", 0), 2),
            "total_market_cap_usd": data.get("total_market_cap", {}).get("usd", 0),
            "total_volume_24h": data.get("total_volume", {}).get("usd", 0),
            "active_cryptocurrencies": data.get("active_cryptocurrencies", 0),
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de CoinGecko: {e}")
    return None


def fetch_defillama_tvl() -> float | None:
    """
    Descarga el Total Value Locked (TVL) global desde DeFiLlama.
    Permite al bot evaluar la entrada o salida de capital real de los ecosistemas (Liquidity flows).
    """
    try:
        response = requests.get(DEFILLAMA_TVL_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            # data is a list of dicts: [{'date': str, 'totalLiquidityUSD': float}, ...]
            latest = data[-1]
            return float(latest.get("totalLiquidityUSD", 0))
    except Exception as e:
        logger.error(f"❌ Error obteniendo TVL de DeFiLlama: {e}")
    return None


def save_metric(engine, metric_name: str, metric_value: float, metadata: str = ""):
    """Guarda una métrica on-chain en TimescaleDB."""
    record = {
        "time": datetime.now(timezone.utc),
        "metric_name": metric_name,
        "metric_value": metric_value,
        "metadata_json": metadata,
    }
    df = pd.DataFrame([record])
    df.to_sql("onchain_metrics", engine, if_exists="append", index=False)


def main():
    """Ciclo principal del motor de datos on-chain."""
    logger.info("=" * 60)
    logger.info("🔗 MOTOR ON-CHAIN & MACRO v3.0 — TFG")
    logger.info("=" * 60)

    engine = setup_database()
    logger.info("✅ Base de datos configurada (onchain_metrics)")

    cycle_count = 0
    while True:
        cycle_count += 1
        try:
            logger.info(f"─── Ciclo #{cycle_count} ───")

            # 1. Fear & Greed Index
            fng = fetch_fear_greed_index()
            if fng:
                save_metric(engine, "fear_greed_index", fng["value"],
                            f'{{"classification": "{fng["classification"]}"}}')
                logger.info(f"😱 Fear & Greed: {fng['value']}/100 ({fng['classification']})")

            # 2. Bitcoin Dominance
            market = fetch_market_globals()
            if market:
                save_metric(engine, "btc_dominance", market["btc_dominance"])
                save_metric(engine, "total_market_cap_usd", market["total_market_cap_usd"])
                save_metric(engine, "total_volume_24h", market["total_volume_24h"])
                logger.info(f"📊 BTC Dominance: {market['btc_dominance']}%")
                logger.info(f"💰 Market Cap Total: ${market['total_market_cap_usd']:,.0f}")

            # 3. DeFiLlama Global TVL
            tvl = fetch_defillama_tvl()
            if tvl:
                save_metric(engine, "defillama_global_tvl", tvl)
                logger.info(f"🏦 Global DeFi TVL: ${tvl:,.0f}")

            # Esperar 15 minutos (APIs públicas tienen rate limits)
            logger.info("⏳ Esperando 15 minutos para el siguiente ciclo...")
            time.sleep(900)

        except Exception as e:
            logger.error(f"❌ Error en ciclo on-chain: {e}")
            time.sleep(120)


if __name__ == "__main__":
    logger.info("⏳ Esperando 30 segundos para que TimescaleDB arranque...")
    time.sleep(30)
    main()
