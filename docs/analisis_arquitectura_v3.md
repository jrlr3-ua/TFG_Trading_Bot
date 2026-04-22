# 🤖 Análisis Arquitectónico y Estratégico - TFG Trading Bot (v3.0)
 
> **Autor:** Joan Romà Llorca (Universidad Politécnica de Valencia / Alicante)
> **Tipo de Documento:** Auditoría y Análisis del Código Base Actual
> **Versión Analizada:** 3.0 (Protocolo Institucional Multi-Timeframe)

---

## 1. 🏗️ Resumen Ejecutivo y Arquitectura del Sistema

El proyecto consiste en un **sistema de trading algorítmico de alta frecuencia (Scalping en 5m)** construido sobre la base del framework **Freqtrade**. A diferencia de los bots tradicionales que dependen únicamente de indicadores técnicos, este sistema emplea una **arquitectura híbrida de 7 capas**, integrando Inteligencia Artificial (Machine Learning), Procesamiento de Lenguaje Natural (NLP), Análisis On-Chain y flujos de órdenes (Order Flow).

El sistema está orquestado completamente en **Docker**, conformando una red de 6 microservicios esenciales:

1.  **freqtrade_elite_bot:** El bot principal (Bot 1). Ejecuta la lógica de `FreqaiExampleStrategy.py` conectándose a Binance Futures.
2.  **freqtrade_smc:** Bot experimental (Bot 2) basado en Smart Money Concepts (SMC).
3.  **sentiment_engine:** Microservicio NLP que escrapea noticias e infiere sentimientos usando **FinBERT**.
4.  **onchain_data:** Ingestor de datos macroeconómicos y On-Chain (Fear & Greed, BTC Dominance).
5.  **timescaledb:** Base de datos PostgreSQL optimizada para series temporales. Almacena las predicciones, métricas y los datos de la IA para consumo del bot.
6.  **grafana:** Capa de visualización de los datos.

## 2. 🧠 El Cerebro: `FreqaiExampleStrategy.py` (v3.0)

La estrategia principal no es una simple colección de indicadores; es un pipeline completo de *Machine Learning* y *Machine Learning Operations* (MLOps) de grado institucional.

### Modelo Predictivo (FreqAI)
-   **Algoritmo:** `LightGBMRegressor`.
-   **Target (Objetivo):** Predecir el porcentaje de cambio real en el precio (`&s-price_change`) para las próximas 20 velas. No clasifica sube/baja, sino que realiza una regresión lineal sobre el retorno.
-   **Entrenamiento:** Ventanas dinámicas (Sliding window) de 30 días, reentrenando automáticamente cada 2 horas con los datos más frescos.

### 2.1 Pipeline de Ingeniería de Características (Features)
El bot inyecta más de 18 características combinadas en el modelo LightGBM. La genialidad de esta versión es la inyección de **Multi-Timeframe Features (MTF)**:
-   **Momentum:** RSI, Stochastic RSI, MFI, MACD Histogram.
-   **Volatilidad y Volumen:** Bollinger Band Width, ATR Normalizado, OBV Normalizado.
-   **Variables Estacionales (Cíclicas):** Se usa la codificación seno/coseno (`hour_sin`, `hour_cos`, `day_sin`, `day_cos`) para ayudar al árbol de decisión a entender los ciclos diarios sin tratar al Lunes (0) como "inferior" al Domingo (6).
-   **Visión Cruzada H1/5m:** Ratio de precio 5m vs cierre H1, distancia del precio a la SMA 200 y EMA 50 horaria, permitiendo que el modelo comprenda su entorno micro (5 min) en contexto de la tendencia macro (1h).

### 2.2 Las 7 Capas de Confluencia (Lógica de Entrada)
Para ejecutar un trade, el sistema exige alineamiento institucional completo:
1.  **Macro (H1):** El precio debe estar sobre la SMA 200 para LONGs o por debajo para SHORTs.
2.  **Régimen:** El ADX en 1H > 20 asegura que el mercado está en tendencia, impidiendo compras en momentos laterales que rompen scalping algorítmicos.
3.  **Value Zone:** El precio debe estar cerca de la EMA50 en H1 (Threshold de distancia < 2.5%).
4.  **Aprobación IA:** La predicción de LightGBM debe superar un umbral paramétrico optimizado (`ai_threshold_long` y `short`).
5.  **Filtro NLP (Nuevo v3.0):** El sentimiento específico de la moneda debe ser `> -0.4` (evitando noticias bajistas).
6.  **Volumen:** Confirmación de participación de mercado (Volumen superior a la media de 50 periodos).
7.  **Order Flow:** Monitoreo (aunque no bloqueante) del desequilibrio de las pujas en la profundidad del mercado (Order Book Imbalance).

## 3. 🛡️ Capa de Protección y Gestión de Riesgo Patrimonial

1.  **Risk Management Agresivo pero Seguro:** El apalancamiento (`leverage`) está seteado a `x10` en Isolated Futures Margin.
2.  **Stop Loss Dinámico por ATR:** Se escapa de un número estricto. El SL muta usando el ATR (Average True Range). `(-2 * ATR / Precio)`. Si el mercado se vuelve salvaje, el bot amplía el Stop Loss (hasta máx -3%), para evitar ser liquidado por simples mechas (liquidity grabs).
3.  **Dimensionamiento de Posición (Criterio Kelly Modificado):** El bot inyecta dinámicamente más capital en señales con alta confianza de predicción (llegando a invertir hasta el 40% del wallet, un "Half-Kelly") y el tamaño mínimo para señales más dudables.
4.  **Circuit Breaker (Cortocircuito):** Implementación de seguridad pre-entrada. Si en el día en curso las pérdidas superan el `-10%`, el bot bloquea instantáneamente todas las ejecuciones de entrada para proteger el sistema de eventos de Cisne Negro.
5.  **Filtro On-Chain de Sentimiento Extremo:** Evita buscar "Shorts" si el mercado está en pánico extremo (Fear < 15) o "Longs" si hay extrema euforia (Greed > 85), entendiendo las roturas institucionales de mercado.

## 4. 📰 Microservicio NLP e Ingesta de Datos (`sentiment_ingestor.py`)

Aislado del entorno de Freqtrade, este microservicio mantiene un cronjob corriendo cada 5 minutos:
1.  **Ingesta:** Escrapea RSS de noticias de CoinDesk, CoinTelegraph y Bitcoin.com.
2.  **NER (Named Entity Recognition):** Usa expresiones regulares y matching (`COIN_ALIASES`) para asociar una noticia al ticker concreto afectado (ej: "Vitalik" mapea a `ETH`).
3.  **Clasificación Sentimental:** Envía el título a `ProsusAI/finbert` de HuggingFace, capturando el score.
4.  **Almacenamiento Per-Coin:** Almacena en `timescaledb` bajo la tabla hiper-optimizada `coin_sentiment`.

*El bot de trading consulta esta base de datos local pre-calculada antes de cada vela de 5 minutos, garantizando no añadir latencia a las reglas de operaciones en real-time.*

## 5. 📉 Bot Aleatorio/Experimental: Freqtrade SMC (`SMC_Scalping_TFG.py`)

Se diseñó estratégicamente una alternativa basada en **SMC (Smart Money Concepts)**:
-   A nivel de features, se entrena a la IA para aprender ineficiencias del mercado, proveyendo un cálculo explícito de los **FVG (Fair Value Gaps)** y del *width* de Bollinger.
-   El sistema tiene un disparador *híbrido paralelo* (Entra si la IA lo ordena **O** si hay una señal táctica humana basada en un pullback al FVG con confirmación de EMA 200). Se aprovecha la característica `enter_tag` para documentar la toma de decisiones.

## 6. 🚀 Tareas y Futuro del Proyecto

Tal como detalla el archivo de contexto del TFG, los pasos previstos actualmente son:
-   **Migración a Producción 24/7:** Sacar de `dry_run` y aprovisionar en un VPS robusto (Contabo/Hetzner).
-   **Auditoría sobre Rendimiento:** Evaluar si el sistema termina saliendo con más frecuencia por el umbral Stop Loss vs la recolección normal del ROI Positivo y Trailing Take Profit configurado en `config.json`.
-   **Refinamiento LightGBM:** Posibilidad de testear el Feature Importance obtenido internamente de FreqAI para eliminar features de ruido y refinar el modelo ML para entornos de alta volatilidad.
 
---
*Generado para auditoría en preparación de la defensa del Trabajo de Fin de Grado Universitario.*
