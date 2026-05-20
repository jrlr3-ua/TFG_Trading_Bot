#!/bin/bash
# ================================================================
# TFG: Script de Backtesting Comparativo
# ================================================================
# Ejecuta backtests con la estrategia v2.0 y genera resultados
# para análisis posterior.
#
# Uso: docker compose run --rm freqtrade bash /freqtrade/user_data/scripts/run_backtests.sh
# ================================================================

set -e

echo "════════════════════════════════════════════════════════════"
echo "  🧪 TFG — BACKTESTING COMPARATIVO"
echo "════════════════════════════════════════════════════════════"

# Configuración
TIMERANGE="20260201-20260401"
CONFIG="/freqtrade/user_data/config.json"
STRATEGY="FreqaiExampleStrategy"
MODEL="LightGBMRegressor"

# ─── PASO 1: Descargar datos frescos ────────────────────────────
echo ""
echo "📥 PASO 1: Descargando datos de mercado..."
echo "────────────────────────────────────────────"
freqtrade download-data \
    --config $CONFIG \
    --timerange $TIMERANGE \
    --timeframes 5m 15m 1h \
    --trading-mode futures

echo "✅ Datos descargados"

# ─── PASO 2: Backtest principal (v2.0) ──────────────────────────
echo ""
echo "🧠 PASO 2: Ejecutando backtest v2.0 (12 features, regresión, ATR stop)..."
echo "────────────────────────────────────────────"
freqtrade backtesting \
    --config $CONFIG \
    --strategy $STRATEGY \
    --freqaimodel $MODEL \
    --timerange $TIMERANGE \
    --timeframe 5m \
    --export trades \
    --export-filename /freqtrade/user_data/backtest_results/v2_0_result.json

echo "✅ Backtest v2.0 completado"

# ─── PASO 3: Resumen ────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ BACKTESTING COMPLETADO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📁 Resultados guardados en: user_data/backtest_results/"
echo ""
echo "Para ver los resultados detallados:"
echo "  freqtrade backtesting-show"
echo ""
echo "Para generar gráficos:"
echo "  freqtrade plot-profit --config $CONFIG --strategy $STRATEGY"
echo ""
