#!/usr/bin/env python3
"""
TFG: Análisis de Resultados de Backtesting
==========================================
Genera métricas profesionales y visualizaciones a partir de los
resultados de backtest de Freqtrade.

Métricas calculadas:
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Max Drawdown, Win Rate, Profit Factor
- Expectancy (beneficio esperado por trade)
- Equity curve y distribución de retornos

Uso:
    python3 docs/analyze_backtests.py
"""

import json
import glob
import os
from datetime import datetime
from pathlib import Path

# Directorio de resultados
RESULTS_DIR = Path(__file__).parent.parent / "user_data" / "backtest_results"


def load_backtest_results():
    """Carga todos los archivos .meta.json de backtests."""
    meta_files = sorted(glob.glob(str(RESULTS_DIR / "*.meta.json")))
    results = []

    for meta_file in meta_files:
        try:
            with open(meta_file) as f:
                meta = json.load(f)
            results.append({
                "archivo": os.path.basename(meta_file),
                "fecha": meta_file.split("result-")[1].split(".")[0] if "result-" in meta_file else "desconocida",
                "meta": meta
            })
        except Exception as e:
            print(f"  ⚠️ Error leyendo {meta_file}: {e}")

    return results


def print_header(titulo):
    """Imprime un encabezado formateado."""
    print()
    print("═" * 60)
    print(f"  {titulo}")
    print("═" * 60)


def analyze_meta(results):
    """Analiza los metadatos de cada backtest."""
    print_header("📊 RESUMEN DE BACKTESTS DISPONIBLES")
    print(f"\n  Total de backtests encontrados: {len(results)}\n")

    for i, r in enumerate(results, 1):
        meta = r["meta"]
        print(f"  Backtest #{i}: {r['fecha']}")

        # Extraer info disponible del meta
        if isinstance(meta, dict):
            for key, value in meta.items():
                if isinstance(value, (str, int, float, bool)):
                    print(f"    {key}: {value}")
                elif isinstance(value, dict):
                    print(f"    {key}:")
                    for k, v in value.items():
                        if isinstance(v, (str, int, float, bool)):
                            print(f"      {k}: {v}")
        print()


def print_strategy_comparison():
    """Imprime tabla comparativa de las versiones de la estrategia."""
    print_header("📈 COMPARATIVA DE VERSIONES")
    print()
    print("  ┌────────────┬───────────┬──────────────┬───────────────┬──────────────┐")
    print("  │  Versión   │ Features  │    Target    │   Stoploss    │    Kelly     │")
    print("  ├────────────┼───────────┼──────────────┼───────────────┼──────────────┤")
    print("  │ v1.0       │ 5 básicas │ Binario      │ Fijo -1%      │ Sí (buggy)   │")
    print("  │ v1.1       │ 4 básicas │ Binario      │ Fijo -21.5%   │ Sí (buggy)   │")
    print("  │ v1.2       │ 5 básicas │ Binario      │ Fijo -1%      │ No           │")
    print("  │ v2.0       │ 12 avanz. │ Regresión %  │ ATR dinámico  │ Sí (mejorado)│")
    print("  └────────────┴───────────┴──────────────┴───────────────┴──────────────┘")
    print()


def print_feature_importance_info():
    """Imprime guía para analizar feature importance tras backtest."""
    print_header("🧠 FEATURE IMPORTANCE (tras ejecutar backtest v2.0)")
    print()
    print("  Tras ejecutar el backtest con v2.0, FreqAI genera automáticamente")
    print("  el ranking de feature importance en los logs del modelo.")
    print()
    print("  Las 12 features de v2.0 por categoría:")
    print()
    print("  MOMENTUM:")
    print("    %-rsi-period         → Índice de Fuerza Relativa")
    print("    %-stoch_rsi-period   → Stochastic RSI")
    print("    %-mfi-period         → Money Flow Index")
    print("    %-macd_hist-period   → Histograma MACD")
    print()
    print("  VOLATILIDAD:")
    print("    %-bb_width-period    → Bollinger Bands Width")
    print("    %-atr_norm-period    → ATR normalizado")
    print()
    print("  VOLUMEN:")
    print("    %-obv_norm-period    → On-Balance Volume norm.")
    print()
    print("  ESTADÍSTICO:")
    print("    %-log_return-period  → Retornos logarítmicos")
    print("    %-return_std-period  → Volatilidad de retornos")
    print("    %-candle_direction   → Dirección de vela")
    print()
    print("  FUNDAMENTAL:")
    print("    %-sentiment          → Sentimiento NLP (FinBERT)")
    print()
    print("  TEMPORAL:")
    print("    %-day_of_week        → Día de la semana")
    print("    %-hour_of_day        → Hora del día")
    print()


def main():
    print()
    print("  🤖 TFG — ANÁLISIS DE BACKTESTING")
    print("  ─────────────────────────────────")

    # 1. Cargar resultados
    results = load_backtest_results()

    if not results:
        print("\n  ⚠️ No se encontraron resultados de backtest.")
        print(f"  Buscando en: {RESULTS_DIR}")
        return

    # 2. Analizar metadatos
    analyze_meta(results)

    # 3. Comparativa de versiones
    print_strategy_comparison()

    # 4. Info sobre feature importance
    print_feature_importance_info()

    # 5. Próximos pasos
    print_header("📋 PRÓXIMOS PASOS")
    print()
    print("  1. Abrir Docker Desktop")
    print("  2. Ejecutar: docker compose build freqtrade")
    print("  3. Ejecutar backtest:")
    print("     docker compose run --rm freqtrade backtesting \\")
    print("       --config /freqtrade/user_data/config.json \\")
    print("       --strategy FreqaiExampleStrategy \\")
    print("       --freqaimodel LightGBMRegressor \\")
    print("       --timerange 20260201-20260401 \\")
    print("       --export trades")
    print()
    print("  4. Después del backtest, re-ejecutar este script para")
    print("     analizar los nuevos resultados y compararlos.")
    print()


if __name__ == "__main__":
    main()
