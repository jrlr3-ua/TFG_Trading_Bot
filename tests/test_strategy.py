"""
TFG: Suite de Tests — Estrategia de Trading (FreqaiExampleStrategy v3.0)
========================================================================
Valida los componentes críticos de la estrategia:
  - Test 1:  Conviction-Based Sizing (Proxy Kelly al 40%)
  - Test 1b: Sizing sin wallets (backtesting)
  - Test 2:  Stop Loss Dinámico basado en ATR (alta volatilidad)
  - Test 2b: Stop Loss ATR (baja volatilidad)

Ejecución: make test
"""
import datetime
from unittest.mock import MagicMock, patch

# Las dependencias pesadas ya están mockeadas por conftest.py
import user_data.strategies.FreqaiExampleStrategy as StrategyModule

# ─── Obtener la clase real de la estrategia ──────────────────────────
StrategyClass = StrategyModule.FreqaiExampleStrategy


def _make_strategy():
    """Helper: crea una instancia mockeada de la estrategia."""
    strat = StrategyClass()
    strat.dp = MagicMock()
    strat.timeframe = "5m"
    strat._db_engine = None
    return strat


def _mock_dataframe(prediction=0.01, atr=50, sar=0):
    """Helper: genera un dataframe mock con valores controlados."""
    df = MagicMock()
    df.empty = False
    row = {"&s-price_change": prediction, "atr": atr, "sar": sar}
    df.iloc.__getitem__ = MagicMock(return_value=row)
    return df


def test_conviction_based_sizing():
    """
    Test 1: Garantiza que el Conviction-Based Sizing devuelve un stake
    mayor ante mayor confianza de la IA, y que nunca supera el 40% del wallet.
    """
    strat = _make_strategy()

    # Simular wallets disponibles (1000 USDT)
    strat.wallets = MagicMock()
    strat.wallets.get_total_stake_amount.return_value = 1000.0

    current_time = datetime.datetime.now()

    # Baja convicción (+0.5%)
    low_df = _mock_dataframe(prediction=0.005, atr=5)
    strat.dp.get_analyzed_dataframe.return_value = (low_df, None)
    low_stake = strat.custom_stake_amount(
        "BTC/USDT", current_time, 100.0, 10.0, 5.0, 1000.0, "", "long"
    )

    # Alta convicción (+3%)
    high_df = _mock_dataframe(prediction=0.03, atr=5)
    strat.dp.get_analyzed_dataframe.return_value = (high_df, None)
    high_stake = strat.custom_stake_amount(
        "BTC/USDT", current_time, 100.0, 10.0, 5.0, 1000.0, "", "long"
    )

    # A mayor convicción, mayor stake
    assert high_stake > low_stake
    # El cap es 40% del wallet (400)
    assert high_stake <= 400.0


def test_conviction_sizing_without_wallets():
    """
    Test 1b: Garantiza que el sizing no crashea cuando self.wallets es None
    (escenario de backtesting).
    """
    strat = _make_strategy()
    strat.wallets = None  # Simular backtesting sin objeto wallets

    df = _mock_dataframe(prediction=0.02, atr=5)
    strat.dp.get_analyzed_dataframe.return_value = (df, None)

    current_time = datetime.datetime.now()
    # No debe lanzar excepción
    stake = strat.custom_stake_amount(
        "BTC/USDT", current_time, 100.0, 10.0, 5.0, 1000.0, "", "long"
    )
    assert stake >= 5.0  # Al menos el min_stake


def test_dynamic_atr_stoploss():
    """
    Test 2: Garantiza que el stop loss ATR se calcula como -(2 * ATR / precio)
    con caps entre -0.5% y -3%.
    ATR=50, precio=1000 → -(2*50/1000) = -0.10 → capped a -0.03
    """
    strat = _make_strategy()

    df = _mock_dataframe(atr=50)
    strat.dp.get_analyzed_dataframe.return_value = (df, None)

    sl = strat.custom_stoploss(
        pair="BTC/USDT",
        trade=MagicMock(is_short=False),
        current_time=datetime.datetime.now(),
        current_rate=1000,
        current_profit=0,
        after_fill=True,
    )
    # -(2*50/1000) = -0.10 → capped a -0.03
    assert sl == -0.03
    # Verificación explícita de que el resultado cae en el intervalo de seguridad
    assert -0.03 <= sl <= -0.005


def test_atr_stoploss_low_volatility():
    """
    Test 2b: Con baja volatilidad, el stop debe ser más ceñido.
    ATR=3, precio=1000 → -(2*3/1000) = -0.006 → within caps [-0.005, -0.03]
    """
    strat = _make_strategy()

    df = _mock_dataframe(atr=3)
    strat.dp.get_analyzed_dataframe.return_value = (df, None)

    sl = strat.custom_stoploss(
        pair="BTC/USDT",
        trade=MagicMock(is_short=False),
        current_time=datetime.datetime.now(),
        current_rate=1000,
        current_profit=0,
        after_fill=True,
    )
    # -(2*3/1000) = -0.006 → within range [-0.005, -0.03]
    assert sl == -0.006
