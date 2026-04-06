from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
# ... importaciones anteriores ...

class FreqaiHyperoptStrategy(FreqaiExampleStrategy):
    # En lugar de valores fijos, definimos RANGOS GENÉTICOS
    
    # Rango de Stoploss: Busca entre -5% y -0.5%
    stoploss_range = DecimalParameter(-0.05, -0.005, default=-0.01, space="sell", optimize=True)
    
    # Rango para el ROI (Take Profit)
    roi_table = {
        0: 0.15,  # Valor inicial
        20: 0.04,
        40: 0.02,
        60: 0.01
    }

    # Optimización de Indicadores Técnicos
    buy_sma_period = IntParameter(100, 300, default=200, space="buy", optimize=True)
    buy_ema_period = IntParameter(20, 100, default=50, space="buy", optimize=True)
    
    # Optimización del Umbral de la IA (¿Cuán seguro debe estar el bot?)
    ai_confidence_threshold = DecimalParameter(0.5, 0.9, default=0.55, space="buy", optimize=True)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Usamos self.buy_sma_period.value en lugar de 200 fijo
        dataframe['sma_optimized'] = ta.SMA(dataframe, timeperiod=self.buy_sma_period.value)
        dataframe['ema_optimized'] = ta.EMA(dataframe, timeperiod=self.buy_ema_period.value)
        
        # ... resto del código usando las variables optimizadas ...
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Usamos el umbral genético
        ai_signal_long = (dataframe["do_predict"] == 1) & (dataframe["&s-up_or_down"] > self.ai_confidence_threshold.value)
        
        # ... resto de condiciones ...
        return dataframe