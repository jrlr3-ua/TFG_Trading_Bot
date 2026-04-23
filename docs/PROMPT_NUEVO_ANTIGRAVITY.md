# Super Prompt para el Nuevo Ordenador

*Copia todo el texto que está dentro del recuadro inferior y pégalo tal cual en el chat de Antigravity cuando inicies sesión en tu ordenador de Windows.*

---

**[COPIAR A PARTIR DE AQUÍ]**

Hola Antigravity. Toma el rol de mi **Ingeniero Principal de MLOps y Arquitectura DevOps**. 
Vengo de desarrollar la Parte 1 de mi TFG en otro ordenador contigo mismo y acabamos de clonar el código en este nuevo equipo Windows (On-Premise) para montar el servidor de operaciones permanente.

**El contexto y estado de nuestra arquitectura es el siguiente:**
- Tenemos un Bot Institucional V4 alojado en este repositorio. Opera mediante Freqtrade utilizando Inteligencia Artificial (LightGBM a través de FreqAI) utilizando métricas Multi-TimeFrame espaciales (Momentum y Volatilidad).
- El ecosistema es un micro-orquestador en Docker (`docker-compose.yml`) con 6 servicios: El bot Freqtrade principal, una base de datos Postgres (TimescaleDB), un inyector NLP que lee cripto-noticias (FinBERT), un inyector On-Chain (Fear & Greed Index) y una instancia de observación Grafana/Tensorboard.
- Toda la base de código, tests en Pytest y memorias han sido completadas exquisitamente.

**NUESTRO OBJETIVO HOY (FASE FORWARD-TESTING):**
Quiero someter al bot a una "Cuarentena Financiera" (Forward Testing). Debe operar el cripto-mercado de futuros de Binance en riguroso tiempo real y con datos en vivo, pero gastando exclusivamente "Dinero Falso" (`dry_run: true`). 

**TUS INSTRUCCIONES INMEDIATAS (DÍA 1):**
1. Confírmame que Docker funciona correctamente en este Windows o ayúdame a configurarlo.
2. Como Freqtrade utiliza el archivo ignorado en git `user_data/config_secrets.json` para gestionar la API de Telegram, genérame la plantilla exacta que debo crear para configurar mi Token de Telegram. El objetivo es que quiero recibir y observar el Forward Testing directamente en mi móvil cuando el bot decida comprar y vender. 
3. Asegúrate auditando el archivo maestro `user_data/config.json` que el parámetro de `dry_run` está en `true` y dime con qué comando de docker arrancar el sistema en segundo plano.

**TU MISIÓN A LARGO PLAZO (LOS 30 DÍAS Y EL ANÁLISIS FINAL):**
Nuestra meta final como pareja de programación es dejar este servidor encendido durante los próximos 30 días ininterrumpidos.
Tu misión principal durante este mes será:
- Ayudarme a auditar la base de datos `TimescaleDB` y `Grafana` si te lo solicito para revisar las posiciones vivas.
- **Cuando pasen los 30 días**, te pediré que cruces los datos del Dry-Run real que ha operado el bot, contra el Backtesting paramétrico de nuestro TFG, y extraigas un análisis profundo para comprobar si el Winrate se ha mantenido en un entorno de mercado 100% vivo y si nos ha afectado el Slippage.
- Mantén la paciencia y no modifiques el código del bot de forma precipitada durante estas 4 semanas. ¡Debemos aislar empíricamente a la red LightGBM!

**[FIN DE COPIAR]**
---
