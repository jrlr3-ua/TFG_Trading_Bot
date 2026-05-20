# ═══════════════════════════════════════════════════════════════════════
# TFG Trading Bot — Backtesting Exhaustivo v4.0 Institucional (PowerShell)
# ═══════════════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "🚀 BACKTESTING EXHAUSTIVO v4.0 INSTITUCIONAL — 5 MOMENTOS"
Write-Host "═══════════════════════════════════════════════════════════"

Write-Host "📥 Descargando datos Ene 2025 - Mar 2026..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h --timerange 20250101-20260401 --exchange binance --trading-mode futures

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "═══ BACKTEST #1: 🟢 BULL FUERTE (Abr-May 2025) ══════════"
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250401-20250601 | Out-File -FilePath backtest_v40_1_bull.txt -Encoding utf8

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "═══ BACKTEST #2: 🔴 BEAR SEVERO (Feb-Abr 2025) ══════════"
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250201-20250401 | Out-File -FilePath backtest_v40_2_bear.txt -Encoding utf8

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "═══ BACKTEST #3: 🟡 LATERAL/MIXTO (Ago-Oct 2025) ════════"
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250801-20251001 | Out-File -FilePath backtest_v40_3_lateral.txt -Encoding utf8

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "═══ BACKTEST #4: ⚫ CRASH (Oct-Dic 2025) ════════════════"
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20251001-20251201 | Out-File -FilePath backtest_v40_4_crash.txt -Encoding utf8

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "🏆 RESUMEN FINAL — TODOS LOS BACKTESTS COMPLETADOS"
Write-Host "═══════════════════════════════════════════════════════════"
