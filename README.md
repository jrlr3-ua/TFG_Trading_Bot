# 🤖 TFG: Sistema de Trading Algorítmico Híbrido

> Trabajo de Final de Grado — Joan Romà Llorca  
> Universidad Politécnica de Valencia

## 📋 Descripción

Sistema de **trading algorítmico** basado en [Freqtrade](https://www.freqtrade.io/) que combina cinco capas de análisis para generar señales de compra/venta en el mercado de criptomonedas:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 🤖 Machine Learning | LightGBM (FreqAI) | Predicción de dirección del precio |
| 📰 NLP | FinBERT | Análisis de sentimiento de noticias |
| 📊 Order Flow | Order Book Imbalance | Detección de presión institucional |
| 📈 Análisis Técnico | SMA/EMA (H1) | Filtro de tendencia macro |
| 🛡️ Risk Management | Circuit Breaker | Protección de capital |

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                     │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Bot 1       │  │  Bot 2       │  │  Sentiment │ │
│  │  FreqAI      │  │  SMC+IA      │  │  Engine    │ │
│  │  (Principal) │  │  (Experim.)  │  │  (FinBERT) │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                 │        │
│         ▼                 ▼                 ▼        │
│  ┌─────────────────────────────────────────────────┐ │
│  │              TimescaleDB (PostgreSQL)           │ │
│  └─────────────────────┬───────────────────────────┘ │
│                        │                             │
│                        ▼                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │                   Grafana                       │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 🚀 Requisitos

- **Docker** y **Docker Compose** v2+
- **4 GB RAM** mínimo (FinBERT requiere ~400 MB para el modelo)

## ⚙️ Instalación y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd TFG_Trading_Bot
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus valores reales
   ```

3. **Levantar los servicios:**
   ```bash
   docker compose up -d --build
   ```

4. **Verificar que todo funciona:**
   ```bash
   docker compose ps                    # Estado de contenedores
   docker compose logs -f freqtrade     # Logs del bot principal
   docker compose logs -f sentiment_analysis  # Logs del motor NLP
   ```

## 📁 Estructura del Proyecto

```
TFG_Trading_Bot/
├── docker-compose.yml              # Orquestación de servicios
├── Dockerfile                      # Bot 1 (FreqAI + ML)
├── Dockerfile.sentiment            # Motor NLP (FinBERT)
├── Dockerfile.smc                  # Bot 2 (SMC)
├── .env.example                    # Template de variables de entorno
├── contexto_tfg.md                 # Contexto para IA asistente
├── data_engineering/
│   └── sentiment_ingestor.py       # Pipeline NLP → TimescaleDB
├── docs/
│   └── strategy_evolution.md       # Evolución de la estrategia
└── user_data/
    ├── config.json                 # Config principal (x10 leverage)
    ├── config_smc.json             # Config Bot SMC
    ├── strategies/
    │   ├── FreqaiExampleStrategy.py        # Estrategia activa (v1.2)
    │   ├── FreqaiExampleStrategy_legacy.py # Versiones anteriores
    │   └── SMC_Scalping_TFG.py             # Bot 2 - SMC
    ├── models/                     # Modelos FreqAI entrenados
    ├── backtest_results/           # Resultados de backtesting
    └── logs/                       # Logs de ejecución
```

## 📊 Acceso a Servicios

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| Freqtrade API (Bot 1) | `http://localhost:8081` | freqtrader / superpassword |
| Freqtrade API (Bot 2) | `http://localhost:8082` | freqtrader / superpassword |
| Grafana | `http://localhost:3000` | admin / admin |

## 📝 Licencia

Proyecto académico — Todos los derechos reservados.
