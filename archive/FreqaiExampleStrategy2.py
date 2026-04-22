# import logging
# from functools import reduce
# import numpy as np
# import pandas as pd
# import talib.abstract as ta
# import pandas_ta as pta
# from pandas import DataFrame
# from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, merge_informative_pair
# from datetime import datetime, timedelta
# from sqlalchemy import create_engine

# class FreqaiExampleStrategy(IStrategy):
#     """
#     Estrategia TFG: Protocolo Alex Ruiz (TradingLab) + Hybrid AI
#     ------------------------------------------------------------
#     1. Trend Following (Estrategia A): Precio > SMA 200 (H1).
#     2. Zona de Valor: Retroceso a EMA 50 (H1).
#     3. Gatillo: Predicción FreqAI + Sentimiento Positivo.
#     4. Gestión: Stop Loss 1%, Break Even a 1R.
#     """
    
#     # --- CONFIGURACIÓN DEL BOT ---
#     INTERFACE_VERSION = 3
#     can_short = True
#     timeframe = "5m"  # Timeframe de ejecución (Gatillo)
    
#     # Periodo de arranque para calcular indicadores H1
#     startup_candle_count: int = 200 

#     # --- GESTIÓN DE RIESGO (Alex Ruiz Rules) ---
#     # Stop Loss fijo del 1% (Regla inquebrantable)
#     stoploss = -0.01 
    
#     # ROI (Take Profit Escalonado simulado)
#     # TP1: 1:1 (1%) -> El trailing stop se encarga de asegurar
#     # TP2: 1:2 (2%)
#     # TP3: Runner
#     minimal_roi = {
#         "0": 0.10,      # Runner: Intentar capturar hasta un 10%
#         "40": 0.02,     # TP2: A los 40 min, conformarse con 2%
#         "20": 0.01,     # TP1: A los 20 min, asegurar 1%
#     }

#     # Trailing Stop (El "Break Even" automático)
#     trailing_stop = True
#     trailing_stop_positive = 0.01  # Cuando gane 1%...
#     trailing_stop_positive_offset = 0.011 # ...activa el trailing justo detrás
#     trailing_only_offset_is_reached = True

#     # --- INFRAESTRUCTURA DE DATOS ---
#     DB_URL = "postgresql://postgres:password@timescaledb:5432/freqtrade"

#     def __init__(self, config: dict) -> None:
#         super().__init__(config)
#         try:
#             self.engine = create_engine(self.DB_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
#         except Exception as e:
#             print(f"⚠️ Error DB: {e}")

#     # --- 1. CONFIGURACIÓN DE TIMEFRAMES (H1 vs M5) ---
#     def informative_pairs(self):
#         # Necesitamos datos de H1 para definir la tendencia (El "Juez")
#         pairs = self.dp.current_whitelist()
#         informative_pairs = [(pair, '1h') for pair in pairs]
        
#         # Añadimos pares adicionales para FreqAI si es necesario
#         informative_pairs += self.freqai.start(self.dataframe, self.metadata, self)
        
#         return informative_pairs

#     # --- 2. CÁLCULO DE INDICADORES ---
#     def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
#         # A) Indicadores en M5 (Gatillo / Estructura Fina)
#         # -----------------------------------------------
#         # FreqAI (Tu modelo LightGBM)
#         dataframe = self.freqai.start(dataframe, metadata, self)
        
#         # Ingesta de Sentimiento (Tu motor NLP)
#         dataframe = self.merge_sentiment_data(dataframe)

#         # B) Indicadores en H1 (Tendencia Fractal)
#         # -----------------------------------------------
#         # Obtenemos los datos de 1 hora
#         informative_h1 = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        
#         # SMA 200 (El Juez de Tendencia)
#         informative_h1['sma_200'] = ta.SMA(informative_h1, timeperiod=200)
        
#         # EMA 50 (La Zona de Valor / Imán)
#         informative_h1['ema_50'] = ta.EMA(informative_h1, timeperiod=50)
        
#         # Calculamos distancia porcentual a la EMA 50 (Para detectar el "Pullback")
#         # Si la distancia es pequeña (< 0.5%), estamos en "Zona de Valor"
#         informative_h1['dist_ema50'] = abs((informative_h1['close'] - informative_h1['ema_50']) / informative_h1['ema_50'])

#         # Fusionamos H1 con M5
#         dataframe = merge_informative_pair(dataframe, informative_h1, self.timeframe, '1h', ffill=True)
#         # Ahora tenemos columnas como: sma_200_1h, ema_50_1h, dist_ema50_1h

#         return dataframe

#     def merge_sentiment_data(self, dataframe: DataFrame) -> DataFrame:
#         """ Fusión robusta de datos de sentimiento (Tu código blindado) """
#         dataframe['sentiment_score'] = 0.0
#         try:
#             query = "SELECT time, sentiment_score FROM market_sentiment ORDER BY time DESC LIMIT 500"
#             sentiment_df = pd.read_sql(query, self.engine)
#             if not sentiment_df.empty:
#                 sentiment_df['time'] = pd.to_datetime(sentiment_df['time']).dt.tz_convert('UTC')
#                 dataframe['date'] = pd.to_datetime(dataframe['date']).dt.tz_convert('UTC')
#                 sentiment_df = sentiment_df.sort_values('time')
#                 merged_df = pd.merge_asof(dataframe, sentiment_df, left_on='date', right_on='time', direction='backward')
#                 if 'sentiment_score_y' in merged_df.columns:
#                     dataframe['sentiment_score'] = merged_df['sentiment_score_y'].fillna(0.0)
#         except Exception:
#             pass
#         return dataframe

#     # --- 3. REGLAS DE ENTRADA (EL ALGORITMO) ---
#     def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
#         # Parche de seguridad
#         if "sentiment_score" not in dataframe.columns: dataframe["sentiment_score"] = 0.0

#         # --- ESTRATEGIA A: TREND FOLLOWING + PULLBACK ---
        
#         # CONDICIÓN 1: Tendencia Alcista en H1 (Precio por encima de SMA 200)
#         trend_bullish = (dataframe['close_1h'] > dataframe['sma_200_1h'])
        
#         # CONDICIÓN 2: Pullback a Zona de Valor (Precio cerca de EMA 50 H1)
#         # Definimos "cerca" como estar a menos de un 1.5% de distancia de la EMA
#         in_value_zone = (dataframe['dist_ema50_1h'] < 0.015) 
        
#         # CONDICIÓN 3: Gatillo FreqAI (La IA predice subida)
#         ai_signal_long = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] > 0.55)
        
#         # CONDICIÓN 4: Filtro de Sentimiento (No operar contra noticias graves)
#         sentiment_safe = (dataframe['sentiment_score'] > -0.2)

#         # ENTRY LONG
#         enter_long_cond = [
#             trend_bullish,
#             in_value_zone,
#             ai_signal_long,
#             sentiment_safe,
#             (dataframe['volume'] > 0)
#         ]
        
#         if enter_long_cond:
#             dataframe.loc[reduce(lambda x, y: x & y, enter_long_cond), "enter_long"] = 1

#         # --- ESTRATEGIA SHORT (Espejo) ---
#         trend_bearish = (dataframe['close_1h'] < dataframe['sma_200_1h'])
#         ai_signal_short = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] < 0.45)
        
#         enter_short_cond = [
#             trend_bearish,
#             in_value_zone,
#             ai_signal_short,
#             (dataframe['sentiment_score'] < 0.2), # Sentimiento no excesivamente positivo
#             (dataframe['volume'] > 0)
#         ]
        
#         if enter_short_cond:
#             dataframe.loc[reduce(lambda x, y: x & y, enter_short_cond), "enter_short"] = 1

#         return dataframe

#     def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#         # Usamos ROI y Stoploss dinámicos, pero podemos añadir salidas por IA
        
#         # Salida si la IA cambia de opinión drásticamente
#         exit_long_cond = [dataframe["do_predict"] == 1, dataframe["&s-up_or_down"] < 0.40]
#         if exit_long_cond: dataframe.loc[reduce(lambda x, y: x & y, exit_long_cond), "exit_long"] = 1

#         exit_short_cond = [dataframe["do_predict"] == 1, dataframe["&s-up_or_down"] > 0.60]
#         if exit_short_cond: dataframe.loc[reduce(lambda x, y: x & y, exit_short_cond), "exit_short"] = 1

#         return dataframe

#     # FreqAI Mandatory Methods (Boilerplate)
#     def feature_engineering_expand_all(self, dataframe: DataFrame, period: int, metadata: dict, **kwargs) -> DataFrame:
#         dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
#         dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)
#         dataframe["%-bb_width-period"] = (ta.BBANDS(dataframe, timeperiod=period)["upperband"] - ta.BBANDS(dataframe, timeperiod=period)["lowerband"]) / ta.BBANDS(dataframe, timeperiod=period)["middleband"]
#         if "sentiment_score" not in dataframe.columns: dataframe["sentiment_score"] = 0.0
#         dataframe["%-sentiment"] = dataframe["sentiment_score"]
#         return dataframe

#     def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
#         dataframe["%-pct-change"] = dataframe["close"].pct_change()
#         dataframe["%-raw_volume"] = dataframe["volume"]
#         return dataframe

#     def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
#         dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek
#         dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
#         return dataframe

#     def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
#         dataframe["&s-up_or_down"] = np.where(dataframe["close"].shift(-self.freqai_info["feature_parameters"]["label_period_candles"]) > dataframe["close"], 1, 0)
#         return dataframe

import logging
from functools import reduce
import numpy as np
import pandas as pd
import talib.abstract as ta
import pandas_ta as pta
from pandas import DataFrame
from freqtrade.strategy import IStrategy, merge_informative_pair
from sqlalchemy import create_engine

class FreqaiExampleStrategy(IStrategy):
    """
    Estrategia TFG: Protocolo Alex Ruiz (TradingLab) + Hybrid AI
    CORREGIDA: Eliminado error de dataframe en informative_pairs
    """
    
    # --- CONFIGURACIÓN DEL BOT ---
    INTERFACE_VERSION = 3
    can_short = True
    timeframe = "5m" 
    
    # Periodo de arranque
    startup_candle_count: int = 200 

    # --- GESTIÓN DE RIESGO ---
    stoploss = -0.01 
    
    minimal_roi = {
        "0": 0.10,      
        "40": 0.02,     
        "20": 0.01,     
    }

    trailing_stop = True
    trailing_stop_positive = 0.01  
    trailing_stop_positive_offset = 0.011 
    trailing_only_offset_is_reached = True

    # --- DB ---
    DB_URL = "postgresql://postgres:password@timescaledb:5432/freqtrade"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        try:
            self.engine = create_engine(self.DB_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
        except Exception as e:
            print(f"⚠️ Error DB: {e}")

    # --- 1. CONFIGURACIÓN DE TIMEFRAMES ---
    def informative_pairs(self):
        # CORRECCIÓN: Solo definimos los pares de 1H para la lógica de Alex Ruiz
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, '1h') for pair in pairs]
        return informative_pairs

    # --- 2. CÁLCULO DE INDICADORES ---
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        # A) FreqAI y Sentimiento (M5)
        dataframe = self.freqai.start(dataframe, metadata, self)
        dataframe = self.merge_sentiment_data(dataframe)

        # B) Indicadores en H1 (Tendencia)
        informative_h1 = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        
        # SMA 200 y EMA 50
        informative_h1['sma_200'] = ta.SMA(informative_h1, timeperiod=200)
        informative_h1['ema_50'] = ta.EMA(informative_h1, timeperiod=50)
        informative_h1['dist_ema50'] = abs((informative_h1['close'] - informative_h1['ema_50']) / informative_h1['ema_50'])

        # Fusionamos
        dataframe = merge_informative_pair(dataframe, informative_h1, self.timeframe, '1h', ffill=True)

        return dataframe

    def merge_sentiment_data(self, dataframe: DataFrame) -> DataFrame:
        dataframe['sentiment_score'] = 0.0
        try:
            query = "SELECT time, sentiment_score FROM market_sentiment ORDER BY time DESC LIMIT 500"
            sentiment_df = pd.read_sql(query, self.engine)
            if not sentiment_df.empty:
                sentiment_df['time'] = pd.to_datetime(sentiment_df['time']).dt.tz_convert('UTC')
                dataframe['date'] = pd.to_datetime(dataframe['date']).dt.tz_convert('UTC')
                sentiment_df = sentiment_df.sort_values('time')
                merged_df = pd.merge_asof(dataframe, sentiment_df, left_on='date', right_on='time', direction='backward')
                if 'sentiment_score_y' in merged_df.columns:
                    dataframe['sentiment_score'] = merged_df['sentiment_score_y'].fillna(0.0)
        except Exception:
            pass
        return dataframe

    # --- 3. REGLAS DE ENTRADA ---
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        if "sentiment_score" not in dataframe.columns: dataframe["sentiment_score"] = 0.0

        # Condiciones
        trend_bullish = (dataframe['close_1h'] > dataframe['sma_200_1h'])
        in_value_zone = (dataframe['dist_ema50_1h'] < 0.015) 
        ai_signal_long = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] > 0.55)
        sentiment_safe = (dataframe['sentiment_score'] > -0.2)

        enter_long_cond = [
            trend_bullish,
            in_value_zone,
            ai_signal_long,
            sentiment_safe,
            (dataframe['volume'] > 0)
        ]
        
        if enter_long_cond:
            dataframe.loc[reduce(lambda x, y: x & y, enter_long_cond), "enter_long"] = 1

        # Short
        trend_bearish = (dataframe['close_1h'] < dataframe['sma_200_1h'])
        ai_signal_short = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] < 0.45)
        
        enter_short_cond = [
            trend_bearish,
            in_value_zone,
            ai_signal_short,
            (dataframe['sentiment_score'] < 0.2), 
            (dataframe['volume'] > 0)
        ]
        
        if enter_short_cond:
            dataframe.loc[reduce(lambda x, y: x & y, enter_short_cond), "enter_short"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        exit_long_cond = [dataframe["do_predict"] == 1, dataframe["&s-up_or_down"] < 0.40]
        if exit_long_cond: dataframe.loc[reduce(lambda x, y: x & y, exit_long_cond), "exit_long"] = 1

        exit_short_cond = [dataframe["do_predict"] == 1, dataframe["&s-up_or_down"] > 0.60]
        if exit_short_cond: dataframe.loc[reduce(lambda x, y: x & y, exit_short_cond), "exit_short"] = 1

        return dataframe

    # FreqAI Mandatory Methods
    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int, metadata: dict, **kwargs) -> DataFrame:
        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)
        dataframe["%-bb_width-period"] = (ta.BBANDS(dataframe, timeperiod=period)["upperband"] - ta.BBANDS(dataframe, timeperiod=period)["lowerband"]) / ta.BBANDS(dataframe, timeperiod=period)["middleband"]
        if "sentiment_score" not in dataframe.columns: dataframe["sentiment_score"] = 0.0
        dataframe["%-sentiment"] = dataframe["sentiment_score"]
        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw_volume"] = dataframe["volume"]
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek
        dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        dataframe["&s-up_or_down"] = np.where(dataframe["close"].shift(-self.freqai_info["feature_parameters"]["label_period_candles"]) > dataframe["close"], 1, 0)
        return dataframe
    
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float, max_stake: float,
                            entry_tag: Optional[str], side: str, **kwargs) -> float:
        
        # 1. Obtenemos la última predicción de la IA para este par
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1]
        
        # Probabilidad de éxito según LightGBM (0.0 a 1.0)
        ai_confidence = last_candle.get("&s-up_or_down", 0.5)

        # 2. Fórmula de Ajuste de Riesgo (Variante conservadora de Kelly)
        # Si confianza es 0.5 (50%), factor es 0.
        # Si confianza es 0.8 (80%), factor es alto.
        risk_factor = (ai_confidence - 0.5) * 2  # Escala de 0 a 1
        
        # Nunca arriesgar más del 5% del capital total en una sola operación
        total_wallet = self.wallets.get_total_stake_amount()
        max_risk_per_trade = total_wallet * 0.05
        
        # Stake ajustado
        adjusted_stake = max_risk_per_trade * risk_factor

        # Límites de seguridad
        if adjusted_stake < min_stake: return min_stake
        if adjusted_stake > max_stake: return max_stake
        
        return adjusted_stake
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                            side: str, **kwargs) -> bool:
        
        # 1. Calcular Profit/Loss del día
        today = datetime.now(timezone.utc).date()
        trades_today = Trade.get_trades([Trade.close_date >= today]).all()
        
        daily_profit = sum(t.close_profit for t in trades_today)
        
        # 2. Regla del Circuit Breaker (-3% diario)
        MAX_DAILY_DRAWDOWN = -0.03 
        
        if daily_profit < MAX_DAILY_DRAWDOWN:
            print(f"🚨 ALERTA: Pérdida diaria máxima alcanzada ({daily_profit:.2%}). Bloqueando entradas.")
            return False  # Cancela la operación
            
        return True # Permite la operación