#!/bin/bash
# run_massive_hyperopt.sh
# Pipeline de Fuerza Bruta para Vía 2 (Máxima Rentabilidad)

echo "=========================================================="
echo "🚀 VÚA 2 - INICIANDO HYPEROPT MASIVO SOBRE FreqaiExampleStrategy"
echo "=========================================================="
echo ""

echo "📥 1️⃣ Descargando datos masivos (Enero 2024 - Junio 2025)..."
docker compose run --rm freqtrade download-data -t 5m 15m 1h \
    --timerange 20240101-20250601 --exchange binance --trading-mode futures

echo ""
echo "⚙️ 2️⃣ Lanzando Hyperopt (500 Epochs)..."
# Optimizamos thresholds (buy/sell espacios parametrizados), ROI y Stoploss/Trailing
# SharpeHyperOptLoss castiga las estrategias ruidosas.
docker compose run --rm freqtrade hyperopt \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy roi stoploss trailing \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20240201-20250601 \
    -e 500 \
    --min-trades 50 > massive_hyperopt_v12.log 2>&1

echo "✅ Hyperopt Masivo finalizado. Los resultados y los parámetros óptimos están en massive_hyperopt_v12.log"
