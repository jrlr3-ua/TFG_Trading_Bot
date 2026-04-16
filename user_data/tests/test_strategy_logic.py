import pytest
import pandas as pd
from unittest.mock import MagicMock
from datetime import datetime, timezone

from freqtrade.data.dataprovider import DataProvider
from user_data.strategies.FreqaiExampleStrategy import FreqaiExampleStrategy

@pytest.fixture
def strategy():
    """Fixture que inicializa la estrategia con dependencias simuladas."""
    config = {
        "bot_name": "test_bot",
        "timeframe": "5m",
        "stake_currency": "USDT",
        "stake_amount": "unlimited",
        "max_open_trades": 5
    }
    strat = FreqaiExampleStrategy(config)
    
    # Mocking DataProvider y Wallets
    strat.dp = MagicMock(spec=DataProvider)
    strat.wallets = MagicMock()
    
    # Simulamos que el wallet total es de 1000 USDT siempre
    strat.wallets.get_total_stake_amount.return_value = 1000.0
    return strat

def test_half_kelly_stake_amount(strategy):
    """
    Test del Criterio de Kelly (Half-Kelly ajustado a 40%).
    Debe escalar la posición proporcionalmente a la confianza de la predicción.
    """
    pair = "BTC/USDT:USDT"
    
    # Escenario 1: Confianza IA alta (+1.5% predicción)
    df_high_conf = pd.DataFrame([{
        "close": 50000,
        "&s-price_change": 0.015  # 1.5% predicho (75% riesgo)
    }])
    strategy.dp.get_analyzed_dataframe.return_value = (df_high_conf, None)
    
    # Esperamos: riesgo base (400) * factor(0.75) = 300 aprox
    stake_high = strategy.custom_stake_amount(
        pair, datetime.now(timezone.utc), 50000, 
        proposed_stake=200, min_stake=10, max_stake=400, entry_tag=None, side="long"
    )
    assert stake_high > 200, "High confidence should risk more than default proposed stake."
    assert stake_high <= 400, "Should not exceed max 40% (400 USDT)."

    # Escenario 2: Confianza IA baja (+0.2% predicción)
    df_low_conf = pd.DataFrame([{
        "close": 50000,
        "&s-price_change": 0.002  # 0.2% predicho (10% riesgo)
    }])
    strategy.dp.get_analyzed_dataframe.return_value = (df_low_conf, None)
    
    stake_low = strategy.custom_stake_amount(
        pair, datetime.now(timezone.utc), 50000, 
        proposed_stake=200, min_stake=10, max_stake=400, entry_tag=None, side="long"
    )
    assert stake_low < stake_high, "Lower confidence must yield lower stake amount."

def test_dynamic_atr_stoploss(strategy):
    """
    Test del Stoploss dinámico basado en la Volatilidad (ATR).
    Debe estar capeado al -3% máximo de pérdida.
    """
    pair = "BTC/USDT:USDT"
    
    # Escenario: Volatilidad muy baja (ATR pequeño)
    df_low_vol = pd.DataFrame([{"atr": 50}])  # Precio 50k, ATR 50 (muy poco)
    strategy.dp.get_analyzed_dataframe.return_value = (df_low_vol, None)
    
    stop_baja = strategy.custom_stoploss(
        pair, None, datetime.now(timezone.utc), 
        current_rate=50000, current_profit=0, after_fill=True
    )
    # Stop = -2 * 50 / 50000 = -0.002
    assert -0.01 <= stop_baja <= -0.005, "Low volatility should trigger smaller tight stoploss."

    # Escenario: Volatilidad muy alta (Cisne Negro)
    df_high_vol = pd.DataFrame([{"atr": 3000}])
    strategy.dp.get_analyzed_dataframe.return_value = (df_high_vol, None)
    
    stop_alta = strategy.custom_stoploss(
        pair, None, datetime.now(timezone.utc), 
        current_rate=50000, current_profit=0, after_fill=True
    )
    # Debería dar -0.12, pero está capado al -0.03 (-3.0%)
    assert stop_alta == -0.03, "High volatility must be strictly capped at -3.0% stoploss."
