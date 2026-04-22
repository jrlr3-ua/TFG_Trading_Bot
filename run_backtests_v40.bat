@echo off
echo =======================================================
echo BACKTESTING EXHAUSTIVO v4.0 INSTITUCIONAL
echo =======================================================

echo Descargando datos Ene 2025 - Mar 2026...
docker compose run --rm freqtrade download-data -t 5m 15m 1h --timerange 20250101-20260401 --exchange binance --trading-mode futures

echo =======================================================
echo === BACKTEST #1: BULL FUERTE (Abr-May 2025) ===
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250401-20250601 > backtest_v40_1_bull.txt

echo =======================================================
echo === BACKTEST #2: BEAR SEVERO (Feb-Abr 2025) ===
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250201-20250401 > backtest_v40_2_bear.txt

echo =======================================================
echo === BACKTEST #3: LATERAL/MIXTO (Ago-Oct 2025) ===
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20250801-20251001 > backtest_v40_3_lateral.txt

echo =======================================================
echo === BACKTEST #4: CRASH (Oct-Dic 2025) ===
docker compose run --rm freqtrade backtesting --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --timerange 20251001-20251201 > backtest_v40_4_crash.txt

echo =======================================================
echo TODOS LOS BACKTESTS COMPLETADOS
echo =======================================================
