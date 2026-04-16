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

---

## Versión 2.1 — ADX Regime Filter

**Archivo:** `FreqaiExampleStrategy.py`

Corrección de pérdidas en mercados laterales.

**Cambios respecto a v2.0:**
- **ADX Filter (Capa 6):** No opera cuando ADX < 20 (mercado lateral sin tendencia)
- Mantiene TODA la configuración rentable de v2.0

---

## Versión 3.0 — Institutional Multi-Timeframe ← ACTUAL

**Archivo:** `FreqaiExampleStrategy.py`

Salto institucional: 5 mejoras estratégicas profundas.

**Mejora 1: Multi-Timeframe Features (MTF)**

| Feature MTF | Descripción | Justificación |
|---|---|---|
| price_ratio_5m_1h | Ratio precio 5m vs cierre H1 | Divergencia micro/macro |
| dist_sma200_1h | Distancia al SMA200 en H1 | Posición relativa a tendencia |
| dist_ema50_1h | Distancia al EMA50 en H1 | Zona de valor macro |
| adx_1h_norm | ADX H1 normalizado (0-1) | Fuerza de tendencia macro |
| volume_ratio | Volumen relativo a media 50p | Confirma interés real |
| hour_sin/cos | Codificación cíclica horaria | Preserva circularidad temporal |
| day_sin/cos | Codificación cíclica diaria | Preserva circularidad semanal |

La IA ahora ve el "bosque" (H1) además de los "árboles" (5m).

**Mejora 2: NLP per-coin (NER - Named Entity Recognition)**

- Antes: Sentimiento global (1 score para todo el mercado)
- Ahora: Detecta qué moneda menciona cada titular
- Ejemplo: "Ethereum sube, Ripple cae" → ETH: +0.9, XRP: -0.8
- Nueva tabla `coin_sentiment` en TimescaleDB
- Fallback a sentimiento global si no hay datos per-coin

**Mejora 3: On-Chain & Macroeconómicos**

- Nuevo microservicio `onchain_data` (6º contenedor Docker)
- Descarga Fear & Greed Index cada 15 min
- Descarga BTC Dominance y Market Cap total
- `confirm_trade_entry` consulta F&G: bloquea LONGs en Extreme Greed (>85) y SHORTs en Extreme Fear (<15)

**Mejora 4: MLOps (Trazabilidad de la IA)**

- `_log_prediction_metrics()`: Log de cada predicción (par, señal, confianza, sentimiento, ADX)
- Log de señales de entrada en `populate_entry_trend`
- Log de trades confirmados en `confirm_trade_entry`
- Pipeline NLP logging: distribución pos/neg/neutral, latencia

**Mejora 5: Maker Pricing (Optimización de Comisiones)**

- `price_side: "other"` en entry_pricing y exit_pricing
- Al comprar: orden limit al precio del bid (lado opuesto)
- Al vender: orden limit al precio del ask (lado opuesto)
- Comisión Maker: 0.02% vs Taker: 0.05% (ahorro del 60%)
