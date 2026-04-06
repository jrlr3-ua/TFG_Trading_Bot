# ==========================================
# TFG: SISTEMA DE TRADING ALGORÍTMICO HÍBRIDO
# Autor: Joan Romà Llorca
# Versión: 2.0 (Matrícula de Honor)
# ==========================================
#
# Arquitectura de decisión multi-capa:
#   1. Machine Learning (FreqAI / LightGBM) — 12 features avanzadas
#   2. NLP (Sentimiento de mercado via FinBERT + TimescaleDB)
#   3. Order Flow (Order Book Imbalance)
#   4. Análisis Técnico Macro (SMA/EMA en H1)
#   5. Gestión de Riesgo Dinámica (ATR + Circuit Breaker)
#
# CAMBIOS v2.0 vs v1.2:
#   - Feature Engineering ampliado: 5 features → 12 features
#   - Target de regresión (% cambio) en vez de binario
#   - Stop Loss dinámico basado en ATR
#   - Umbrales de entrada adaptados al nuevo target
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
    Estrategia TFG v2.0: Protocolo Híbrido Avanzado
    ================================================
    Combina 5 capas de análisis para generar señales de trading:

    - Capa 1 (ML):   LightGBM con 12 features predice % de cambio del precio
    - Capa 2 (NLP):  FinBERT filtra por sentimiento de mercado
    - Capa 3 (Flow): Order Book Imbalance detecta presión institucional
    - Capa 4 (TA):   SMA/EMA en H1 filtra tendencia macro
    - Capa 5 (Risk): Stop loss dinámico ATR + Circuit Breaker diario
    """

    # ─── CONFIGURACIÓN GENERAL ──────────────────────────────────────────
    INTERFACE_VERSION = 3
    can_short = True
    timeframe = "5m"
    startup_candle_count: int = 200

    # ─── CONEXIÓN A BASE DE DATOS ───────────────────────────────────────
    DB_URL = "postgresql://postgres:password@timescaledb:5432/freqtrade"

    # ─── PARÁMETROS OPTIMIZABLES (Hyperopt) ─────────────────────────────
    # Indicadores técnicos macro (H1)
    buy_sma_period = IntParameter(100, 300, default=160, space="buy", optimize=True, load=True)
    buy_ema_period = IntParameter(20, 100, default=79, space="buy", optimize=True, load=True)

    # Umbrales de confianza IA (adaptados al target de regresión)
    # Ahora la IA predice % de cambio, así que los umbrales representan
    # el % mínimo de movimiento predicho para entrar en una operación.
    ai_threshold_long = DecimalParameter(0.001, 0.02, default=0.005, space="buy", optimize=True, load=True)
    ai_threshold_short = DecimalParameter(-0.02, -0.001, default=-0.005, space="buy", optimize=True, load=True)

    # ─── GESTIÓN DE RIESGO ──────────────────────────────────────────────
    # minimal_roi y stoploss se delegan al config.json
    # para evitar conflictos de precedencia con Freqtrade.
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

    # ═══════════════════════════════════════════════════════════════════
    # CÁLCULO DE INDICADORES (Pipeline de datos)
    # ═══════════════════════════════════════════════════════════════════
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Pipeline de indicadores (orden crítico):
        1. NLP → crea 'sentiment_score' antes de que FreqAI lo use como feature
        2. FreqAI → genera predicción '&s-price_change' y 'do_predict'
        3. Order Flow → calcula imbalance del libro de órdenes
        4. Macro H1 → fusiona SMA/EMA de temporalidad superior
        5. ATR → calcula volatilidad para stop loss dinámico
        """
        # 1. CAPA NLP
        dataframe = self._merge_sentiment_data(dataframe)

        # 2. CAPA ML (FreqAI)
        dataframe = self.freqai.start(dataframe, metadata, self)

        # 3. CAPA ORDER FLOW (solo en live/dry-run)
        dataframe['order_book_imbalance'] = 0.5
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

        # 5. ATR para stop loss dinámico (cálculo local, no feature de FreqAI)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

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

    # ═══════════════════════════════════════════════════════════════════
    # LÓGICA DE ENTRADA
    # ═══════════════════════════════════════════════════════════════════
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Señales de entrada LONG y SHORT.
        Requiere confluencia de: tendencia macro + IA + sentimiento.

        v2.0: La IA ahora predice el % de cambio del precio, no un binario.
        Entramos solo cuando la predicción supera un umbral mínimo de movimiento.
        """
        # Filtros técnicos (H1)
        trend_bullish = (dataframe['close_1h'] > dataframe['sma_200_1h'])
        trend_bearish = (dataframe['close_1h'] < dataframe['sma_200_1h'])
        in_value_zone = (dataframe['dist_ema50_1h'] < 0.015)

        # Señales IA (v2.0: target de regresión)
        # La IA predice el % de cambio → entramos cuando predice movimiento suficiente
        ai_signal_long = (
            (dataframe["do_predict"] == 1) &
            (dataframe["&s-price_change"] > self.ai_threshold_long.value)
        )
        ai_signal_short = (
            (dataframe["do_predict"] == 1) &
            (dataframe["&s-price_change"] < self.ai_threshold_short.value)
        )

        # Filtros NLP
        sentiment_safe_long = (dataframe['sentiment_score'] > -0.2)
        sentiment_safe_short = (dataframe['sentiment_score'] < 0.2)

        # LONG: Tendencia alcista + Zona de valor + IA predice subida + Sentimiento OK
        dataframe.loc[
            trend_bullish & in_value_zone & ai_signal_long & sentiment_safe_long,
            "enter_long"
        ] = 1

        # SHORT: Tendencia bajista + Zona de valor + IA predice bajada + Sentimiento OK
        dataframe.loc[
            trend_bearish & in_value_zone & ai_signal_short & sentiment_safe_short,
            "enter_short"
        ] = 1

        return dataframe

    # ═══════════════════════════════════════════════════════════════════
    # LÓGICA DE SALIDA
    # ═══════════════════════════════════════════════════════════════════
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Salida cuando la IA invierte su predicción.
        v2.0: Usa el signo del % predicho en vez de umbrales fijos.
        """
        # Salir de LONG si la IA predice caída
        dataframe.loc[
            (dataframe["do_predict"] == 1) & (dataframe["&s-price_change"] < -0.002),
            "exit_long"
        ] = 1
        # Salir de SHORT si la IA predice subida
        dataframe.loc[
            (dataframe["do_predict"] == 1) & (dataframe["&s-price_change"] > 0.002),
            "exit_short"
        ] = 1
        return dataframe

    # ═══════════════════════════════════════════════════════════════════
    # STOP LOSS DINÁMICO (basado en ATR)
    # ═══════════════════════════════════════════════════════════════════
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, after_fill: bool,
                        **kwargs) -> float:
        """
        Stop loss dinámico basado en el ATR (Average True Range).

        En vez de un stop fijo del -1%, el stop se adapta a la volatilidad:
        - Mercado volátil → stop más amplio (evita que nos saquen por ruido)
        - Mercado tranquilo → stop más estrecho (protege más el capital)

        Fórmula: stop = -2 * ATR / precio_entrada
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return -0.01  # Fallback al stop fijo

        last_candle = dataframe.iloc[-1]
        atr = last_candle.get('atr', 0)

        if atr > 0 and current_rate > 0:
            # Stop a 2x ATR del precio actual
            atr_stop = -(2 * atr / current_rate)
            # Limitar entre -0.5% y -3% para mantener el control
            return max(min(atr_stop, -0.005), -0.03)

        return -0.01  # Fallback

    # ═══════════════════════════════════════════════════════════════════
    # CIRCUIT BREAKER (Protección de Capital)
    # ═══════════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════════
    # FREQAI: INGENIERÍA DE CARACTERÍSTICAS (12 Features)
    # ═══════════════════════════════════════════════════════════════════
    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int,
                                       metadata: dict, **kwargs) -> DataFrame:
        """
        Features técnicas expandidas por periodo para FreqAI.
        v2.0: Ampliado de 5 a 12 features por conjunto de indicadores.

        Categorías:
        - Momentum: RSI, Stochastic RSI, MFI, MACD
        - Volatilidad: BB Width, ATR normalizado
        - Volumen: OBV normalizado
        - Fundamental: Sentimiento NLP
        """
        # --- MOMENTUM ---
        # RSI: Índice de Fuerza Relativa (sobrecompra/venta)
        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)

        # Stochastic RSI: RSI del RSI (más sensible a cambios)
        rsi = ta.RSI(dataframe, timeperiod=period)
        rsi_min = rsi.rolling(window=period).min()
        rsi_max = rsi.rolling(window=period).max()
        dataframe["%-stoch_rsi-period"] = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)

        # MFI: Money Flow Index (RSI ponderado por volumen)
        dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)

        # MACD: Histograma (diferencia entre señal y MACD)
        macd = ta.MACD(dataframe, fastperiod=period, slowperiod=period * 2, signalperiod=9)
        dataframe["%-macd_hist-period"] = macd["macdhist"]

        # --- VOLATILIDAD ---
        # Bollinger Bands Width (amplitud normalizada)
        bb = ta.BBANDS(dataframe, timeperiod=period)
        dataframe["%-bb_width-period"] = (bb["upperband"] - bb["lowerband"]) / bb["middleband"]

        # ATR normalizado (volatilidad relativa al precio)
        dataframe["%-atr_norm-period"] = ta.ATR(dataframe, timeperiod=period) / dataframe["close"]

        # --- VOLUMEN ---
        # OBV normalizado (presión compradora/vendedora acumulada)
        obv = ta.OBV(dataframe)
        obv_sma = obv.rolling(window=period).mean()
        dataframe["%-obv_norm-period"] = (obv - obv_sma) / (obv_sma.abs() + 1e-10)

        # --- ESTADÍSTICO ---
        # Retornos logarítmicos (mejor distribución para ML)
        dataframe["%-log_return-period"] = np.log(dataframe["close"] / dataframe["close"].shift(period))

        # Volatilidad de retornos (régimen de mercado)
        dataframe["%-return_std-period"] = dataframe["close"].pct_change().rolling(window=period).std()

        # --- FUNDAMENTAL ---
        # Sentimiento NLP (FinBERT)
        if "sentiment_score" not in dataframe.columns:
            dataframe["sentiment_score"] = 0.0
        dataframe["%-sentiment"] = dataframe["sentiment_score"]

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """Features básicas no dependientes de periodo."""
        # Cambio porcentual (feature clave para la IA)
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        # Volumen bruto
        dataframe["%-raw_volume"] = dataframe["volume"]
        # Ratio close/open (indica dirección de la vela)
        dataframe["%-candle_direction"] = (dataframe["close"] - dataframe["open"]) / dataframe["open"]
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """Features temporales (patrones cíclicos del mercado)."""
        dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek
        dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Target v2.0: Regresión del % de cambio del precio.

        En vez de predecir binario (sube/baja), ahora predecimos CUÁNTO
        se mueve el precio en las próximas N velas. Esto permite:
        - Distinguir entre movimientos pequeños y grandes
        - Ajustar el tamaño de posición según la magnitud predicha
        - Generar métricas de error más ricas (MAE, RMSE)
        """
        N = self.freqai_info["feature_parameters"]["label_period_candles"]
        dataframe["&s-price_change"] = (
            dataframe["close"].shift(-N) - dataframe["close"]
        ) / dataframe["close"]
        return dataframe