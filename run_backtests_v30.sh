#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# TFG Trading Bot — Backtesting Exhaustivo v3.0 (5 Momentos de Mercado)
# ═══════════════════════════════════════════════════════════════════════
# Ejecuta 5 backtests secuenciales en diferentes regímenes de mercado
# para validar la robustez del sistema v3.0 Institucional.
#
# IMPORTANTE: Usa el path completo de docker para evitar problemas de PATH
# ═══════════════════════════════════════════════════════════════════════

export PATH="/usr/local/bin:$PATH"

echo "═══════════════════════════════════════════════════════════"
echo "🚀 BACKTESTING EXHAUSTIVO v3.0 — 5 MOMENTOS DE MERCADO"
echo "═══════════════════════════════════════════════════════════"
echo "Inicio: $(date)"
echo ""

# ─── FASE 1: Descargar datos Ene 2025 - Jun 2025 ───
echo "📥 Descargando datos Ene 2025 - Jun 2025..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h \
    --timerange 20250101-20250601 --exchange binance --trading-mode futures

# ─── BACKTEST #1: Bull Fuerte (Abr-May 2025) ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "═══ BACKTEST #1/5: 🟢 BULL FUERTE (Abr-May 2025) ═══════"
echo "═══════════════════════════════════════════════════════════"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250401-20250601 2>&1 \
    | tee backtest_v30_1_bull.txt
echo "✅ Backtest #1 completado"

# ─── BACKTEST #2: Bear Severo (Feb-Abr 2025) ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "═══ BACKTEST #2/5: 🔴 BEAR SEVERO (Feb-Abr 2025) ════════"
echo "═══════════════════════════════════════════════════════════"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250201-20250401 2>&1 \
    | tee backtest_v30_2_bear.txt
echo "✅ Backtest #2 completado"

# ─── FASE 2: Descargar datos Jun 2025 - Abr 2026 ───
echo ""
echo "📥 Descargando datos Jun 2025 - Abr 2026..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h \
    --timerange 20250601-20260401 --exchange binance --trading-mode futures

# ─── BACKTEST #3: Lateral/Mixto (Ago-Oct 2025) ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "═══ BACKTEST #3/5: 🟡 LATERAL/MIXTO (Ago-Oct 2025) ══════"
echo "═══════════════════════════════════════════════════════════"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20250801-20251001 2>&1 \
    | tee backtest_v30_3_lateral.txt
echo "✅ Backtest #3 completado"

# ─── BACKTEST #4: Crash (Oct-Dic 2025) ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "═══ BACKTEST #4/5: ⚫ CRASH (Oct-Dic 2025) ═══════════════"
echo "═══════════════════════════════════════════════════════════"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20251001-20251201 2>&1 \
    | tee backtest_v30_4_crash.txt
echo "✅ Backtest #4 completado"

# ─── BACKTEST #5: Recuperación (Ene-Mar 2026) ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "═══ BACKTEST #5/5: 🔵 RECUPERACIÓN (Ene-Mar 2026) ════════"
echo "═══════════════════════════════════════════════════════════"
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20260101-20260401 2>&1 \
    | tee backtest_v30_5_recovery.txt
echo "✅ Backtest #5 completado"

# ─── RESUMEN FINAL ───
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🏆 RESUMEN FINAL — TODOS LOS BACKTESTS COMPLETADOS"
echo "═══════════════════════════════════════════════════════════"
echo "Fin: $(date)"
echo ""
echo "Archivos generados:"
echo "  📄 backtest_v30_1_bull.txt"
echo "  📄 backtest_v30_2_bear.txt"
echo "  📄 backtest_v30_3_lateral.txt"
echo "  📄 backtest_v30_4_crash.txt"
echo "  📄 backtest_v30_5_recovery.txt"
echo ""
echo "Para analizar los resultados:"
echo "  grep -A5 'TOTAL' backtest_v30_*.txt"
echo "═══════════════════════════════════════════════════════════"
