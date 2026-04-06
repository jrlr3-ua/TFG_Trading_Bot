# ==========================================
# TFG: SISTEMA DE TRADING ALGORÍTMICO HÍBRIDO
# Autor: Joan Romà Llorca
# Versión: 1.2 (Production - Config-Driven)
# ==========================================
#
# Arquitectura de decisión multi-capa:
#   1. Machine Learning (FreqAI / LightGBM)
#   2. NLP (Sentimiento de mercado via FinBERT + TimescaleDB)
#   3. Order Flow (Order Book Imbalance)
#   4. Análisis Técnico Macro (SMA/EMA en H1)
#   5. Circuit Breaker (Protección de capital)
#
# NOTA: minimal_roi y stoploss se delegan al config.json
# para permitir su modificación sin tocar el código.
#
# Versiones anteriores disponibles en:
#   → FreqaiExampleStrategy_legacy.py
# ==========================================

import logging
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame
from sqlalchemy import create_engine

from freqtrade.strategy import (
    IStrategy,
    IntParameter,
    DecimalParameter,
    merge_informative_pair
)
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)


class FreqaiExampleStrategy(IStrategy):
    """
    Estrategia TFG: Protocolo Híbrido Avanzado
    -------------------------------------------
    Combina 5 capas de análisis para generar señales de trading:

    - Capa 1 (ML):   LightGBM predice dirección del precio (20 velas)
    - Capa 2 (NLP):  FinBERT filtra por sentimiento de mercado
    - Capa 3 (Flow): Order Book Imbalance detecta presión institucional
    - Capa 4 (TA):   SMA/EMA en H1 filtra tendencia macro
    - Capa 5 (Risk): Circuit Breaker bloquea entradas en drawdown diario
    """

    # ─── CONFIGURACIÓN GENERAL ──────────────────────────────────────────
    INTERFACE_VERSION = 3
    can_short = True
    timeframe = "5m"
    startup_candle_count: int = 200

    # ─── CONEXIÓN A BASE DE DATOS ───────────────────────────────────────
    DB_URL = "postgresql://postgres:password@timescaledb:5432/freqtrade"

    # ─── PARÁMETROS OPTIMIZABLES (Hyperopt) ─────────────────────────────
    # Estos valores fueron optimizados mediante algoritmo genético (Hyperopt)
    # sobre datos de Feb 2026. Ver FreqaiExampleStrategy.json para detalles.
    buy_sma_period = IntParameter(100, 300, default=160, space="buy", optimize=True, load=True)
    buy_ema_period = IntParameter(20, 100, default=79, space="buy", optimize=True, load=True)
    ai_confidence_long = DecimalParameter(0.5, 0.9, default=0.864, space="buy", optimize=True, load=True)
    ai_confidence_short = DecimalParameter(0.1, 0.5, default=0.125, space="buy", optimize=True, load=True)

    # ─── GESTIÓN DE RIESGO ──────────────────────────────────────────────
    # NOTA: minimal_roi y stoploss están COMENTADOS a propósito.
    # Se delegan al config.json para evitar conflictos de precedencia
    # (Freqtrade prioriza .py sobre .json si ambos definen estos valores).
    # minimal_roi = { "0": 0.02, "10": 0.01, "20": 0.005, "40": 0 }
    # stoploss = -0.01

    # Trailing Stop: asegura beneficios a partir de +1%
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.011
    trailing_only_offset_is_reached = True

    # ─── TIMEFRAMES INFORMATIVOS ────────────────────────────────────────
    def informative_pairs(self):
        """Define pares de H1 para el filtro de tendencia macro."""
        pairs = self.dp.current_whitelist()
        return [(pair, '1h') for pair in pairs]

    # ─── CÁLCULO DE INDICADORES ─────────────────────────────────────────
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Pipeline de indicadores (orden crítico):
        1. NLP → crea 'sentiment_score' antes de que FreqAI lo use como feature
        2. FreqAI → genera predicción '&s-up_or_down' y 'do_predict'
        3. Order Flow → calcula imbalance del libro de órdenes
        4. Macro H1 → fusiona SMA/EMA de temporalidad superior
        """
        # 1. CAPA NLP
        dataframe = self._merge_sentiment_data(dataframe)

        # 2. CAPA ML (FreqAI)
        dataframe = self.freqai.start(dataframe, metadata, self)

        # 3. CAPA ORDER FLOW (solo en live/dry-run)
        dataframe['order_book_imbalance'] = 0.5  # Valor neutro por defecto
        if self.dp and self.dp.runmode.value in ('live', 'dry_run'):
            try:
                order_book = self.dp.market(metadata['pair']).fetch_order_book(limit=10)
                bids_vol = sum([bid[1] for bid in order_book['bids']])
                asks_vol = sum([ask[1] for ask in order_book['asks']])
                total_vol = bids_vol + asks_vol
                if total_vol > 0:
                    dataframe.loc[dataframe.index[-1], 'order_book_imbalance'] = bids_vol / total_vol
            except Exception as e:
                logger.debug(f"Error cargando Order Book: {e}")

        # 4. CAPA MACRO H1
        informative_h1 = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        informative_h1['sma_200'] = ta.SMA(informative_h1, timeperiod=self.buy_sma_period.value)
        informative_h1['ema_50'] = ta.EMA(informative_h1, timeperiod=self.buy_ema_period.value)
        informative_h1['dist_ema50'] = abs(
            (informative_h1['close'] - informative_h1['ema_50']) / informative_h1['ema_50']
        )
        dataframe = merge_informative_pair(dataframe, informative_h1, self.timeframe, '1h', ffill=True)

        return dataframe

    def _merge_sentiment_data(self, dataframe: DataFrame) -> DataFrame:
        """
        Fusiona datos de sentimiento NLP desde TimescaleDB.
        Solo se ejecuta en live/dry-run para evitar ralentizar backtests.
        """
        dataframe['sentiment_score'] = 0.0
        if self.dp and self.dp.runmode.value in ('live', 'dry_run'):
            try:
                engine = create_engine(self.DB_URL)
                query = "SELECT time, sentiment_score FROM market_sentiment ORDER BY time DESC LIMIT 500"
                sentiment_df = pd.read_sql(query, engine)
                engine.dispose()
                if not sentiment_df.empty:
                    sentiment_df['time'] = pd.to_datetime(sentiment_df['time']).dt.tz_convert('UTC')
                    dataframe['date'] = pd.to_datetime(dataframe['date']).dt.tz_convert('UTC')
                    merged_df = pd.merge_asof(
                        dataframe.sort_values('date'),
                        sentiment_df.sort_values('time'),
                        left_on='date', right_on='time', direction='backward'
                    )
                    if 'sentiment_score_y' in merged_df.columns:
                        dataframe['sentiment_score'] = merged_df['sentiment_score_y'].fillna(0.0)
            except Exception:
                pass
        return dataframe

    # ─── LÓGICA DE ENTRADA ──────────────────────────────────────────────
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Señales de entrada LONG y SHORT.
        Requiere confluencia de: tendencia macro + zona de valor + IA + sentimiento.
        """
        # Filtros técnicos (H1)
        trend_bullish = (dataframe['close_1h'] > dataframe['sma_200_1h'])
        trend_bearish = (dataframe['close_1h'] < dataframe['sma_200_1h'])
        in_value_zone = (dataframe['dist_ema50_1h'] < 0.015)

        # Señales IA
        ai_signal_long = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] > self.ai_confidence_long.value)
        ai_signal_short = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] < self.ai_confidence_short.value)

        # Filtros NLP
        sentiment_safe_long = (dataframe['sentiment_score'] > -0.2)
        sentiment_safe_short = (dataframe['sentiment_score'] < 0.2)

        # LONG: Tendencia alcista + Zona de valor + IA bullish + Sentimiento no negativo
        dataframe.loc[
            trend_bullish & in_value_zone & ai_signal_long & sentiment_safe_long,
            "enter_long"
        ] = 1

        # SHORT: Tendencia bajista + Zona de valor + IA bearish + Sentimiento no positivo
        dataframe.loc[
            trend_bearish & in_value_zone & ai_signal_short & sentiment_safe_short,
            "enter_short"
        ] = 1

        return dataframe

    # ─── LÓGICA DE SALIDA ───────────────────────────────────────────────
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Salida cuando la IA invierte su predicción con fuerza."""
        dataframe.loc[
            (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] < 0.40),
            "exit_long"
        ] = 1
        dataframe.loc[
            (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] > 0.60),
            "exit_short"
        ] = 1
        return dataframe

    # ─── CIRCUIT BREAKER (Protección de Capital) ────────────────────────
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                            side: str, **kwargs) -> bool:
        """
        Bloquea nuevas entradas si la pérdida acumulada del día supera -10%.
        Desactivado en backtest/hyperopt para evitar errores de DB.
        """
        if self.dp and self.dp.runmode.value in ('backtest', 'hyperopt'):
            return True
        try:
            today = datetime.now(timezone.utc).date()
            trades_today = Trade.get_trades([Trade.close_date >= today]).all()
            daily_profit = sum(t.close_profit for t in trades_today)
            if daily_profit < -0.10:
                logger.warning(f"⚠️ Circuit Breaker activado: pérdida diaria {daily_profit:.2%}")
                return False
        except Exception:
            pass
        return True

    # ─── FREQAI: FEATURE ENGINEERING ────────────────────────────────────
    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int,
                                       metadata: dict, **kwargs) -> DataFrame:
        """Features técnicas expandidas por periodo para FreqAI."""
        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        bb = ta.BBANDS(dataframe, timeperiod=period)
        dataframe["%-bb_width-period"] = (bb["upperband"] - bb["lowerband"]) / bb["middleband"]
        if "sentiment_score" not in dataframe.columns:
            dataframe["sentiment_score"] = 0.0
        dataframe["%-sentiment"] = dataframe["sentiment_score"]
        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """Features básicas no dependientes de periodo."""
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw_volume"] = dataframe["volume"]
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """Features temporales (día de la semana, hora del día)."""
        dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek
        dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Target de la IA: predicción binaria de dirección del precio.
        1 = el precio sube en las próximas N velas, 0 = baja.
        """
        N = self.freqai_info["feature_parameters"]["label_period_candles"]
        dataframe["&s-up_or_down"] = np.where(
            dataframe["close"].shift(-N) > dataframe["close"], 1, 0
        )
        return dataframe