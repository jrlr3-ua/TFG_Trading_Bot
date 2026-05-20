#  Guía Completa de Despliegue y Explicación del Proyecto

## Sistema de Trading Algorítmico Híbrido — TFG Joan Romà Llorca

**Versión:** 3.0 | **Última actualización:** Mayo 2026

---

## Índice

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Requisitos Previos](#3-requisitos-previos)
4. [Instalación Local (Desarrollo)](#4-instalación-local-desarrollo)
5. [Despliegue en Servidor VPS (Producción)](#5-despliegue-en-servidor-vps-producción)
6. [Configuración de Credenciales](#6-configuración-de-credenciales)
7. [Operación del Sistema](#7-operación-del-sistema)
8. [Monitorización y Dashboards](#8-monitorización-y-dashboards)
9. [Ejecución de Backtests](#9-ejecución-de-backtests)
10. [Tests Unitarios](#10-tests-unitarios)
11. [Mantenimiento y Troubleshooting](#11-mantenimiento-y-troubleshooting)
12. [Estructura del Repositorio](#12-estructura-del-repositorio)

---

## 1. Visión General del Proyecto

### ¿Qué es?

Un bot de trading algorítmico que opera de forma **autónoma 24/7** en el mercado de futuros de criptomonedas (Binance Futures). Combina **7 capas de análisis** para tomar decisiones:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 1 | SMA 200 (H1) | Filtro de tendencia macro |
| 2 | ADX (H1) | Detección de régimen (tendencial vs lateral) |
| 3 | EMA 50 (H1) | Zona de valor |
| 4 | LightGBM (FreqAI) | Predicción de precio con IA |
| 5 | FinBERT (NLP) | Análisis de sentimiento de noticias |
| 6 | Volumen | Confirmación de interés del mercado |
| 7 | Order Book Imbalance | Presión compradora/vendedora |

### ¿Cómo funciona?

```
Datos de Mercado (Binance API)
         │
         ▼
┌─────────────────────────────────────────────┐
│         FREQTRADE (Bot Principal)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 18+      │  │ LightGBM │  │ 7 Capas  │  │
│  │ Features │──│ Regressor│──│ Confluenc│  │
│  │ Pipeline │  │ (FreqAI) │  │ Filter   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│         │              │             │      │
│    ┌────▼──────────────▼─────────────▼──┐   │
│    │     Motor de Decisión + Riesgo     │   │
│    │  Kelly 40% │ ATR Stop │ C.Breaker  │   │
│    └────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Binance Futures   │
    │   (Ejecución)       │
    └─────────────────────┘
```

### Universo de Activos (11 pares)

BTC, ETH, SOL, BNB, ADA, XRP, DOT, LINK, AVAX, DOGE, NEAR — todos contra USDT en futuros perpetuos.

---

## 2. Arquitectura del Sistema

El sistema está compuesto por **6 microservicios Docker** independientes:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Freqtrade   │  │  Sentiment   │  │  On-Chain     │   │
│  │  (Bot + IA)  │  │  Engine      │  │  Ingestor     │   │
│  │  :8081       │  │  (FinBERT)   │  │  (Fear&Greed) │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘   │
│         │                 │                  │            │
│         └─────────────────┼──────────────────┘            │
│                           │                               │
│                  ┌────────▼────────┐                      │
│                  │  TimescaleDB    │                      │
│                  │  (PostgreSQL)   │                      │
│                  │  :5432          │                      │
│                  └────────┬────────┘                      │
│                           │                               │
│              ┌────────────┼────────────┐                  │
│              │                         │                  │
│     ┌────────▼────────┐  ┌─────────────▼──┐              │
│     │    Grafana       │  │  Tensorboard   │              │
│     │    :3000         │  │  :6006         │              │
│     └─────────────────┘  └────────────────┘              │
└──────────────────────────────────────────────────────────┘
```

| Servicio | Contenedor | Puerto | Función |
|----------|-----------|--------|---------|
| `freqtrade` | `freqtrade_elite_bot` | 8081 | Bot principal + FreqAI + LightGBM |
| `sentiment_analysis` | `sentiment_engine` | — | Motor NLP FinBERT + NER |
| `timescaledb` | `freqtrade_db` | 5432 | Base de datos de series temporales |
| `grafana` | `freqtrade_viz` | 3000 | Dashboard de visualización |
| `onchain_data` | `onchain_engine` | — | Ingestor Fear & Greed / BTC Dominance |
| `tensorboard` | `mlops_tensorboard` | 6006 | Monitorización MLOps |

---

## 3. Requisitos Previos

### Hardware Mínimo

| Componente | Mínimo | Recomendado |
|-----------|--------|-------------|
| RAM | 4 GB | 8 GB |
| CPU | 2 vCPU | 4 vCPU |
| Disco | 20 GB SSD | 40 GB SSD |
| Red | 10 Mbps | 100 Mbps |

### Software

- **Docker** ≥ 24.0 y **Docker Compose** ≥ v2
- **Git** para clonar el repositorio
- **Sistema Operativo:** Ubuntu 22.04+ (servidor) / macOS o Linux (desarrollo)

### Cuentas Necesarias

1. **Binance** — Cuenta verificada con acceso a Futures
2. **Telegram** — Bot creado vía @BotFather (opcional, para notificaciones)

---

## 4. Instalación Local (Desarrollo)

### 4.1 Clonar el Repositorio

```bash
git clone https://github.com/jrlr3-ua/TFG_Trading_Bot.git
cd TFG_Trading_Bot
```

### 4.2 Configurar Variables de Entorno

```bash
# Copiar la plantilla de variables de entorno
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Base de Datos (TimescaleDB)
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=freqtrade

# Telegram Bot (opcional)
TELEGRAM_TOKEN=tu_token_bot_telegram
TELEGRAM_CHAT_ID=tu_chat_id

# Grafana
GF_SECURITY_ADMIN_PASSWORD=tu_password_grafana

# Freqtrade API (para FreqUI)
FREQTRADE_JWT_SECRET=una_clave_secreta_larga
FREQTRADE_USERNAME=freqtrader
FREQTRADE_PASSWORD=tu_password_freqtrade
```

### 4.3 Configurar Credenciales del Exchange

```bash
# Copiar la plantilla de secretos
cp user_data/config_secrets.json.example user_data/config_secrets.json
```

Edita `user_data/config_secrets.json`:

```json
{
    "exchange": {
        "key": "TU_API_KEY_DE_BINANCE",
        "secret": "TU_API_SECRET_DE_BINANCE"
    },
    "telegram": {
        "enabled": true,
        "token": "TU_TOKEN_BOT_TELEGRAM",
        "chat_id": "TU_CHAT_ID"
    }
}
```

### 4.4 Levantar el Sistema

```bash
# Construir e iniciar todos los servicios
make start

# Equivalente a:
docker compose up -d --build
```

### 4.5 Verificar que Todo Funciona

```bash
# Ver el estado de los contenedores
docker compose ps

# Resultado esperado:
# NAME                  STATUS
# freqtrade_elite_bot   Up (healthy)
# sentiment_engine      Up
# freqtrade_db          Up (healthy)
# freqtrade_viz         Up
# onchain_engine        Up
# mlops_tensorboard     Up

# Ver logs del bot principal
make logs
```

---

## 5. Despliegue en Servidor VPS (Producción)

### 5.1 Selección del Servidor

**Opciones recomendadas:**

| Proveedor | Plan | RAM | CPU | Precio/mes |
|-----------|------|-----|-----|-----------|
| Hetzner Cloud | CAX11 (ARM) | 4 GB | 2 vCPU | ~4€ |
| Hetzner Cloud | CPX21 | 4 GB | 3 vCPU | ~8€ |
| Contabo | VPS S | 8 GB | 4 vCPU | ~6€ |
| Oracle Cloud | VM.Standard.A1 | 6 GB | 1 OCPU | **Gratis** |

> **Nota:** Oracle Cloud ofrece instancias ARM gratuitas permanentemente (Always Free Tier) con hasta 24 GB RAM y 4 OCPU. Es la opción más económica para un proyecto académico.

### 5.2 Conexión al Servidor

```bash
# Conectar por SSH (sustituye con tu IP)
ssh root@TU_IP_DEL_SERVIDOR

# Si usas clave SSH (recomendado):
ssh -i ~/.ssh/tu_clave root@TU_IP_DEL_SERVIDOR
```

### 5.3 Despliegue Automático

```bash
# 1. Clonar el repositorio en el servidor
git clone https://github.com/jrlr3-ua/TFG_Trading_Bot.git
cd TFG_Trading_Bot

# 2. Configurar credenciales (ANTES de ejecutar deploy)
cp .env.example .env
nano .env  # Rellena con tus valores reales

cp user_data/config_secrets.json.example user_data/config_secrets.json
nano user_data/config_secrets.json  # API keys de Binance + Telegram

# 3. Ejecutar el script de despliegue automático
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

El script `deploy_ubuntu.sh` automatiza:
1.  Actualización del sistema operativo
2.  Configuración del firewall (UFW) — solo puertos 22, 3000, 8081
3.  Instalación de Docker y Docker Compose
4.  Construcción e inicio de los 6 contenedores

### 5.4 Verificación Post-Despliegue

```bash
# Verificar que los 6 servicios están corriendo
docker compose ps

# Verificar los logs (debe mostrar entrenamiento de LightGBM)
docker compose logs -f freqtrade

# Verificar que TimescaleDB está healthy
docker compose exec timescaledb pg_isready -U postgres

# Verificar que el motor NLP está procesando noticias
docker compose logs sentiment_analysis | tail -20

# Verificar acceso web
curl -I http://localhost:3000  # Grafana
curl -I http://localhost:8081  # FreqUI
```

### 5.5 Configuración de Seguridad (Producción)

```bash
# Verificar firewall
sudo ufw status
# Debe mostrar:
# 22/tcp    ALLOW    (SSH)
# 3000/tcp  ALLOW    (Grafana)
# 8081/tcp  ALLOW    (FreqUI)

# IMPORTANTE: El puerto 5432 (PostgreSQL) NO debe estar expuesto al exterior
# Si lo está, bloquearlo:
sudo ufw deny 5432/tcp

# Verificar que los secretos NO están en Git
git status  # .env y config_secrets.json NO deben aparecer
cat .gitignore | grep -E "\.env|config_secrets"
```

---

## 6. Configuración de Credenciales

### 6.1 API Keys de Binance

1. Accede a [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Crea una nueva API Key
3. **Permisos obligatorios:**
   - ✅ Enable Reading
   - ✅ Enable Futures
   - ❌ Enable Withdrawals (NUNCA activar)
   - ❌ Enable Vanilla Options
4. **Restricción IP:** Añade la IP de tu VPS (obligatorio para seguridad)
5. Copia `API Key` y `API Secret` en `config_secrets.json`

### 6.2 Bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Envía `/newbot` y sigue las instrucciones
3. Copia el **token** que te proporciona
4. Para obtener tu `chat_id`:
   - Habla con [@userinfobot](https://t.me/userinfobot)
   - Te devolverá tu ID numérico
5. Configura ambos valores en `.env` y `config_secrets.json`

### 6.3 Modo Simulado vs Real

En `user_data/config.json`:

```json
{
    "dry_run": true,     // true = simulado (sin dinero real)
                         // false = REAL (usa dinero de Binance)
    "dry_run_wallet": 1000,  // Balance simulado en USDT
    "trading_mode": "futures",
    "margin_mode": "isolated"
}
```

> ⚠️ **IMPORTANTE:** Mantén `dry_run: true` hasta completar al menos 30 días de Forward-Testing satisfactorio.

---

## 7. Operación del Sistema

### 7.1 Comandos del Makefile

```bash
make help        # Muestra todos los comandos disponibles
make start       # Inicia todos los servicios en background
make stop        # Detiene todos los contenedores
make restart     # Reinicia la arquitectura completa
make logs        # Logs del bot principal (Freqtrade)
make nlp-logs    # Logs del motor de sentimiento (FinBERT)
make db-logs     # Logs de TimescaleDB
make backup      # Backup de la base de datos
make test        # Ejecuta los tests unitarios
make clean       # Limpia modelos obsoletos de la IA
```

### 7.2 Flujo de Operación Normal

```
1. make start              → Levanta los 6 servicios
2. make logs               → Verifica que el bot está operando
3. Abre http://<IP>:3000   → Dashboard Grafana
4. Abre http://<IP>:8081   → FreqUI (interfaz web del bot)
5. Telegram                → Recibes notificaciones de trades
```

### 7.3 Ciclo de Vida del Bot

El bot ejecuta un ciclo continuo cada 5 minutos:

1. **Descarga datos** OHLCV de Binance para los 11 pares
2. **Calcula 18+ indicadores** técnicos (RSI, MACD, BB, ATR, OBV...)
3. **Consulta TimescaleDB** para obtener sentimiento NLP y Fear & Greed
4. **LightGBM predice** el cambio de precio para las próximas 100 minutos
5. **Evalúa las 7 capas** de confluencia
6. Si hay señal → **calcula el tamaño** de posición (Kelly empírico 40%)
7. **Ejecuta la orden** en Binance
8. **Gestiona el riesgo** en tiempo real (ATR stop, trailing, Circuit Breaker)

---

## 8. Monitorización y Dashboards

### 8.1 FreqUI (Puerto 8081)

Interfaz web nativa de Freqtrade:
- Operaciones abiertas y cerradas
- Rendimiento acumulado
- Gráficos de precio con señales
- Control remoto (iniciar/parar bot)

**Acceso:** `http://<IP>:8081`
**Credenciales:** Las definidas en `.env` (`FREQTRADE_USERNAME` / `FREQTRADE_PASSWORD`)

### 8.2 Grafana (Puerto 3000)

Dashboard profesional conectado a TimescaleDB:
- Sentimiento NLP per-coin en tiempo real
- Fear & Greed Index histórico
- Métricas de rendimiento del bot
- Alertas configurables

**Acceso:** `http://<IP>:3000`
**Credenciales:** admin / `GF_SECURITY_ADMIN_PASSWORD`

### 8.3 Tensorboard (Puerto 6006)

Monitorización MLOps de los modelos LightGBM:
- Métricas de entrenamiento
- Evolución del loss
- Comparativa entre re-entrenamientos

**Acceso:** `http://<IP>:6006`

### 8.4 Telegram

Notificaciones automáticas de:
-  Apertura de operaciones (par, dirección, tamaño)
-  Cierre de operaciones (profit/loss)
-  Activación del Circuit Breaker
-  Resumen diario de rendimiento

---

## 9. Ejecución de Backtests

### 9.1 Backtest Simple

```bash
# Backtest de un periodo específico (ejemplo: Bull Market Abr-May 2025)
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --config user_data/config.json \
    --timerange 20250401-20250601 \
    --timeframe 5m
```

### 9.2 Backtest Multi-Escenario

```bash
# Bull Market
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --config user_data/config.json \
    --timerange 20250401-20250601

# Crash
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --config user_data/config.json \
    --timerange 20251001-20251201

# Bear Market
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --config user_data/config.json \
    --timerange 20250701-20251001

# Lateral
docker compose run --rm freqtrade backtesting \
    --strategy FreqaiExampleStrategy \
    --freqaimodel LightGBMRegressor \
    --config user_data/config.json \
    --timerange 20250801-20251001
```

### 9.3 Descarga de Datos Históricos

```bash
# Descargar datos antes de ejecutar backtests
docker compose run --rm freqtrade download-data \
    --config user_data/config.json \
    --timerange 20250101-20260401 \
    --timeframe 5m 1h
```

---

## 10. Tests Unitarios

### 10.1 Ejecutar Tests

```bash
# Desde la raíz del proyecto
make test

# O directamente:
export PYTHONPATH=./ && pytest tests/ -v
```

### 10.2 Tests Disponibles

| Test | Archivo | Qué Valida |
|------|---------|-----------|
| `test_kelly_empirico_sizing` | `tests/test_strategy.py` | Dimensionamiento Kelly 40% |
| `test_dynamic_atr_stoploss` | `tests/test_strategy.py` | Stop loss dinámico ATR |
| `test_html_cleaning` | `tests/test_nlp.py` | Limpieza HTML de titulares |
| `test_ner_detection` | `tests/test_nlp.py` | Detección de entidades (NER) |
| `test_rss_fallback` | `tests/test_nlp.py` | Fallback cuando RSS falla |

---

## 11. Mantenimiento y Troubleshooting

### 11.1 Problemas Comunes

**El bot no arranca:**
```bash
docker compose logs freqtrade | tail -50
# Causas comunes:
# - config_secrets.json no existe o tiene formato incorrecto
# - TimescaleDB no está ready (esperar healthcheck)
# - API keys de Binance inválidas o sin permisos de Futures
```

**El motor NLP no procesa noticias:**
```bash
docker compose logs sentiment_analysis | tail -50
# Causas comunes:
# - Sin conexión a internet (feeds RSS inaccesibles)
# - TimescaleDB no está ready
# - Primer inicio: FinBERT tarda ~2 min en descargarse
```

**TimescaleDB no arranca:**
```bash
docker compose logs timescaledb
# Solución: resetear el volumen
docker compose down -v  #  BORRA TODOS LOS DATOS
docker compose up -d
```

**Grafana no muestra datos:**
- Verifica que el datasource de PostgreSQL apunta a `timescaledb:5432`
- Usuario: `postgres`, Password: el de tu `.env`
- Base de datos: `freqtrade`

### 11.2 Backup y Restauración

```bash
# Crear backup
make backup
# Genera: backups/freqtrade_YYYYMMDD_HHMMSS.sql.gz

# Restaurar backup
gunzip -c backups/freqtrade_FECHA.sql.gz | \
  docker compose exec -T timescaledb psql -U postgres -d freqtrade
```

### 11.3 Actualización del Sistema

```bash
# Actualizar código
git pull origin master

# Reconstruir y reiniciar
docker compose up --build -d

# Limpiar modelos obsoletos si hay cambios en la estrategia
make clean && make restart
```

---

## 12. Estructura del Repositorio

```
TFG_Trading_Bot/
├── 📄 docker-compose.yml          # Orquestación de 6 microservicios
├── 📄 Dockerfile                  # Imagen del bot principal
├── 📄 Dockerfile.sentiment        # Imagen del motor NLP
├── 📄 Dockerfile.onchain          # Imagen del ingestor on-chain
├── 📄 Makefile                    # Comandos de operación
├── 📄 deploy_ubuntu.sh            # Script de despliegue automático
├── 📄 .env.example                # Plantilla de variables de entorno
├── 📄 requirements.txt            # Dependencias Python
├── 📄 README.md                   # Documentación principal
│
├── 📁 user_data/
│   ├── 📁 strategies/
│   │   └── FreqaiExampleStrategy.py  # ⭐ Estrategia principal (624 líneas)
│   ├── 📁 scripts/
│   │   ├── sentiment_ingestor.py     # Motor NLP FinBERT
│   │   └── onchain_ingestor.py       # Ingestor Fear & Greed
│   ├── 📄 config.json                # Configuración principal
│   └── 📄 config_secrets.json        # 🔒 Credenciales (NO en Git)
│
├── 📁 tests/
│   ├── test_strategy.py              # Tests de Kelly + ATR
│   └── test_nlp.py                   # Tests de NLP
│
├── 📁 grafana/
│   └── provisioning/                 # Configuración auto de Grafana
│
├── 📁 docs/
│   ├── 📁 memoria/
│   │   ├── memoria_tfg.md            # Memoria en Markdown
│   │   └── Memoria_TFG_Joan_Roma.docx # 📝 Memoria final Word
│   ├── GUIA_DESPLIEGUE_COMPLETA.md   # Esta guía
│   └── GUIA_USO_REAL.md              # Guía de operación con dinero real
│
└── 📁 archive/
    └── backtest_v*.txt               # Logs históricos de backtests
```

---

## Checklist de Despliegue

- [ ] Clonar repositorio
- [ ] Crear `.env` desde `.env.example`
- [ ] Crear `config_secrets.json` con API keys de Binance
- [ ] Ejecutar `./deploy_ubuntu.sh` (o `make start` en local)
- [ ] Verificar 6 contenedores con `docker compose ps`
- [ ] Acceder a Grafana (`http://<IP>:3000`)
- [ ] Acceder a FreqUI (`http://<IP>:8081`)
- [ ] Verificar logs del bot (`make logs`)
- [ ] Verificar notificaciones de Telegram
- [ ] Confirmar que `.env` y `config_secrets.json` están en `.gitignore`
- [ ] Confirmar que el firewall bloquea el puerto 5432
- [ ] Ejecutar tests unitarios (`make test`)

---

> **Autor:** Joan Romà Llorca — Universitat d'Alacant, Junio 2026
