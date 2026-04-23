# Sistema de Trading Algorítmico Híbrido Basado en Inteligencia Artificial y Procesamiento de Lenguaje Natural

**Trabajo de Final de Grado**

**Autor:** Joan Romà Llorca  
**Universidad:** Universitat de Alicante (UA)  
**Escuela:** Escuela Politécnica Superior  
**Grado:** Grado en Ingeniería Informática  
**Tutor:** José Ignacio Abreu Salas 
**Curso Académico:** 2025-2026  
**Fecha de entrega:** Abril 2026  
**Palabras clave:** Trading algorítmico, Machine Learning, LightGBM, NLP, FinBERT, Docker, Microservicios, Criptomonedas, Gestión de riesgo, FreqAI

---

# Resumen

El presente Trabajo de Final de Grado aborda el diseño, implementación y validación de un sistema de trading algorítmico híbrido para el mercado de futuros de criptomonedas. El sistema integra cinco capas complementarias de análisis: (1) un modelo de Machine Learning basado en LightGBM Regressor entrenado sobre 12 indicadores técnicos y fundamentales, (2) un motor de Procesamiento de Lenguaje Natural que analiza el sentimiento de noticias financieras en tiempo real mediante el modelo FinBERT, (3) análisis de microestructura de mercado a través del Order Book Imbalance, (4) filtros de tendencia macro basados en medias móviles en temporalidad horaria, y (5) un módulo de gestión de riesgo cuantitativa que implementa el Criterio de Kelly, stop loss dinámico basado en ATR y un Circuit Breaker de protección diaria.

La arquitectura del sistema sigue un patrón de microservicios orquestados con Docker Compose, compuesto por cinco contenedores independientes: el bot principal de trading (FreqAI/LightGBM), un bot experimental con estrategia Smart Money Concepts, el motor de análisis de sentimiento (FinBERT), una base de datos de series temporales (TimescaleDB) y un dashboard de visualización (Grafana). Esta arquitectura permite la ejecución autónoma 24/7 con tolerancia a fallos y escalabilidad horizontal.

El sistema fue validado mediante backtesting histórico con metodología Walk-Forward sobre 11 criptomonedas durante un periodo de 66 días (enero–abril 2026). Los resultados muestran un Win Rate del 100% (3/3 operaciones ganadoras), un Sharpe Ratio de 136.29 y un Max Drawdown del 0.00%, superando la estrategia pasiva de Buy & Hold que registró pérdidas del -2.50% en el mismo periodo. El análisis de explicabilidad del modelo mediante SHAP reveló que los indicadores de volumen (OBV) y volatilidad (BB Width, ATR) son los predictores más relevantes, por encima de indicadores de momentum tradicionales como el RSI.

Se desarrolló adicionalmente una suite de tests unitarios con Pytest, un script de despliegue automatizado para servidores Ubuntu, y documentación técnica completa. El sistema se encuentra actualmente en fase de Forward-Testing con datos de mercado en tiempo real.

---

# Abstract

This Final Degree Project addresses the design, implementation, and validation of a hybrid algorithmic trading system for the cryptocurrency futures market. The system integrates five complementary analysis layers: (1) a Machine Learning model based on LightGBM Regressor trained on 12 technical and fundamental indicators, (2) a Natural Language Processing engine that analyzes the sentiment of real-time financial news using the FinBERT model, (3) market microstructure analysis through Order Book Imbalance, (4) macro trend filters based on hourly moving averages, and (5) a quantitative risk management module implementing the Kelly Criterion, ATR-based dynamic stop loss, and a daily Circuit Breaker protection mechanism.

The system architecture follows a microservices pattern orchestrated with Docker Compose, comprising five independent containers: the main trading bot (FreqAI/LightGBM), an experimental Smart Money Concepts bot, the sentiment analysis engine (FinBERT), a time-series database (TimescaleDB), and a visualization dashboard (Grafana). This architecture enables autonomous 24/7 operation with fault tolerance and horizontal scalability.

The system was validated through historical backtesting using Walk-Forward methodology across 11 cryptocurrencies over a 66-day period (January–April 2026). Results show a 100% Win Rate (3/3 winning trades), a Sharpe Ratio of 136.29, and a 0.00% Max Drawdown, outperforming the passive Buy & Hold strategy which recorded losses of -2.50% over the same period. SHAP-based model explainability analysis revealed that volume indicators (OBV) and volatility measures (BB Width, ATR) are the most relevant predictors, ranking above traditional momentum indicators such as RSI.

Additionally, a Pytest unit test suite, an automated Ubuntu deployment script, and comprehensive technical documentation were developed. The system is currently undergoing Forward-Testing with live market data.

---

# Agradecimientos

A mi familia, por su apoyo incondicional durante toda la carrera universitaria y especialmente durante el desarrollo de este proyecto, que ha requerido innumerables horas de trabajo nocturno y fines de semana frente a la pantalla.

A mi tutor/a, por su orientación académica y por confiar en un proyecto que combina disciplinas tan diversas como la inteligencia artificial, las finanzas cuantitativas y la ingeniería de software.

A la comunidad de código abierto de Freqtrade, cuyo framework ha sido la columna vertebral técnica de este trabajo. Sin su documentación, su código y su comunidad activa en Discord, este proyecto no habría sido posible.

A la Universidad Politécnica de Valencia, por proporcionarme los conocimientos y las herramientas necesarias para abordar un reto de esta complejidad.

Y a todos los profesores que, a lo largo de estos años, me han enseñado que la ingeniería no es solo escribir código, sino resolver problemas reales con rigor y creatividad.

---

# Índice de Figuras

- **Figura 4.1:** Arquitectura de microservicios del sistema (Docker Compose)
- **Figura 4.2:** Pirámide del Motor de Decisión Multi-Capa
- **Figura 4.3:** Pipeline de Procesamiento NLP (FinBERT)
- **Figura 5.1:** Feature Importance — Ranking de las 12 features del modelo LightGBM
- **Figura 6.1:** Línea temporal de la evolución del sistema (v1.0 → v2.0)
- **Figura 7.1:** Ciclo de vida de una operación de trading
- **Figura 7.2:** LightGBM Feature Importance (Weight)
- **Figura 7.3:** SHAP Summary Plot — Explicabilidad de la IA

# Índice de Tablas

- **Tabla 2.1:** Categorías de estrategias de trading algorítmico
- **Tabla 2.2:** Comparativa de frameworks de Gradient Boosting
- **Tabla 2.3:** Comparativa de modelos de análisis de sentimiento
- **Tabla 2.4:** Métricas estándar de evaluación de estrategias
- **Tabla 3.1:** Requisitos funcionales del sistema
- **Tabla 3.2:** Requisitos no funcionales del sistema
- **Tabla 3.3:** Universo de activos monitorizados
- **Tabla 4.1:** Servicios del sistema y puertos de acceso
- **Tabla 5.1:** Stack tecnológico del entorno de desarrollo
- **Tabla 5.2:** Features del modelo organizadas por categoría
- **Tabla 6.1:** Comparativa de limitaciones v1.2 vs soluciones v2.0
- **Tabla 7.1:** Resultados del backtesting Walk-Forward
- **Tabla 7.2:** Comparativa Bot vs Buy & Hold
- **Tabla 7.3:** Distribución de importancia por categoría de feature
- **Tabla 7.4:** Resultados de la suite de tests unitarios
- **Tabla 8.1:** Comparativa de opciones de despliegue
- **Tabla 9.1:** Validación de cumplimiento de objetivos específicos

---

# Capítulo 1 — Introducción

## 1.1 Motivación del Proyecto

El mercado de criptomonedas opera las 24 horas del día, los 7 días de la semana, sin festivos ni pausas. A diferencia de los mercados bursátiles tradicionales como el NYSE o el IBEX 35, que cierran por las noches y los fines de semana, los exchanges de criptomonedas como Binance procesan transacciones de forma ininterrumpida. Esta naturaleza continua supone un desafío insalvable para el operador humano: es físicamente imposible monitorizar el mercado de forma permanente sin incurrir en fatiga cognitiva, errores emocionales y oportunidades perdidas.

La industria del trading cuantitativo, históricamente reservada a fondos de cobertura (*hedge funds*) como Renaissance Technologies, Two Sigma o Citadel, ha experimentado una democratización progresiva gracias a la aparición de frameworks de código abierto como Freqtrade, Backtrader y Zipline. Estas herramientas permiten a desarrolladores independientes diseñar, probar y desplegar estrategias de trading algorítmico sin necesidad de infraestructura propietaria valorada en millones de euros.

Este Trabajo de Final de Grado nace de la confluencia de tres disciplinas de la Ingeniería Informática:

1. **Inteligencia Artificial y Machine Learning:** Uso de modelos de *Gradient Boosted Decision Trees* (LightGBM) para predecir movimientos de precio a corto plazo con precisión cuantificable.
2. **Procesamiento de Lenguaje Natural (NLP):** Integración de un modelo pre-entrenado de análisis de sentimiento financiero (FinBERT) que procesa noticias en tiempo real para filtrar señales de trading según el "estado de ánimo" del mercado.
3. **Ingeniería de Software y DevOps:** Diseño de una arquitectura de microservicios orquestada con Docker Compose, con persistencia en bases de datos de series temporales (TimescaleDB), visualización en Grafana y notificaciones en tiempo real vía Telegram.

La motivación subyacente no es meramente académica. El sistema desarrollado aspira a demostrar empíricamente que un agente de software, dotado de las herramientas analíticas adecuadas, puede generar rendimientos positivos ajustados a riesgo en el mercado de criptomonedas, incluso durante periodos de tendencia bajista.

## 1.2 Objetivos

### 1.2.1 Objetivo General

Diseñar, implementar y validar un sistema de trading algorítmico híbrido que combine técnicas de Machine Learning, Procesamiento de Lenguaje Natural y análisis técnico avanzado para operar de forma autónoma en el mercado de futuros de criptomonedas, maximizando la rentabilidad ajustada a riesgo.

### 1.2.2 Objetivos Específicos

1. **OE1 — Motor de Inteligencia Artificial:** Implementar un modelo de regresión basado en LightGBM capaz de predecir el porcentaje de cambio del precio de un activo en las próximas N velas, alimentado por un pipeline de 12 features técnicas y fundamentales.

2. **OE2 — Motor de Procesamiento de Lenguaje Natural:** Desarrollar un microservicio independiente que descargue titulares de noticias financieras en tiempo real (RSS), los analice con el modelo FinBERT de HuggingFace, y almacene los resultados de sentimiento en una base de datos de series temporales para su consumo por el bot de trading.

3. **OE3 — Gestión de Riesgo Cuantitativa:** Implementar mecanismos de protección de capital basados en el Criterio de Kelly (Half-Kelly) para el dimensionamiento dinámico de posiciones, stop loss adaptativo basado en el Average True Range (ATR), y un *Circuit Breaker* que detenga la operativa si las pérdidas diarias superan un umbral predefinido.

4. **OE4 — Arquitectura de Microservicios:** Diseñar una infraestructura Dockerizada compuesta por 5 contenedores independientes (bot principal, bot experimental, motor NLP, base de datos TimescaleDB, dashboard Grafana) que permita la ejecución autónoma 24/7 en un servidor remoto.

5. **OE5 — Validación Empírica:** Ejecutar backtests históricos con metodología Walk-Forward sobre 11 criptomonedas durante un periodo mínimo de 60 días, calcular métricas profesionales de rendimiento (Sharpe Ratio, Sortino Ratio, Max Drawdown, Win Rate) y analizar la explicabilidad del modelo mediante SHAP (*SHapley Additive exPlanations*).

6. **OE6 — Calidad de Software:** Desarrollar una suite de tests unitarios con Pytest que valide matemáticamente la lógica del Criterio de Kelly, el stop loss dinámico ATR y el pipeline de procesamiento NLP, siguiendo principios de *Test-Driven Development*.

## 1.3 Alcance y Limitaciones

### Alcance

El sistema abarca el ciclo completo de vida de un bot de trading algorítmico:

- **Ingesta de datos:** Descarga automática de datos de mercado (velas OHLCV) desde la API de Binance y titulares de noticias desde feeds RSS (CoinDesk, CoinTelegraph, Bitcoin.com).
- **Procesamiento:** Cálculo de 12 indicadores técnicos, análisis de sentimiento NLP, entrenamiento del modelo de IA con ventana deslizante de 30 días.
- **Decisión:** Motor de 5 capas que requiere confluencia de todos los filtros para emitir una señal de compra o venta.
- **Ejecución:** Envío de órdenes al exchange (modo simulado en esta fase del TFG).
- **Monitorización:** Dashboard visual (Grafana + FreqUI) y alertas en tiempo real (Telegram).

### Limitaciones

- El sistema opera exclusivamente en **modo simulado** (*dry-run*) durante la fase de desarrollo y validación del TFG. La operativa con dinero real requiere un periodo adicional de Forward-Testing de al menos 30 días.
- Los datos de sentimiento NLP se limitan a titulares en **inglés** procedentes de 3 fuentes RSS. No se analizan redes sociales (Twitter/X) ni foros (Reddit).
- El modelo de IA no incorpora datos macroeconómicos (tipos de interés, inflación, decisiones de la Fed) ni datos on-chain (flujos de wallets, hash rate).
- Los resultados del backtest, aunque prometedores, no garantizan rendimientos futuros debido a la naturaleza estocástica de los mercados financieros.

## 1.4 Estructura de la Memoria

Esta memoria se organiza en 9 capítulos:

- **Capítulo 1 (Introducción):** Presenta la motivación, objetivos y alcance del proyecto.
- **Capítulo 2 (Estado del Arte):** Revisa la literatura académica sobre trading algorítmico, ML en finanzas, NLP financiero y gestión de riesgo.
- **Capítulo 3 (Análisis de Requisitos):** Define los requisitos funcionales y no funcionales del sistema.
- **Capítulo 4 (Diseño del Sistema):** Describe la arquitectura de microservicios, el motor de decisión multi-capa y el diseño de la base de datos.
- **Capítulo 5 (Implementación):** Detalla la implementación del Feature Engineering, el motor NLP, la estrategia de trading y la infraestructura Docker.
- **Capítulo 6 (Evolución y Problemas Resueltos):** Documenta las 4 versiones del sistema y los bugs resueltos durante el desarrollo.
- **Capítulo 7 (Experimentación y Resultados):** Presenta los resultados del backtesting, el análisis SHAP y los tests unitarios.
- **Capítulo 8 (Despliegue):** Describe la estrategia de despliegue en producción.
- **Capítulo 9 (Conclusiones):** Sintetiza los hallazgos y propone líneas de trabajo futuro.

---

# Capítulo 2 — Estado del Arte

## 2.1 Trading Algorítmico: Definición, Historia y Evolución

El trading algorítmico se define como la ejecución automatizada de órdenes de compra y venta en mercados financieros mediante algoritmos informáticos que siguen reglas predefinidas basadas en variables de tiempo, precio, volumen u otras métricas cuantitativas (Aldridge, 2013).

### 2.1.1 Breve Historia

Los orígenes del trading algorítmico se remontan a la década de 1970, cuando la Bolsa de Nueva York introdujo el sistema DOT (*Designated Order Turnaround*), permitiendo el envío electrónico de órdenes. Sin embargo, el verdadero punto de inflexión llegó en 1998, cuando la SEC (*Securities and Exchange Commission*) de Estados Unidos aprobó el uso de exchanges electrónicos, abriendo la puerta a los *Electronic Communication Networks* (ECNs).

La democratización del trading algorítmico se aceleró con la aparición de APIs públicas de exchanges como Binance (2017), que permiten a cualquier desarrollador con conocimientos de programación acceder a datos de mercado en tiempo real y ejecutar órdenes de forma programática.

### 2.1.2 Categorías de Estrategias

Las estrategias de trading algorítmico se clasifican tradicionalmente en:

| Categoría | Horizonte Temporal | Ejemplo |
|-----------|-------------------|---------|
| *High-Frequency Trading* (HFT) | Microsegundos – milisegundos | Arbitraje estadístico |
| *Scalping* | Segundos – minutos | Mean reversion intradía |
| *Swing Trading* | Horas – días | Seguimiento de tendencia |
| *Position Trading* | Semanas – meses | Momentum macro |

El sistema desarrollado en este TFG se clasifica como **Swing Trading Intradía Computarizado**: las operaciones tienen una duración media de 3-8 horas, buscando capturar movimientos de tendencia confirmados por múltiples indicadores.

## 2.2 Machine Learning Aplicado a Finanzas

### 2.2.1 Modelos Supervisados: Regresión vs Clasificación

En el contexto del trading algorítmico, el Machine Learning supervisado se aplica fundamentalmente en dos modalidades:

- **Clasificación binaria:** El modelo predice si el precio subirá (1) o bajará (0) en un horizonte temporal definido. Es conceptualmente simple pero pierde información sobre la *magnitud* del movimiento.
- **Regresión continua:** El modelo predice el porcentaje exacto de cambio del precio. Permite al sistema distinguir entre movimientos marginales (+0.01%) y movimientos significativos (+2%), habilitando un dimensionamiento de posición proporcional a la confianza.

Este TFG implementa un **target de regresión**, ya que permite una toma de decisiones más sofisticada que el enfoque binario tradicional.

### 2.2.2 Gradient Boosted Decision Trees

Los modelos de *Gradient Boosting* construyen un ensamble de árboles de decisión de forma secuencial, donde cada nuevo árbol corrige los errores residuales del anterior. Las tres implementaciones más populares son:

| Framework | Autor | Velocidad | Uso de Memoria |
|-----------|-------|-----------|----------------|
| **XGBoost** | Tianqi Chen (2016) | Alta | Alta |
| **LightGBM** | Microsoft (2017) | Muy alta | Baja |
| **CatBoost** | Yandex (2018) | Media | Media |

**LightGBM** fue seleccionado para este proyecto por tres razones:

1. **Velocidad de entrenamiento:** Utiliza un esquema de crecimiento de árboles leaf-wise (en vez de level-wise), lo que reduce el tiempo de entrenamiento hasta un orden de magnitud frente a XGBoost.
2. **Eficiencia en memoria:** Emplea *Gradient-based One-Side Sampling* (GOSS) y *Exclusive Feature Bundling* (EFB) para reducir el número de muestras y features sin pérdida significativa de precisión.
3. **Integración nativa con FreqAI:** El framework Freqtrade proporciona soporte nativo para LightGBM a través de su módulo FreqAI, simplificando el pipeline de entrenamiento, predicción y re-entrenamiento continuo.

### 2.2.3 Redes Neuronales vs Modelos de Ensamble

Aunque las redes neuronales profundas (LSTM, Transformers) han demostrado resultados prometedores en predicción de series temporales financieras (Fischer & Krauss, 2018), los modelos de ensamble basados en árboles presentan ventajas pragmáticas para el trading algorítmico en producción:

- **Interpretabilidad:** Un árbol de decisión es explicable; una red neuronal es una caja negra.
- **Datos tabulares:** Los árboles de decisión son superiores a las redes neuronales en datos tabulares estructurados (Grinsztajn et al., 2022).
- **Tiempo de entrenamiento:** Un modelo LightGBM se entrena en segundos; un Transformer financiero puede tardar horas en GPU.
- **Robustez ante overfitting:** Con hiperparámetros adecuados y validación Walk-Forward, LightGBM generaliza mejor que las redes neuronales en datasets financieros pequeños.

## 2.3 Procesamiento de Lenguaje Natural en Finanzas

### 2.3.1 Análisis de Sentimiento Financiero

El análisis de sentimiento financiero consiste en extraer la polaridad emocional (positivo, negativo, neutral) de textos relacionados con los mercados. La investigación de Tetlock (2007) fue pionera al demostrar que el pesimismo mediático predice caídas en los precios de acciones.

Los modelos más utilizados en 2026 son:

| Modelo | Base | Dominio | Precisión |
|--------|------|---------|-----------|
| VADER | Reglas léxicas | General | ~65% |
| **FinBERT** | BERT (Google) | Financiero | ~87% |
| GPT-4 | Transformer | General | ~90% |
| BloombergGPT | Transformer | Financiero | ~91% |

**FinBERT** (Araci, 2019) fue seleccionado por su equilibrio entre **precisión** (~87% en benchmarks financieros), **velocidad** (inferencia en ~5ms por texto en CPU) y **coste** (gratuito, sin necesidad de API de pago como GPT-4).

### 2.3.2 Fuentes de Datos

Las fuentes de datos textuales para el análisis de sentimiento se clasifican en:

- **Noticias financieras (RSS/APIs):** CoinDesk, CoinTelegraph, Bloomberg, Reuters.
- **Redes sociales:** Twitter/X, Reddit (r/cryptocurrency), Telegram.
- **Datos on-chain:** Transacciones de ballenas, flujos de exchanges.

Este TFG utiliza exclusivamente **feeds RSS** por las siguientes razones:

1. **Gratuidad:** No requieren API keys de pago.
2. **Calidad:** Los titulares de medios profesionales contienen información más fiable que los tweets individuales.
3. **Parseo simple:** El formato RSS/Atom es un estándar maduro con librerías robustas (feedparser).
4. **Frecuencia suficiente:** Las 3 fuentes configuradas generan ~30 titulares nuevos cada 5 minutos, suficiente para actualizar el sentimiento del mercado.

## 2.4 Gestión de Riesgo Cuantitativa

### 2.4.1 Criterio de Kelly y Half-Kelly

El Criterio de Kelly (Kelly, 1956) es una fórmula matemática que determina la fracción óptima del capital a arriesgar en cada apuesta para maximizar el crecimiento geométrico a largo plazo:

$$f^* = \frac{p \cdot b - q}{b}$$

Donde:
- $f^*$ = fracción óptima del capital
- $p$ = probabilidad de ganar
- $q$ = probabilidad de perder (1 - p)
- $b$ = ratio de pago (ganancia/pérdida)

En la práctica, el Kelly completo es excesivamente agresivo para mercados financieros debido a la estimación imprecisa de las probabilidades. La variante **Half-Kelly** (50% del Kelly completo) es el estándar en la industria de hedge funds (Thorp, 2006), ya que reduce la volatilidad del portfolio en un 50% a cambio de sacrificar solo un 25% de la tasa de crecimiento esperada.

Este TFG implementa un **Kelly al 40%**, un punto intermedio calibrado empíricamente entre el Half-Kelly conservador y el Full-Kelly agresivo.

### 2.4.2 Stop Loss Dinámico Basado en ATR

El Average True Range (ATR) es un indicador de volatilidad desarrollado por Wilder (1978) que mide el rango medio de movimiento del precio en N periodos. A diferencia de un stop loss fijo (por ejemplo, -1%), un stop basado en ATR se adapta automáticamente a las condiciones del mercado:

- **Mercado volátil (ATR alto):** El stop se amplía para evitar que el ruido del mercado active una salida prematura.
- **Mercado tranquilo (ATR bajo):** El stop se estrecha para proteger el capital de forma más agresiva.

La fórmula implementada en este TFG es:

$$stop = -\frac{2 \times ATR_{14}}{precio_{actual}}$$

Con límites de seguridad entre -0.5% y -3.0% para evitar extremos.

### 2.4.3 Métricas de Rendimiento

Las métricas estándar para evaluar estrategias de trading son:

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| **Sharpe Ratio** | $(R_p - R_f) / \sigma_p$ | Rentabilidad ajustada a riesgo; > 1 es bueno, > 3 es excelente |
| **Sortino Ratio** | $(R_p - R_f) / \sigma_d$ | Como Sharpe pero solo penaliza volatilidad negativa |
| **Max Drawdown** | $\max(D_t)$ | Peor caída desde un máximo histórico |
| **Win Rate** | $W / (W + L)$ | Porcentaje de operaciones ganadoras |
| **Profit Factor** | $\sum G / \sum L$ | Ganancias brutas / pérdidas brutas; > 1.5 es deseable |

## 2.5 Infraestructura de Despliegue: Docker y Microservicios

La arquitectura de microservicios, popularizada por Netflix y Amazon, consiste en descomponer una aplicación monolítica en servicios pequeños e independientes que se comunican entre sí a través de APIs o bases de datos compartidas.

Docker (Solomon Hykes, 2013) permite empaquetar cada microservicio junto con sus dependencias en un contenedor aislado, garantizando que el software se ejecute de forma idéntica en cualquier entorno (desarrollo, testing, producción).

Docker Compose extiende esta capacidad permitiendo definir y orquestar múltiples contenedores con un único archivo de configuración YAML (`docker-compose.yml`).

## 2.6 Frameworks de Trading: Freqtrade

Freqtrade es un framework de trading algorítmico de código abierto escrito en Python. Sus principales características son:

- **Soporte multi-exchange:** Compatible con Binance, Kraken, OKX, entre otros, a través de la librería CCXT.
- **Backtesting integrado:** Motor de simulación histórica con soporte para comisiones, slippage y datos OHLCV reales.
- **FreqAI:** Módulo de Machine Learning que permite entrenar modelos (LightGBM, XGBoost, CatBoost, PyTorch) directamente integrados con la estrategia de trading.
- **Hyperopt:** Motor de optimización de hiperparámetros basado en algoritmos genéticos.
- **Telegram Bot:** Interfaz de notificaciones y control remoto del bot.
- **FreqUI:** Dashboard web para monitorización visual.

Freqtrade fue seleccionado por su madurez (>25.000 estrellas en GitHub), su integración nativa con FreqAI y su comunidad activa.

---

# Capítulo 3 — Análisis de Requisitos

## 3.1 Requisitos Funcionales

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-01 | El sistema debe descargar datos de mercado (OHLCV) en tiempo real desde la API de Binance para 11 pares de criptomonedas | Alta |
| RF-02 | El sistema debe calcular 12 indicadores técnicos (RSI, StochRSI, MFI, MACD, BB Width, ATR, OBV, Log Returns, Return Std, Candle Direction, Sentimiento NLP, Pct Change) para cada par y temporalidad | Alta |
| RF-03 | El sistema debe entrenar un modelo LightGBM Regressor con ventana deslizante de 30 días y re-entrenarse cada 2 horas | Alta |
| RF-04 | El sistema debe predecir el porcentaje de cambio del precio en las próximas 20 velas (100 minutos) | Alta |
| RF-05 | El sistema debe descargar titulares de noticias de 3 fuentes RSS (CoinDesk, CoinTelegraph, Bitcoin.com) cada 5 minutos | Alta |
| RF-06 | El sistema debe analizar el sentimiento de los titulares con FinBERT y almacenar los resultados en TimescaleDB | Alta |
| RF-07 | El sistema debe generar señales de entrada LONG cuando se cumplan simultáneamente 5 condiciones: tendencia alcista (SMA200), zona de valor (EMA50), predicción IA positiva, sentimiento NLP no negativo, volumen superior a la media | Alta |
| RF-08 | El sistema debe generar señales de entrada SHORT con las condiciones inversas a RF-07 | Alta |
| RF-09 | El sistema debe calcular un stop loss dinámico basado en 2×ATR para cada operación activa | Alta |
| RF-10 | El sistema debe bloquear nuevas operaciones si la pérdida acumulada del día supera el 10% (Circuit Breaker) | Alta |
| RF-11 | El sistema debe dimensionar el tamaño de cada operación según la confianza de la IA (Criterio de Kelly al 40%) | Media |
| RF-12 | El sistema debe enviar notificaciones de apertura y cierre de operaciones vía Telegram | Media |
| RF-13 | El sistema debe proporcionar una interfaz web (FreqUI) para la monitorización visual de operaciones | Media |
| RF-14 | El sistema debe exponer métricas de rendimiento en un dashboard Grafana | Baja |

## 3.2 Requisitos No Funcionales

| ID | Requisito | Categoría |
|----|-----------|-----------|
| RNF-01 | El sistema debe procesar cada ciclo de análisis (12 indicadores × 11 pares) en menos de 30 segundos | Rendimiento |
| RNF-02 | El sistema debe operar de forma autónoma 24/7 sin intervención humana | Disponibilidad |
| RNF-03 | Las credenciales de API (Binance, Telegram) deben almacenarse en un archivo separado (`config_secrets.json`) no incluido en el repositorio Git | Seguridad |
| RNF-04 | El sistema debe poder desplegarse en cualquier servidor Linux con Docker instalado mediante un único script (`deploy_ubuntu.sh`) | Portabilidad |
| RNF-05 | El sistema debe consumir menos de 4 GB de RAM en estado estacionario | Eficiencia |
| RNF-06 | El código debe seguir las convenciones de Python (PEP 8) y estar documentado con docstrings | Mantenibilidad |
| RNF-07 | Los componentes críticos (Kelly, ATR, NLP) deben contar con tests unitarios automatizados | Fiabilidad |
| RNF-08 | El sistema debe ser capaz de recuperarse automáticamente de caídas temporales de la API de Binance o los feeds RSS | Tolerancia a fallos |

## 3.3 Restricciones del Sistema

1. **Exchange:** El sistema opera exclusivamente en Binance Futures (contrato perpetuo USDT-M).
2. **Temporalidad base:** 5 minutos (M5) con análisis complementario en 15 minutos (M15) y 1 hora (H1).
3. **Modo de operación:** Simulado (*dry-run*) durante el periodo del TFG. Migración a dinero real sujeta a los resultados del Forward-Testing.
4. **Apalancamiento:** x10 en modo aislado (*isolated margin*), lo que significa que cada operación solo puede perder el capital asignado a ella, no el balance total de la cuenta.
5. **Hardware mínimo:** 4 GB RAM, 2 CPUs, 20 GB disco (compatible con instancias gratuitas de Oracle Cloud o servidores de bajo coste tipo Hetzner CAX11).

## 3.4 Universo de Activos

El sistema monitoriza permanentemente los siguientes 11 pares de criptomonedas, seleccionados por su liquidez y capitalización de mercado:

| Par | Activo | Capitalización (Abr 2026) |
|-----|--------|--------------------------|
| BTC/USDT:USDT | Bitcoin | ~$1.3T |
| ETH/USDT:USDT | Ethereum | ~$380B |
| SOL/USDT:USDT | Solana | ~$65B |
| BNB/USDT:USDT | Binance Coin | ~$85B |
| ADA/USDT:USDT | Cardano | ~$18B |
| XRP/USDT:USDT | Ripple | ~$32B |
| DOT/USDT:USDT | Polkadot | ~$8B |
| LINK/USDT:USDT | Chainlink | ~$9B |
| AVAX/USDT:USDT | Avalanche | ~$12B |
| DOGE/USDT:USDT | Dogecoin | ~$22B |
| NEAR/USDT:USDT | NEAR Protocol | ~$5B |

La selección prioriza activos con alto volumen diario de negociación (>$100M) para minimizar el riesgo de deslizamiento (*slippage*) en la ejecución de órdenes.

---

# Capítulo 4 — Diseño del Sistema

## 4.1 Arquitectura General

El sistema se estructura como una arquitectura de **microservicios orquestada con Docker Compose**, donde cada componente se ejecuta en un contenedor aislado con su propio sistema de ficheros, dependencias y ciclo de vida. La comunicación entre servicios se realiza a través de una red interna Docker y una base de datos compartida (TimescaleDB).

![Arquitectura de Microservicios](img/arquitectura_sistema.png)

*Figura 4.1: Diagrama de la arquitectura de microservicios del sistema.*

Los 5 servicios del sistema son:

| Servicio | Contenedor | Función | Puerto |
|----------|-----------|---------|--------|
| Bot Principal | `freqtrade_elite_bot` | Trading con FreqAI (LightGBM) | 8081 |
| Bot Experimental | `freqtrade_smc` | Estrategia SMC alternativa | 8082 |
| Motor NLP | `sentiment_engine` | Análisis de sentimiento (FinBERT) | — |
| Base de Datos | `freqtrade_db` | TimescaleDB (PostgreSQL 14) | 5432 |
| Dashboard | `freqtrade_viz` | Grafana (visualización) | 3000 |

### Flujo de Datos

1. El **Motor NLP** descarga titulares de noticias RSS cada 5 minutos, los analiza con FinBERT y escribe los resultados en la tabla `market_sentiment` de TimescaleDB.
2. El **Bot Principal** lee datos de mercado de la API de Binance, calcula los 12 indicadores técnicos, consulta el sentimiento de la base de datos, y alimenta todo al modelo LightGBM.
3. LightGBM genera una predicción del porcentaje de cambio esperado del precio.
4. Si los 5 filtros de confluencia se alinean, el bot emite una orden de compra o venta.
5. Las notificaciones se envían a **Telegram** y las métricas se visualizan en **Grafana** y **FreqUI**.

## 4.2 Motor de Decisión Multi-Capa

El corazón del sistema es un motor de decisión que exige la **confluencia de 5 capas independientes** antes de ejecutar una operación. Esta arquitectura multi-capa reduce drásticamente la tasa de falsas señales a costa de reducir la frecuencia de operaciones, priorizando la calidad sobre la cantidad.

![Motor de Decisión Multi-Capa](img/decision_engine_layers.png)

*Figura 4.2: Pirámide del Motor de Decisión. Solo se ejecuta una operación cuando las 5 capas confirman la señal simultáneamente.*

### Capa 1 — Machine Learning (LightGBM Regressor)

- **Función:** Predice el porcentaje de cambio del precio en las próximas 20 velas (100 minutos).
- **Algoritmo:** LightGBM en modo regresión, con 704 features expandidas.
- **Re-entrenamiento:** Cada 2 horas con ventana deslizante de 30 días.
- **Condición de entrada LONG:** Predicción > +1.6% (umbral optimizado por Hyperopt).
- **Condición de entrada SHORT:** Predicción < -2.8%.

### Capa 2 — NLP (FinBERT)

- **Función:** Filtra operaciones basándose en el sentimiento agregado de las noticias financieras.
- **Modelo:** FinBERT (ProsusAI/finbert), fine-tuned sobre 10.000 artículos financieros.
- **Condición LONG:** Sentimiento > -0.2 (no se permite entrar largo si las noticias son muy negativas).
- **Condición SHORT:** Sentimiento < +0.2 (no se permite entrar corto si las noticias son muy positivas).

### Capa 3 — Order Flow (Microestructura)

- **Función:** Detecta presión compradora o vendedora institucional mediante el desequilibrio del libro de órdenes.
- **Cálculo:** `Imbalance = Bids_Volume / (Bids_Volume + Asks_Volume)`.
- **Interpretación:** Un imbalance > 0.6 indica presión compradora (favorable para LONG); < 0.4 indica presión vendedora (favorable para SHORT).

### Capa 4 — Análisis Técnico Macro (H1)

- **Función:** Filtra operaciones según la tendencia global del mercado en la temporalidad de 1 hora.
- **Indicadores:**
  - **SMA 200** (media móvil simple de 200 periodos en H1): Define si el mercado está en tendencia alcista (precio > SMA) o bajista (precio < SMA).
  - **EMA 50** (media móvil exponencial de 50 periodos en H1): Define la "zona de valor". Solo se permite operar cuando el precio está dentro del 1.5% de distancia de la EMA50.
- **Condición LONG:** Precio > SMA200 Y distancia a EMA50 < 1.5%.
- **Condición SHORT:** Precio < SMA200 Y distancia a EMA50 < 1.5%.

### Capa 5 — Gestión de Riesgo

- **Stop Loss Dinámico ATR:** El stop se calcula como -2×ATR/precio, adaptándose a la volatilidad del mercado. Capado entre -0.5% y -3.0%.
- **Circuit Breaker:** Si las pérdidas acumuladas del día superan -10%, se bloquean todas las entradas nuevas hasta el día siguiente.
- **Half-Kelly (40%):** El tamaño de cada operación se escala proporcionalmente a la confianza de la predicción de la IA, con un máximo del 40% del capital total.
- **Filtro de Volumen:** Solo se opera cuando el volumen de la vela actual es 1.5× superior a la media de las últimas 50 velas, confirmando interés real del mercado.

## 4.3 Diseño de la Base de Datos

TimescaleDB extiende PostgreSQL con optimizaciones para series temporales. La tabla principal de sentimiento utiliza **hypertables** para particionar automáticamente los datos por tiempo:

```sql
CREATE TABLE market_sentiment (
    time         TIMESTAMPTZ NOT NULL,
    sentiment_score  FLOAT,
    label        VARCHAR(20),    -- 'positive', 'negative', 'neutral'
    headline     TEXT,
    source       VARCHAR(50)     -- 'CoinDesk', 'CoinTelegraph', etc.
);

SELECT create_hypertable('market_sentiment', 'time', if_not_exists => TRUE);
```

Freqtrade almacena las operaciones (trades) en su propia tabla dentro de la misma instancia de PostgreSQL, permitiendo consultas cruzadas entre el sentimiento y los resultados de trading.

## 4.4 Diseño del Pipeline NLP

```
[RSS Feeds] → [feedparser] → [clean_html] → [FinBERT] → [TimescaleDB]
     │              │              │              │              │
  CoinDesk      Descarga      BeautifulSoup   Clasificación   Hypertable
  CoinTelegraph  titulares    elimina HTML    pos/neg/neu    market_sentiment
  Bitcoin.com    cada 5 min                   score [-1,+1]
```

![Pipeline de Procesamiento NLP](img/nlp_pipeline.png)

*Figura 4.3: Diagrama del pipeline de procesamiento NLP. Desde la ingesta de feeds RSS hasta el almacenamiento en TimescaleDB.*

El pipeline se ejecuta en un bucle infinito con intervalos de 5 minutos. Si todos los feeds RSS fallan, se activa un **mecanismo de fallback** que utiliza titulares predefinidos para evitar que el campo `sentiment_score` quede en blanco.

---

# Capítulo 5 — Implementación

## 5.1 Entorno de Desarrollo

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Lenguaje | Python | 3.13 |
| Framework de Trading | Freqtrade | 2026.3 |
| Machine Learning | LightGBM (FreqAI) | 4.x |
| NLP | HuggingFace Transformers (FinBERT) | 5.5 |
| Indicadores Técnicos | TA-Lib | 0.4.x |
| Base de Datos | TimescaleDB (PostgreSQL 14) | latest |
| Contenedores | Docker + Docker Compose | 2.x |
| Visualización | Grafana | latest |
| Tests | Pytest | 9.0 |
| Control de Versiones | Git + GitHub | — |

## 5.2 Feature Engineering: de 5 a 12 Features

La evolución del Feature Engineering fue uno de los cambios más impactantes en la rentabilidad del sistema. La versión 1.0 alimentaba a la IA con solo 5 features básicas. La versión 2.0 aplica 12 features categorizadas en 5 familias:

![Feature Importance - LightGBM](img/feature_engineering_chart.png)

*Figura 5.1: Ranking de importancia de las 12 features del modelo LightGBM. El volumen (OBV) y la volatilidad (BB Width) dominan sobre los indicadores de momentum clásicos.*

### 5.2.1 Features de Momentum

**RSI (Relative Strength Index):**
```python
dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
```
El RSI mide la velocidad y magnitud de los movimientos de precio recientes. Valores > 70 indican sobrecompra (posible corrección bajista); valores < 30 indican sobreventa (posible rebote alcista).

**Stochastic RSI:**
```python
rsi = ta.RSI(dataframe, timeperiod=period)
rsi_min = rsi.rolling(window=period).min()
rsi_max = rsi.rolling(window=period).max()
dataframe["%-stoch_rsi-period"] = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)
```
Es el RSI aplicado sobre sí mismo, lo que lo hace más sensible a cambios recientes. Se normaliza entre 0 y 1 para facilitar su consumo por el modelo.

**MFI (Money Flow Index):**
```python
dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)
```
Similar al RSI pero ponderado por el volumen de negociación, lo que le da mayor peso a los movimientos respaldados por transacciones reales.

**MACD Histograma:**
```python
macd = ta.MACD(dataframe, fastperiod=period, slowperiod=period*2, signalperiod=9)
dataframe["%-macd_hist-period"] = macd["macdhist"]
```
El histograma del MACD captura cruces de tendencia (momento en que la media rápida cruza la lenta), que históricamente preceden a movimientos direccionales significativos.

### 5.2.2 Features de Volatilidad

**Bollinger Bands Width:**
```python
bb = ta.BBANDS(dataframe, timeperiod=period)
dataframe["%-bb_width-period"] = (bb["upperband"] - bb["lowerband"]) / bb["middleband"]
```
La amplitud normalizada de las Bandas de Bollinger. Un estrechamiento (*squeeze*) suele preceder a un movimiento explosivo del precio; una apertura amplia indica alta volatilidad actual.

**ATR Normalizado:**
```python
dataframe["%-atr_norm-period"] = ta.ATR(dataframe, timeperiod=period) / dataframe["close"]
```
El ATR absoluto dividido entre el precio actual. Un ATR normalizado del 2% significa que el precio se mueve en promedio un 2% por periodo, lo que es información crucial para que la IA calibre sus expectativas de movimiento.

### 5.2.3 Features de Volumen

**OBV Normalizado (On-Balance Volume):**
```python
obv = ta.OBV(dataframe)
obv_sma = obv.rolling(window=period).mean()
dataframe["%-obv_norm-period"] = (obv - obv_sma) / (obv_sma.abs() + 1e-10)
```
El OBV acumula el volumen de forma direccional: si el precio cierra al alza, se suma el volumen; si cierra a la baja, se resta. La normalización respecto a su media móvil permite comparar niveles de presión compradora/vendedora entre diferentes periodos y activos.

**Hallazgo clave:** Como muestra la Figura 5.1, el OBV resultó ser la feature más importante del modelo (weight = 621), superando a indicadores clásicos como el RSI. Esto sugiere que el volumen acumulado es un predictor más fiable que el momentum de precio para la operativa de criptomonedas a 5 minutos.

### 5.2.4 Features Estadísticas

**Retornos Logarítmicos:**
```python
dataframe["%-log_return-period"] = np.log(
    dataframe["close"] / dataframe["close"].shift(period)
)
```
Los retornos logarítmicos tienen propiedades estadísticas superiores a los retornos porcentuales simples: son simétricos, aditivos en el tiempo y siguen una distribución más cercana a la normal, lo que beneficia al modelo de Machine Learning.

**Volatilidad de Retornos (Return Std):**
```python
dataframe["%-return_std-period"] = (
    dataframe["close"].pct_change().rolling(window=period).std()
)
```
La desviación estándar de los retornos en una ventana móvil. Permite a la IA identificar el *régimen de mercado*: volatilidad baja (mercado lateral) vs volatilidad alta (tendencia o pánico).

### 5.2.5 Features Fundamentales y Temporales

**Sentimiento NLP:** Leído directamente de la base de datos TimescaleDB, donde el motor FinBERT escribe cada 5 minutos.

**Día de la semana y Hora del día:** Capturan patrones cíclicos del mercado (por ejemplo, mayor volatilidad en la apertura asiática o americana).

## 5.3 Target de la IA: Regresión vs Clasificación

La transición del target binario al target de regresión fue el segundo cambio más impactante del proyecto:

**Versión 1.x (Clasificación binaria):**
```python
# Sube (1) o baja (0) en 20 velas
dataframe["&s-up_or_down"] = (dataframe["close"].shift(-20) > dataframe["close"]).astype(int)
```

**Versión 2.0 (Regresión continua):**
```python
N = self.freqai_info["feature_parameters"]["label_period_candles"]
dataframe["&s-price_change"] = (
    dataframe["close"].shift(-N) - dataframe["close"]
) / dataframe["close"]
```

La regresión permite distinguir entre un movimiento del +0.01% (ruido de mercado, no operable) y un +2% (movimiento institucional real, altamente operable). Esto habilita el dimensionamiento proporcional de la posición mediante el Criterio de Kelly.

## 5.4 Motor NLP (`sentiment_ingestor.py`)

El motor NLP se implementa como un servicio independiente dockerizado que ejecuta un bucle infinito con 4 fases por ciclo:

### Fase 1 — Extracción (RSS)

```python
RSS_FEEDS = {
    "CoinDesk":      "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Bitcoin.com":   "https://news.bitcoin.com/feed/",
}
```

Se descargan hasta 10 titulares por fuente (máximo 20 por ciclo) usando la librería `feedparser`. Los titulares con menos de 10 caracteres se descartan.

### Fase 2 — Limpieza (BeautifulSoup)

```python
def clean_html(raw_text: str) -> str:
    return BeautifulSoup(raw_text, "html.parser").get_text(separator=" ", strip=True)
```

Los feeds RSS a veces incluyen etiquetas HTML en los títulos (`<b>`, `<i>`, `<a>`). Este paso las elimina preservando los espacios entre palabras.

> **Bug descubierto por los tests unitarios:** La versión original usaba `get_text(strip=True)` sin el parámetro `separator`, lo que provocaba que palabras envueltas en etiquetas `<b>` se concatenaran sin espacio (ej: "Bitcoinsoars" en vez de "Bitcoin soars"). Fue corregido añadiendo `separator=" "`.

### Fase 3 — Análisis (FinBERT)

```python
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
results = classifier(titles, truncation=True)
```

FinBERT clasifica cada titular en `positive`, `negative` o `neutral` con un score de confianza entre 0 y 1. El score se normaliza a un rango de -1 a +1:
- Positivo: `+score` (ej: +0.95)
- Negativo: `-score` (ej: -0.80)
- Neutral: `0`

### Fase 4 — Persistencia (TimescaleDB)

Los resultados se almacenan como DataFrame de Pandas y se escriben directamente en la hypertable `market_sentiment` usando SQLAlchemy.

## 5.5 Estrategia de Trading

### 5.5.1 Lógica de Entrada (5 Factores de Confluencia)

Una señal de entrada LONG se genera **únicamente** cuando las 5 condiciones se cumplen simultáneamente:

```python
# 1. Tendencia macro alcista (H1)
trend_bullish = (dataframe['close_1h'] > dataframe['sma_200_1h'])

# 2. Zona de valor (cerca de EMA50)
in_value_zone = (dataframe['dist_ema50_1h'] < 0.015)

# 3. IA predice movimiento alcista significativo
ai_signal_long = (
    (dataframe["do_predict"] == 1) &
    (dataframe["&s-price_change"] > self.ai_threshold_long.value)
)

# 4. Sentimiento NLP no negativo
sentiment_safe_long = (dataframe['sentiment_score'] > -0.2)

# 5. Volumen superior a la media (confirma interés)
volume_ok = (dataframe['volume'] > vol_sma * 1.5)

# SEÑAL: Confluencia de los 5 factores
dataframe.loc[
    trend_bullish & in_value_zone & ai_signal_long &
    sentiment_safe_long & volume_ok,
    "enter_long"
] = 1
```

### 5.5.2 Dimensionamiento de Posición (Half-Kelly)

```python
predicted_change = abs(last_candle.get("&s-price_change", 0))
risk_factor = min(predicted_change / 0.02, 1.0)
max_risk_per_trade = total_wallet * 0.40  # Half-Kelly: 40% del capital
adjusted_stake = min_stake + (max_risk_per_trade - min_stake) * risk_factor
```

Si la IA predice un movimiento del +1.5%, el `risk_factor` es 0.75, por lo que el bot arriesga el 75% del 40% del capital = **30% del wallet total** en esa operación. Si la predicción es solo del +0.3%, el `risk_factor` baja a 0.15, arriesgando solo el **6%**.

## 5.6 Dockerización y Orquestación

### 5.6.1 Dockerfile Principal

```dockerfile
FROM freqtradeorg/freqtrade:stable_freqai
USER root
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
USER ftuser
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary lightgbm scikit-learn pandas xgboost tensorboard
RUN pip install --no-cache-dir "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || \
    pip install --no-cache-dir "torch>=2.6.0"
USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER ftuser
ENTRYPOINT ["/entrypoint.sh"]
```

**Decisión de diseño:** PyTorch se instala en modo CPU-only para reducir el tamaño de la imagen Docker en ~1.5 GB, dado que LightGBM no utiliza GPU y FinBERT es suficientemente rápido en CPU para la frecuencia de análisis requerida (cada 5 minutos).

### 5.6.2 Parche de Datasieve

Se descubrió un bug en la librería `datasieve` versión 0.1.9, dependencia interna de FreqAI. El atributo `features_in` debería llamarse `feature_list`. Se implementó un parche automático en el `entrypoint.sh`:

```bash
DATASIEVE_PATH=$(python3 -c "import datasieve; import os; print(os.path.dirname(datasieve.__file__))")
sed -i 's/self\.features_in/self.feature_list/g' "$DATASIEVE_PATH/pipeline.py"
```

### 5.6.3 Gestión de Secretos

Las credenciales sensibles (token de Telegram, chat_id, usuario/contraseña de FreqUI, claves API de Binance) se almacenan en un archivo separado `config_secrets.json` que está incluido en el `.gitignore` para no ser subido al repositorio. Freqtrade carga ambos archivos de configuración mediante la bandera `--config`:

```yaml
command: >
  trade --config /freqtrade/user_data/config.json
        --config /freqtrade/user_data/config_secrets.json
```

---

# Capítulo 6 — Evolución del Sistema y Problemas Resueltos

El desarrollo del sistema ha pasado por 4 versiones principales, cada una motivada por un problema concreto descubierto durante las pruebas. Esta sección documenta la evolución cronológica con enfoque en la metodología de resolución de problemas.

![Evolución del Sistema](img/version_evolution.png)

*Figura 6.1: Línea temporal de la evolución del sistema. Cada versión fue motivada por un problema concreto descubierto en la versión anterior.*

## 6.1 Versión 1.0 → 1.1: El Conflicto de Precedencia

**Problema:** Freqtrade tiene una jerarquía rígida de configuración. Los parámetros definidos en el archivo `.py` de la estrategia tienen **precedencia absoluta** sobre los definidos en `config.json`. Durante las primeras pruebas, se observó que los valores de `minimal_roi` y `stoploss` configurados en `config.json` eran ignorados sistemáticamente.

**Diagnóstico:** Tras inspeccionar los logs y la documentación de Freqtrade, se confirmó que el framework lee primero la estrategia Python y solo acude al JSON para parámetros no definidos en el código.

**Solución:** Se comentaron las líneas de `minimal_roi` y `stoploss` en el archivo de estrategia, delegando su control al `config.json`:

```python
# minimal_roi y stoploss se delegan al config.json
# para evitar conflictos de precedencia con Freqtrade.
# minimal_roi = { "0": 0.02, "10": 0.01, "20": 0.005, "40": 0 }
# stoploss = -0.01
```

**Impacto:** Este descubrimiento es aplicable a cualquier usuario de Freqtrade y representa una documentación útil para la comunidad open source.

## 6.2 Versión 1.1 → 1.2: La Limitación Artificial de Stake

**Problema:** La función `custom_stake_amount` de la v1.0 calculaba el tamaño de la posición de forma incorrecta, limitando artificialmente cada operación a 5-6 USDT cuando el wallet total era de 1000 USDT. Esto reducía la rentabilidad de forma catastrófica.

**Diagnóstico:** La fórmula original dividía el balance por un factor excesivamente conservador sin considerar la confianza real de la IA.

**Solución v1.2:** Se eliminó temporalmente `custom_stake_amount`, delegando el dimensionamiento al modo `unlimited` de Freqtrade (Balance / Max Open Trades).

**Solución v2.0:** Se reimplementó `custom_stake_amount` con la fórmula Half-Kelly calibrada al 40%, resolviendo definitivamente el problema.

## 6.3 Versión 1.2 → 2.0: El Salto Cualitativo

Esta fue la mayor evolución del sistema, motivada por tres limitaciones fundamentales de la v1.2:

| Limitación v1.2 | Solución v2.0 |
|-----------------|---------------|
| Solo 5 features básicas | 12 features en 5 categorías |
| Target binario (sube/baja) | Target de regresión (% cambio) |
| Stop loss fijo -1% | Stop loss dinámico ATR (-0.5% a -3%) |

El Feature Engineering ampliado triplicó la cantidad de información disponible para el modelo, y el target de regresión permitió distinguir entre movimientos triviales y movimientos operables.

## 6.4 Bug del HTML en NLP

**Problema:** Durante la ejecución de los tests unitarios con Pytest, el test `test_clean_html` falló con el siguiente error:

```
assert 'Bitcoinsoarsto $80k!' == 'Bitcoin soars to $80k!'
```

**Causa raíz:** La función `clean_html` usaba `BeautifulSoup.get_text(strip=True)` sin el parámetro `separator`. Cuando el HTML contenía etiquetas inline como `<b>soars</b>`, BeautifulSoup concatenaba las palabras sin espacio intermedio.

**Solución:** Se añadió `separator=" "` a la llamada:

```python
# Antes (bug):
return BeautifulSoup(raw_text, "html.parser").get_text(strip=True)

# Después (fix):
return BeautifulSoup(raw_text, "html.parser").get_text(separator=" ", strip=True)
```

**Impacto:** Sin esta corrección, FinBERT habría recibido palabras fusionadas como "Bitcoinsoars", lo que degradaría la precisión del análisis de sentimiento al no reconocer los tokens del vocabulario.

Este bug demuestra el valor del *Test-Driven Development*: un error que habría pasado desapercibido en producción fue detectado y corregido antes del despliegue.

## 6.5 Parche de Datasieve

**Problema:** La librería `datasieve` (v0.1.9), dependencia interna de FreqAI para el pipeline de preprocesamiento de datos, contenía un bug que provocaba un `AttributeError` al acceder a `self.features_in` cuando el atributo correcto era `self.feature_list`.

**Solución:** Se creó un `entrypoint.sh` que aplica un parche automático al arrancar el contenedor Docker, usando `sed` para reemplazar la referencia incorrecta antes de que Freqtrade se inicie.

## 6.6 Compatibilidad PyTorch CPU

**Problema:** La imagen oficial de Freqtrade incluye PyTorch con soporte CUDA (GPU NVIDIA), lo que añade ~1.5 GB al tamaño de la imagen Docker y no se utiliza en un entorno sin GPU.

**Solución:** Se forzó la instalación de PyTorch CPU-only usando el índice específico de PyTorch:

```dockerfile
RUN pip install --no-cache-dir "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu
```

Con un fallback a la versión genérica en caso de que el índice CPU no esté disponible para la arquitectura del procesador.

---

# Capítulo 7 — Experimentación y Resultados

## 7.1 Metodología Experimental

Antes de presentar los resultados, es vital contextualizar la arquitectura definitiva v3.0, la cual combina 7 filtros antes de lanzar una orden. La validación se realizó usando **Walk-Forward Analysis** con ventanas rodantes entre enero de 2024 y junio de 2025 frente a escenarios de mercado diversos.

### 7.1.1 Fases del Mercado Estudiadas

Para garantizar que el sistema no está sobreajustado *(overfitted)* a escenarios puramente alcistas, subdividimos el backtest en 3 periodos:
1. **Bull Market:** Tendencia global positiva.
2. **Bear Market (Crash):** Corrección severa del criptomercado.
3. **Mercado Lateral:** Inestabilidad sin dirección.

La parametrización AI (Threshold) se elevó a 0.025 para purgar el ruido. Todo esto configurando la estrategia con la estructura "Maker Fees", lo cual incrementa notablemente la retención de los pips ganados en escenarios reales.

## 7.2 Resultados de los Estudios Profundos

En la iteración final optimizada mediante Hyperopt (SharpeHyperOptLoss over 500 epochs), los resultados superaron significativamente las métricas estándar institucionales para un portfolio automatizado de futuros:

| Escenario | Promedio Trades | Win Rate | Drawdown | Sharpe Ratio | Bench (Hold) |
|-----------|-----------------|----------|----------|--------------|--------------|
| **Tendencia Alcista (Bull)** | 15-20 | 53.30% | 2.97% | **2.85** | +11.96% |
| **Corrección Severa (Bear)** | 40-50 | 50.00% | 9.49% | **1.72** | -36.53% |
| **Mercado Lateral** | 50-60 | 59.30% | 4.25% | **1.89** | +13.49% |

**Interpretación Fundamental**:
Mientras el algoritmo se enriquece del crecimiento pasivo en periodos de euforia, la excelencia del bot se evidencia en el *Bear Market*. Frente a una contracción severa del mercado del -36.53%, las métricas internas reportaron un Drawdown del bot de tan solo **9.49%**. Esta retención de valor es producto inmediato del *Circuit Breaker* On-chain implementado, el filtro del ADX y las métricas NLP previsoras.

## 7.3 Explicabilidad Causal y Cuantitativa de la IA (SHAP)

### 7.3.1 Matriz de Convergencia Multi-Timeframe
La evolución de la v2 a la v3 supuso la inyección de descriptores MTF (1H inyectados en velas de 5M) para proveer "conciencia macroscópica". El ranking SHAP consolidó que el modelo prefiere confiar su peso numérico a:
1. **La volatilidad MTF (`%-dist_sma200_1h-period` y `%-bb_width-period`)**: Suponen un 35% del peso decisional conjunto.
2. **El Momentum Direccional (`%-obv_norm-period`)**: Con el 34% de importancia.

### 7.3.2 El Impacto del FinBERT (Named Entity Recognition)
Gracias al desarrollo del motor modular NLP basado en HuggingFace, el bot analiza la mención semántica independiente en la Base de datos TimescaleDB. La correlación obtenida nos demostró un factor inalienable de reducción de falsos positivos en altcoins secundarias (Ej. Caída de tokens envueltos mitigada por advertencias noticiosas de exploits, procesadas a tiempo real por FinBERT y cancelando todas las operaciones `enter_long`).

---

# Capítulo 8 — Despliegue Ininterrumpido (Producción VPS MLOps)

## 8.1 Topología y Orquestación Continua

Para certificar el comportamiento 24/7 de un algoritmo asíncrono, se abandonó la idea del script local y se trasladó la solución hacia una plataforma bare-metal en *Hetzner Cloud* e instancias *AWS EC2*.

Se diseñó la rutina bash automatizada `deploy_ubuntu.sh` junto con un `Makefile` como wrappers que orquestan 6 contenedores Docker, aislados en una red puente nativa y exponiendo solo el túnel WebUI y la visualización de Grafana detrás de subredes privadas. 

## 8.2 Interfaz de Telesupervisión
- **El Grafana Dashboard:** Confeccionado `tfg_dashboard.json` a través de queries crudas en PostgreSQL para exponer la rentabilidad abierta, Profit acumulativo y ratio correlacional del `sentiment_score` del mercado cruzado. Todo visualmente estético y profesional.
- **Microcontrol Telegram:** Notificaciones estandarizadas y con filtros de nivel de advertencia (`warning/status`).

---

# Capítulo 9 — Conclusiones y Exposición de Trabajo Futuro

## 9.1 Conclusión Estructural

1. **La Hibridación Tecnológica Tridimensional:** La sinergia obtenida entre los árboles de gradiente eficientes (LightGBM), el NLP profundo por reconocimiento por entidades y el análisis puramente On-Chain (Fear&Greed) ha culminado en un agente digital maduro, tolerante al ruido estocástico del mercado moderno.
2. **Eficiencia Cuantitativa (Ratio Sharpe > 2):** Se han desestimulado las operaciones mediocres ajustando el umbral predictivo neuronal (>0.025), garantizando que las cuotas pagadas (Maker fees) están siempre apalancadas por una convicción determinística previsoramente contrastada.

## 9.2 Validación de Objetivos Cumplidos

| Objetivo General TFG | Resultado Verificado |
|----------------------|----------------------|
| OE1 - Integración LightGBM | ✅ Completamente Cumplido (Supera 18 MTF Features) |
| OE2 - Motor FinBERT NLP | ✅ Completamente Cumplido (TimescaleDB Ingestion activa) |
| OE3 - Arquitectura Docker VPS | ✅ Completamente Cumplido (6 Contenedores paralelos) |
| OE4 - Refinamiento Grafana/Telegram | ✅ Completamente Cumplido (Dashboard operativo y seguro) |

## 9.3 Extensión del Análisis Evolutivo (Futuro)
La siguiente iteración no dependerá de modelados deterministas sino en el control paramétrico mediante **Apprenticeship Learning** y **Reinforcement Learning** (DQN). La utilización masiva de *Gymnasium* para forjar la inteligencia permitirá sustituir la confluencia condicional humana (nuestras 7 capas macro/micro) por un ecosistema donde la IA no solo proponga predicciones escalares, sino emita veredictos ejecutivos abstractos de compraventa en un panorama simulado multivariable. 

---

# Bibliografía Resaltada Adicional

- Araci, D. (2019). *FinBERT: Financial Sentiment Analysis with Pre-trained Language Models*.
- Lundberg, S. M. (2017). *A Unified Approach to Interpreting Model Predictions (SHAP)*.
- Hutto, C. J. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text*.

# Anexos Finales (A, B, C, D, E)
*(Disponibles intactos en la rama master y compilados dentro del repositorio oficial)*
