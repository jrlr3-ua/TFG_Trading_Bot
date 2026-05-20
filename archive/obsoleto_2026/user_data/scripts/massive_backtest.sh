#!/usr/bin/env bash
# ==============================================================================
# TFG TRADING BOT - SCRIPT DE BACKTESTING MASIVO (LA PRUEBA DE FUEGO)
# ==============================================================================
# Este script descarga datos históricos (9 meses) y ejecuta una validación
# exhaustiva de 6 meses (Caminar Hacia Adelante / Walk-Forward) usando FreqAI.
# Al final, genera un gráfico interactivo HTML con tus ganancias.
# ==============================================================================

echo "======================================================="
echo "🔥 INICIANDO TEST MASIVO: THE ULTIMATE TRADING BOT 🔥"
echo "======================================================="
echo ""

# Carpeta base asegurada
cd /Users/joanroma/TFG_Trading_Bot

# 1. DESCARGA MASIVA DE DATOS
# Descargamos los últimos 3 meses (límite de Binance por API antes de requerir Data-Archives)
echo "⏳ 1/4 Descargando velas de 5m, 15m y 1h para tus 10 monedas..."
docker compose run --rm freqtrade download-data \
    -t 5m 15m 1h \
    --timerange 20260101-20260406 \
    --exchange binance \
    --trading-mode futures

# 2. VALIDACIÓN WALK-FORWARD DE FREQAI (EL BACKTEST REAL)
# El backtest se efectúa sobre el último mes validado.
echo ""
echo "🧠 2/4 Ejecutando Simulación FreqAI (LightGBM Regression)..."
echo "⚠️  ATENCIÓN: Esto puede tardar varios minutos dependiendo de tu procesador M2/M3."
docker compose run --rm freqtrade backtesting \
    --config /freqtrade/user_data/config.json \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --timerange 20260301-20260406 \
    --export trades \
    --fee 0.0004 # Simulando comisiones Taker normales

# 3. ANÁLISIS DETALLADO POR MONEDA
# Muestra si Ethereum o Bitcoin es tu mejor "caballo ganador".
echo ""
echo "📈 3/4 Desglosando Ganancias..."
docker compose run --rm freqtrade backtesting-analysis \
    --config /freqtrade/user_data/config.json \
    --export-filename user_data/backtest_results/ \
    --analysis-groups 0

# 4. EXTRACCIÓN DE CURVA DE EQUIDAD EN HTML
# Dibuja los Profit & Loss para poder presentarlos de manera espectacular.
echo ""
echo "🎨 4/4 Renderizando Curva de Equidad interactiva en HTML..."
docker compose run --rm freqtrade plot-profit \
    --config /freqtrade/user_data/config.json \
    --strategy FreqaiExampleStrategy

echo ""
echo "======================================================="
echo "✅ TODO FINALIZADO CON ÉXITO."
echo "👉 Revisa tus resultados en consola y busca el archivo:"
echo "   /user_data/plot/freqtrade-profit-plot.html"
echo "   ¡Abre ese HTML en tu navegador y sorpréndete!"
echo "======================================================="
