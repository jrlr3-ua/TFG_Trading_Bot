#!/bin/bash
# Script de 5 backtests secuenciales — v2.1 (v2.0 + ADX)
# Ejecuta automáticamente un backtest tras otro

set -e

echo "═══════════════════════════════════════════════════════"
echo "  BACKTESTING v2.1 — 5 Escenarios de Mercado"
echo "═══════════════════════════════════════════════════════"

# ─── FASE 1: Descargar datos Ene-Jun 2025 ───
echo ""
echo "📥 Descargando datos Ene-Jun 2025..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h \
    --timerange 20250101-20250601 --exchange binance --trading-mode futures --erase

# ─── BACKTEST #1: Bull Fuerte (Abr-May 2025) ───
echo ""
echo "═══ BACKTEST #1/5: 🟢 BULL FUERTE (Abr-May 2025) ═══"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250401-20250601 \
    | tail -n 30 | tee /tmp/bt1_result.txt
echo "✅ Backtest #1 completado"

# ─── BACKTEST #2: Bear Severo (Feb-Abr 2025) ───
echo ""
echo "═══ BACKTEST #2/5: 🔴 BEAR SEVERO (Feb-Abr 2025) ═══"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250201-20250401 \
    | tail -n 30 | tee /tmp/bt2_result.txt
echo "✅ Backtest #2 completado"

# ─── FASE 2: Descargar datos Jun 2025 - Abr 2026 ───
echo ""
echo "📥 Descargando datos Jun 2025 - Abr 2026..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h \
    --timerange 20250601-20260401 --exchange binance --trading-mode futures --erase

# ─── BACKTEST #3: Lateral/Mixto (Ago-Oct 2025) ───
echo ""
echo "═══ BACKTEST #3/5: 🟡 LATERAL/MIXTO (Ago-Oct 2025) ═══"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250801-20251001 \
    | tail -n 30 | tee /tmp/bt3_result.txt
echo "✅ Backtest #3 completado"

# ─── BACKTEST #4: Crash (Oct-Dic 2025) ───
echo ""
echo "═══ BACKTEST #4/5: ⚫ CRASH (Oct-Dic 2025) ═══"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20251001-20251201 \
    | tail -n 30 | tee /tmp/bt4_result.txt
echo "✅ Backtest #4 completado"

# ─── BACKTEST #5: Bear Moderado (Feb-Mar 2026) ───
echo ""
echo "═══ BACKTEST #5/5: 🔵 BEAR MODERADO (Feb-Mar 2026) ═══"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20260201-20260401 \
    | tail -n 30 | tee /tmp/bt5_result.txt
echo "✅ Backtest #5 completado"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🏆 TODOS LOS BACKTESTS COMPLETADOS"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Resultados guardados en /tmp/bt1_result.txt a /tmp/bt5_result.txt"
