import pytest
import datetime
from unittest.mock import MagicMock
import sys
import os

# Añade la raíz y los módulos temporales para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock para dependencias pesadas
sys.modules['talib.abstract'] = MagicMock()
sys.modules['freqtrade.strategy'] = MagicMock()
import user_data.strategies.FreqaiExampleStrategy as StrategyModule

class FakeDataframe(MagicMock):
    @property
    def empty(self):
        return False
    def iloc(self):
        pass

def test_half_kelly_stake_amount():
    """
    Test 1: Garantiza que Half-Kelly devuelve un peso de cartera mayor
    ante mayor retorno AI esperado, y que topa en el threshold de 40%.
    """
    strat = StrategyModule.FreqaiExampleStrategy(MagicMock())
    strat.dp = MagicMock()
    
    current_time = datetime.datetime.now()
    
    # Simula un trade con baja convicción (+0.5%)
    low_prediction_df = MagicMock()
    low_prediction_df.empty = False
    low_prediction_df.iloc = [None, {"&s-price_change": 0.005}] 
    
    # Sobrescribimos el behavior por defecto de Pandas loc
    low_prediction_df.iloc = MagicMock()
    low_prediction_df.iloc.__getitem__.return_value = {"&s-price_change": 0.005}
    
    strat.dp.get_analyzed_dataframe.return_value = (low_prediction_df, None)
    
    low_stake = strat.custom_stake_amount("BTC/USDT", current_time, 100.0, 10.0, 5.0, 1000.0, "", "long", wallets=MagicMock(get_total_stake_amount=lambda: 1000.0))
    
    # High predicción (+3%)
    high_prediction_df = MagicMock()
    high_prediction_df.empty = False
    high_prediction_df.iloc.__getitem__.return_value = {"&s-price_change": 0.03}
    strat.dp.get_analyzed_dataframe.return_value = (high_prediction_df, None)
    
    high_stake = strat.custom_stake_amount("BTC/USDT", current_time, 100.0, 10.0, 5.0, 1000.0, "", "long", wallets=MagicMock(get_total_stake_amount=lambda: 1000.0))
    
    # A mayor convicción, mayor stake (Half Kelly rule)
    assert high_stake > low_stake
    # El cap es 40% del wallet (400) + base (5)
    assert high_stake <= 400.0

def test_dynamic_atr_stoploss():
    """
    Test 2: Garantiza que el ATR loss scale protege las caídas.
    """
    strat = StrategyModule.FreqaiExampleStrategy(MagicMock())
    strat.dp = MagicMock()
    
    df_mock = MagicMock()
    df_mock.empty = False
    df_mock.iloc.__getitem__.return_value = {"atr": 50, "close": 1000}
    strat.dp.get_analyzed_dataframe.return_value = (df_mock, None)
    
    # current_profit es 0
    sl = strat.custom_stoploss(pair="BTC/USDT", trade=MagicMock(), current_time=datetime.datetime.now(), current_rate=1000, current_profit=0, after_fill=True)
    
    # Expected sl = - ((50 * 1.5) / 1000) = -0.075
    assert sl == -0.075
