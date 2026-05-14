# 🤖 TFG: Sistema de Trading Algorítmico Híbrido

> Trabajo de Final de Grado — Joan Romà Llorca  
> Universitat d'Alacant (UA) — Escuela Politécnica Superior  
> Grado en Ingeniería Informática — Curso 2025–2026

## 📋 Descripción

Sistema de **trading algorítmico institucional** basado en [Freqtrade](https://www.freqtrade.io/) que combina **7 capas de análisis** para generar señales de compra/venta en el mercado de futuros de criptomonedas:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 🤖 Machine Learning | LightGBM (FreqAI) | Predicción de % de cambio del precio (Regresión) |
| 📰 NLP | FinBERT + NER per-coin | Sentimiento de noticias financieras por moneda |
| 📊 Order Flow | Order Book Imbalance | Detección de presión institucional |
| 📈 Análisis Técnico | SMA/EMA/ADX (H1) | Filtro de tendencia macro + régimen de mercado |
| 🛡️ Risk Management | Conviction Sizing + ATR + Circuit Breaker | Protección dinámica de capital |
| 🔗 On-Chain | Fear & Greed Index | Bloqueo en extremos emocionales del mercado |
| 🔄 Multi-Timeframe | Features 5m/15m/1h | Visión micro-macro cruzada |

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────┐
│                     Docker Compose                        │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Bot FreqAI  │  │   Sentiment  │  │   On-Chain     │  │
│  │  (LightGBM)  │  │   (FinBERT)  │  │  (F&G Index)   │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                 │                   │           │
│         ▼                 ▼                   ▼           │
│  ┌───────────────────────────────────────────────────┐    │
│  │           TimescaleDB (PostgreSQL 14)              │    │
│  └─────────────────────┬─────────────────────────────┘    │
│                        │                                  │
│              ┌─────────┴──────────┐                       │
│              ▼                    ▼                        │
│  ┌────────────────┐   ┌────────────────┐                  │
│  │    Grafana      │   │  Tensorboard   │                  │
│  │  (Dashboard)    │   │   (MLOps)      │                  │
│  └────────────────┘   └────────────────┘                  │
└──────────────────────────────────────────────────────────┘
```

## 🚀 Requisitos

- **Docker** y **Docker Compose** v2+
- **4 GB RAM** mínimo (FinBERT requiere ~400 MB para el modelo)

## ⚙️ Instalación y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/jrlr3-ua/TFG_Trading_Bot.git
   cd TFG_Trading_Bot
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   cp user_data/config_secrets.json.example user_data/config_secrets.json
   # Editar ambos ficheros con tus credenciales reales
   ```

3. **Levantar los servicios:**
   ```bash
   make start
   ```

4. **Verificar que todo funciona:**
   ```bash
   make logs       # Logs del bot principal
   make nlp-logs   # Logs del motor FinBERT
   make db-logs    # Logs de TimescaleDB
   ```

5. **Ejecutar tests:**
   ```bash
   make test
   ```

## 📁 Estructura del Proyecto

```
TFG_Trading_Bot/
├── docker-compose.yml              # Orquestación de 6 microservicios
├── Dockerfile                      # Bot principal (FreqAI + LightGBM)
├── Dockerfile.sentiment            # Motor NLP (FinBERT + NER)
├── Dockerfile.onchain              # Ingestor On-Chain (Fear & Greed)
├── Makefile                        # Comandos operativos (start/stop/logs/test)
├── deploy_ubuntu.sh                # Despliegue automatizado para VPS Ubuntu
├── backup_db.sh                    # Backup de TimescaleDB con retención 7 días
├── entrypoint.sh                   # Parche runtime datasieve
├── requirements.txt                # Dependencias Python (tests locales)
├── .env.example                    # Template de variables de entorno
├── data_engineering/
│   ├── sentiment_ingestor.py       # Pipeline NLP: RSS → FinBERT → TimescaleDB
│   └── onchain_ingestor.py         # Pipeline On-Chain: F&G → TimescaleDB
├── docs/
│   ├── memoria/                    # Memoria TFG completa (.md + .docx + figuras)
│   ├── strategy_evolution.md       # Evolución cronológica v1.0 → v3.0
│   ├── GUIA_USO_REAL.md            # Guía de despliegue en producción
│   └── HOME_SERVER_SETUP.md        # Guía de servidor casero
├── grafana/
│   └── provisioning/               # Dashboard y datasources de Grafana
├── tests/
│   ├── conftest.py                 # Configuración compartida de tests
│   ├── test_strategy.py            # Tests: Conviction Sizing, ATR Stop Loss
│   └── test_nlp.py                 # Tests: HTML clean, NER, Fallback, Aliases
├── user_data/
│   ├── config.json                 # Configuración principal del bot
│   ├── config_secrets.json.example # Template de credenciales
│   └── strategies/
│       └── FreqaiExampleStrategy.py  # Estrategia v3.0 (611 líneas)
└── archive/                        # Versiones legacy y ficheros históricos
```

## 📊 Acceso a Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| FreqUI (Bot) | `http://localhost:8081` | Interfaz web del bot principal |
| Grafana | `http://localhost:3000` | Dashboard de PnL y sentimiento |
| Tensorboard | `http://localhost:6006` | Monitorización MLOps del modelo |

## 📈 Resultados de Backtesting (Walk-Forward)

| Escenario | Bot (v3.0) | Buy & Hold | Alpha |
|-----------|-----------|------------|-------|
| Bull Market | +2.57% | +11.74% | -9.17% |
| Crash | -1.03% | -34.57% | **+33.54%** |
| Lateral | -0.56% | +13.49% | -14.05% |
| Bear Market | -7.00% | -36.00% | **+29.00%** |
| **Promedio** | **-1.51%** | **-11.34%** | **+9.83%** |

> **Conclusión:** El sistema genera un alpha promedio de +9.83 puntos porcentuales sobre Buy & Hold, con su mayor ventaja durante las crisis de mercado donde actúa como preservador de capital.

## 🧪 Tests

```bash
# Ejecutar la suite completa (10 tests)
make test

# Resultado esperado:
# tests/test_strategy.py::test_conviction_based_sizing      PASSED
# tests/test_strategy.py::test_conviction_sizing_no_wallets  PASSED
# tests/test_strategy.py::test_dynamic_atr_stoploss          PASSED
# tests/test_strategy.py::test_atr_stoploss_low_volatility   PASSED
# tests/test_nlp.py::test_clean_html_logic                   PASSED
# tests/test_nlp.py::test_clean_html_nested_tags             PASSED
# tests/test_nlp.py::test_detect_coins_ner                   PASSED
# tests/test_nlp.py::test_detect_coins_case_insensitive      PASSED
# tests/test_nlp.py::test_fallback_headlines                  PASSED
# tests/test_nlp.py::test_coin_aliases_completeness           PASSED
```

## 📝 Licencia

Proyecto académico — Todos los derechos reservados.  
© 2026 Joan Romà Llorca — Universitat d'Alacant
