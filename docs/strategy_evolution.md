# Evolución de la Estrategia FreqAI

Este documento describe la evolución de la estrategia principal del TFG,
desde la primera versión hasta la versión actual en producción.

## Versión 1.0 — Gold Master (Institutional Grade)

**Archivo:** `FreqaiExampleStrategy_legacy.py` → clase `FreqaiExampleStrategy_v1`

Primera versión funcional con arquitectura completa de 7 capas.

**Características:**
- Parámetros por defecto (no optimizados): SMA 200, EMA 50, confianza IA 55%
- `custom_stake_amount` con Kelly Criterion (dimensionamiento dinámico)
- Circuit Breaker con umbral conservador (-3%)
- Order Flow con filtro de imbalance > 0.4 en entrada
- Feature: ROC (Rate of Change) incluido en FreqAI
- `merge_sentiment_data` se ejecutaba siempre (backtest incluido)

**Problema detectado:**
- `custom_stake_amount` limitaba artificialmente los trades a 5-6 USDT
- ROI y stoploss definidos en `.py` entraban en conflicto con `config.json`

---

## Versión 1.1 — Optimized for Hyperopt

**Archivo:** `FreqaiExampleStrategy_legacy.py` → clase `FreqaiExampleStrategy_v1_1`

Parámetros optimizados mediante algoritmo genético (Hyperopt).

**Cambios respecto a v1.0:**

| Parámetro | v1.0 | v1.1 (Hyperopt) |
|---|---|---|
| `buy_sma_period` | 200 | **160** |
| `buy_ema_period` | 50 | **79** |
| `ai_confidence_long` | 0.55 | **0.864** |
| `ai_confidence_short` | 0.45 | **0.125** |
| `stoploss` | -0.01 | **-0.215** |
| `minimal_roi[0]` | 0.10 | **0.1** |

**Otros cambios:**
- NLP solo en live/dry-run (más rápido en backtest)
- ROC eliminado de features FreqAI
- Order Flow sin filtro estricto en entrada

---

## Versión 1.2 — Production (Config-Driven)

**Archivo:** `FreqaiExampleStrategy.py`

Versión limpia, optimizada y preparada para producción.

**Cambios respecto a v1.1:**
- `minimal_roi` y `stoploss` **delegados al config.json** (resuelve conflicto de precedencia)
- `custom_stake_amount` **eliminado** → usa `unlimited` con balance/slots
- Circuit Breaker ajustado a **-10%** (acorde al apalancamiento x10)
- Cálculo de BBANDS **optimizado** (una sola llamada en vez de tres)
- Método NLP renombrado a `_merge_sentiment_data` (convención privada)
- Docstrings completos en todos los métodos
- Código reducido de 745 a ~200 líneas

---

## Versión 2.0 — Matrícula de Honor ← ACTUAL

**Archivo:** `FreqaiExampleStrategy.py`

Salto cualitativo en la inteligencia del bot.

**Mejora 1: Feature Engineering ampliado (5 → 12 features)**

| Feature | Categoría | Justificación |
|---|---|---|
| RSI | Momentum | Sobrecompra/venta |
| Stochastic RSI | Momentum | RSI del RSI (más sensible) |
| MFI | Momentum | RSI ponderado por volumen |
| MACD Histograma | Momentum | Cruces de tendencia |
| BB Width | Volatilidad | Amplitud de bandas normalizada |
| ATR normalizado | Volatilidad | Volatilidad relativa al precio |
| OBV normalizado | Volumen | Presión compradora/vendedora |
| Log Returns | Estadístico | Mejor distribución para ML |
| Return Std | Estadístico | Régimen de mercado |
| Candle Direction | Precio | Ratio close/open |
| Sentimiento NLP | Fundamental | FinBERT via TimescaleDB |
| Pct Change | Precio | Cambio porcentual |

**Mejora 2: Target de regresión**
- Antes: binario (1=sube, 0=baja) → no distinguía magnitud
- Ahora: `&s-price_change` = % de cambio real del precio en N velas
- Permite ajustar entradas por magnitud del movimiento predicho

**Mejora 3: Stop Loss dinámico (ATR)**
- Antes: stop fijo -1%
- Ahora: `custom_stoploss` calcula stop = 2×ATR / precio
- Mercado volátil → stop más amplio (evita salidas por ruido)
- Mercado tranquilo → stop más estrecho (protege capital)
- Limitado entre -0.5% y -3% por seguridad
