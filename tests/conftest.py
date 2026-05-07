"""
TFG: Configuración compartida para la suite de tests (Pytest).
================================================================
Pre-mock de dependencias pesadas (numpy, pandas, talib, freqtrade, etc.)
para que los tests se puedan ejecutar localmente sin instalar todo el stack.

Ejecución: export PYTHONPATH=./ && pytest tests/ -v
"""
import sys
import os
import math
from unittest.mock import MagicMock

# ─── Pre-mock de TODAS las dependencias pesadas ───────────────────────

# 1. Crear un mock de freqtrade.strategy que provea clases base REALES
#    para que FreqaiExampleStrategy pueda heredar de IStrategy correctamente.

class _FakeIStrategy:
    """Stub mínimo de IStrategy para que la herencia funcione en tests."""
    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "5m"
    startup_candle_count = 200
    trailing_stop = False
    trailing_stop_positive = 0
    trailing_stop_positive_offset = 0
    trailing_only_offset_is_reached = False

    def __init__(self, *args, **kwargs):
        pass

class _FakeIntParameter:
    def __init__(self, low=0, high=100, default=50, space="buy", optimize=True, load=True):
        self.value = default

class _FakeDecimalParameter:
    def __init__(self, low=0.0, high=1.0, default=0.5, space="buy", optimize=True, load=True):
        self.value = default

# Build the freqtrade.strategy mock module
_strategy_module = MagicMock()
_strategy_module.IStrategy = _FakeIStrategy
_strategy_module.IntParameter = _FakeIntParameter
_strategy_module.DecimalParameter = _FakeDecimalParameter
_strategy_module.merge_informative_pair = MagicMock(side_effect=lambda df, *a, **kw: df)

# Build the freqtrade.persistence mock module
_persistence_module = MagicMock()
_persistence_module.Trade = MagicMock()

# Register freqtrade mocks BEFORE any import
sys.modules['freqtrade'] = MagicMock()
sys.modules['freqtrade.strategy'] = _strategy_module
sys.modules['freqtrade.persistence'] = _persistence_module

# 2. Mock otras dependencias pesadas
_heavy_modules = [
    'numpy', 'pandas', 'talib', 'talib.abstract',
    'sqlalchemy', 'sqlalchemy.engine',
    'transformers', 'feedparser', 'psycopg2',
]
for mod in _heavy_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# 3. Configurar numpy mock con funciones matemáticas reales
np_mock = sys.modules['numpy']
np_mock.log = math.log
np_mock.sin = math.sin
np_mock.cos = math.cos
np_mock.pi = math.pi

# 4. Configurar pandas mock
pd_mock = sys.modules['pandas']
pd_mock.DataFrame = MagicMock

# 5. Configurar sqlalchemy mock
sa_mock = sys.modules['sqlalchemy']
sa_mock.create_engine = MagicMock()
sa_mock.text = MagicMock()
