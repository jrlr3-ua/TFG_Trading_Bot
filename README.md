# 🤖 TFG: Sistema de Trading Algorítmico Híbrido

> Trabajo de Final de Grado — Joan Romà Llorca  
> Universitat d'Alacant (UA) — Escuela Politécnica Superior

## 📋 Descripción

Sistema de **trading algorítmico institucional** basado en [Freqtrade](https://www.freqtrade.io/) que combina **7 capas de análisis** para generar señales de compra/venta en el mercado de futuros de criptomonedas:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 🤖 Machine Learning | LightGBM (FreqAI) | Predicción de % de cambio del precio (Regresión) |
| 📰 NLP | FinBERT + NER | Sentimiento per-coin de noticias financieras |
| 📊 Order Flow | Order Book Imbalance | Detección de presión institucional |
| 📈 Análisis Técnico | SMA/EMA/ADX (H1) | Filtro de tendencia macro + régimen |
| 🛡️ Risk Management | Kelly + ATR + Circuit Breaker | Protección dinámica de capital |
| 🔗 On-Chain | Fear & Greed Index | Bloqueo en extremos de mercado |
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
├── docker-compose.yml              # Orquestación de microservicios
├── Dockerfile                      # Bot principal (FreqAI + LightGBM)
├── Dockerfile.sentiment            # Motor NLP (FinBERT)
├── Dockerfile.onchain              # Ingestor On-Chain (Fear & Greed)
├── Makefile                        # Comandos operativos (start/stop/logs/test/backup)
├── deploy_ubuntu.sh                # Script de despliegue automatizado para VPS
├── backup_db.sh                    # Backup de TimescaleDB con retención de 7 días
├── .env.example                    # Template de variables de entorno
├── data_engineering/
│   ├── sentiment_ingestor.py       # Pipeline NLP: RSS → FinBERT → TimescaleDB
│   └── onchain_ingestor.py         # Pipeline On-Chain: Fear & Greed → TimescaleDB
├── docs/
│   ├── memoria/memoria_tfg.md      # Memoria completa del TFG
│   ├── strategy_evolution.md       # Evolución cronológica v1.0 → v5.0
│   ├── GUIA_USO_REAL.md            # Guía de despliegue en producción
│   ├── HOME_SERVER_SETUP.md        # Guía de servidor On-Premise casero
│   └── tradingview_tfg_v4.pine     # Proxy visual PineScript para TradingView
├── grafana/
│   └── provisioning/               # Dashboard y datasources de Grafana
├── tests/
│   ├── test_strategy.py            # Tests: Half-Kelly, ATR Stop Loss
│   └── test_nlp.py                 # Tests: HTML clean, NER, Fallback
├── user_data/
│   ├── config.json                 # Configuración principal (dry_run, FreqAI, pares)
│   ├── config_secrets.json.example # Template de credenciales (Telegram, API)
│   └── strategies/
│       └── FreqaiExampleStrategy.py  # Estrategia activa (v5.0 Institutional)
└── archive/                        # Versiones legacy y ficheros históricos
```

## 📊 Acceso a Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| FreqUI (Bot) | `http://localhost:8081` | Interfaz web del bot principal |
| Grafana | `http://localhost:3000` | Dashboard de PnL y sentimiento |
| Tensorboard | `http://localhost:6006` | Monitorización MLOps del modelo |

## 📈 Resultados de Backtesting

| Escenario | Win Rate | Sharpe | Max Drawdown | Mercado (B&H) |
|-----------|----------|--------|--------------|----------------|
| Bull Market | 71% | 1.13 | 2.83% | +11.74% |
| Bear/Crash | ~50% | 1.72 | 9.49% | -34.57% |
| Lateral | 59.3% | 1.89 | 4.25% | +13.49% |

## 📝 Licencia

Proyecto académico — Todos los derechos reservados.  
© 2026 Joan Romà Llorca — Universitat d'Alacant
