"""
Tests unitarios para componentes críticos de la estrategia híbrida (FreqaiExampleStrategy).
Se utiliza pytest y MagicMock para aislar la lógica del bot y simular dependencias.
"""
import pytest
from datetime import datetime, timezone
import pandas as pd
from unittest.mock import MagicMock, patch

from freqtrade.persistence import Trade
from user_data.strategies.FreqaiExampleStrategy import FreqaiExampleStrategy

@pytest.fixture
def strategy():
    """
    Fixture que inicializa la estrategia con dependencias simuladas.
    Compatible con el estilo conftest.py descrito en la memoria.
    """
    strategy = FreqaiExampleStrategy(config={})
    strategy.dp = MagicMock()
    # Forzar modo dry_run para que confirm_trade_entry ejecute la lógica completa
    # (en backtest retorna True inmediatamente por diseño)
    strategy.dp.runmode.value = 'dry_run'
    return strategy

@patch('user_data.strategies.FreqaiExampleStrategy.Trade')
def test_circuit_breaker_activates(mock_trade, strategy):
    """
    Valida el comportamiento del Circuit Breaker ante pérdidas extremas.
    Es crítico porque previene la ruina de la cuenta en días de crash absoluto.
    Simula una pérdida diaria del -11% y verifica que bloquea la entrada (False).
    """
    # Simular operaciones perdedoras que sumen -0.11 en el día
    trade1 = MagicMock()
    trade1.close_profit = -0.11
    
    mock_query = MagicMock()
    mock_query.all.return_value = [trade1]
    mock_trade.get_trades.return_value = mock_query

    result = strategy.confirm_trade_entry(
        pair="BTC/USDT", order_type="limit", amount=1.0, rate=50000.0,
        time_in_force="gtc", current_time=datetime.now(timezone.utc),
        entry_tag=None, side="long"
    )
    
    assert result is False

@patch('user_data.strategies.FreqaiExampleStrategy.Trade')
@patch('user_data.strategies.FreqaiExampleStrategy.pd.read_sql')
def test_circuit_breaker_allows_below_threshold(mock_read_sql, mock_trade, strategy):
    """
    Valida que el Circuit Breaker permite operar si la pérdida no llega al umbral límite.
    Es crítico para evitar falsos positivos que detengan la operativa sin motivo técnico.
    Simula una pérdida del -9% y verifica que permite la entrada (True).
    """
    trade1 = MagicMock()
    trade1.close_profit = -0.09
    
    mock_query = MagicMock()
    mock_query.all.return_value = [trade1]
    mock_trade.get_trades.return_value = mock_query

    # Simular DataFrame vacío para la consulta on-chain (Fear & Greed)
    mock_read_sql.return_value = pd.DataFrame()
    strategy._get_db_engine = MagicMock()

    result = strategy.confirm_trade_entry(
        pair="BTC/USDT", order_type="limit", amount=1.0, rate=50000.0,
        time_in_force="gtc", current_time=datetime.now(timezone.utc),
        entry_tag=None, side="long"
    )
    
    assert result is True

@patch('user_data.strategies.FreqaiExampleStrategy.Trade')
@patch('user_data.strategies.FreqaiExampleStrategy.pd.read_sql')
def test_fear_greed_blocks_long_at_85(mock_read_sql, mock_trade, strategy):
    """
    Valida el filtro on-chain de sentimiento extremo.
    Es crítico para evitar entrar en posiciones LONG en picos de euforia (Extreme Greed).
    Simula Fear & Greed = 86 y verifica el bloqueo (False).
    """
    mock_query = MagicMock()
    mock_query.all.return_value = [] # Sin pérdidas previas
    mock_trade.get_trades.return_value = mock_query

    # Simular respuesta de base de datos con Fear & Greed = 86
    mock_read_sql.return_value = pd.DataFrame([{'metric_value': 86}])
    strategy._get_db_engine = MagicMock()

    result = strategy.confirm_trade_entry(
        pair="BTC/USDT", order_type="limit", amount=1.0, rate=50000.0,
        time_in_force="gtc", current_time=datetime.now(timezone.utc),
        entry_tag=None, side="long"
    )
    
    assert result is False

@patch('user_data.strategies.FreqaiExampleStrategy.Trade')
@patch('user_data.strategies.FreqaiExampleStrategy.pd.read_sql')
def test_fear_greed_blocks_short_at_15(mock_read_sql, mock_trade, strategy):
    """
    Valida el filtro on-chain de sentimiento extremo bajista.
    Es crítico para evitar vender en corto durante pánico máximo (Extreme Fear).
    Simula Fear & Greed = 14 y verifica el bloqueo de posiciones SHORT (False).
    """
    mock_query = MagicMock()
    mock_query.all.return_value = []
    mock_trade.get_trades.return_value = mock_query

    # Simular respuesta de base de datos con Fear & Greed = 14
    mock_read_sql.return_value = pd.DataFrame([{'metric_value': 14}])
    strategy._get_db_engine = MagicMock()

    result = strategy.confirm_trade_entry(
        pair="BTC/USDT", order_type="limit", amount=1.0, rate=50000.0,
        time_in_force="gtc", current_time=datetime.now(timezone.utc),
        entry_tag=None, side="short"
    )
    
    assert result is False

def test_stoploss_phase2_sar_transition(strategy):
    """
    Valida la transición del stop loss dinámico a la Fase 2 (Trailing Institucional).
    Es crítico para asegurar ganancias ("lock-in") una vez superado el umbral del 2%.
    Simula current_profit = 0.025 y verifica el ajuste basado matemáticamente en el SAR.
    """
    # Preparar dataframe simulado con un indicador Parabolic SAR válido
    df = pd.DataFrame({
        'close': [50000.0],
        'atr': [500.0],
        'sar': [49000.0]  # SAR por debajo del precio actual (típico en tendencia alcista)
    })
    strategy.dp.get_analyzed_dataframe.return_value = (df, None)
    
    mock_trade = MagicMock()
    mock_trade.is_short = False

    # Para LONG: sar_dist = (sar - current_rate) / current_rate 
    # sar_dist = (49000 - 50000) / 50000 = -0.02 (-2.0%)
    # Aplicando clamp: max(min(-0.02, -0.005), -0.05) => -0.02
    result = strategy.custom_stoploss(
        pair="BTC/USDT", trade=mock_trade, current_time=datetime.now(timezone.utc),
        current_rate=50000.0, current_profit=0.025
    )
    
    assert result == -0.02
