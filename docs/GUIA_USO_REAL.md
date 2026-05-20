# Guía Integradora: Opere el Bot TFG con Capital Real

Esta es la guía oficial de producción del **Sistema de Trading Algorítmico Híbrido v3.0**. Después de haber superado las fases de Backtesting y Forward-Testing Simulado, estos son los pasos rigurosos para operar en la bolsa en vivo (Binance Futures) conectando capital real.

> [!CAUTION]
> **Advertencia de Riesgo Soberano:** El mercado de futuros de criptomonedas está altamente apalancado y es volátil. El autor declina cualquier responsabilidad por pérdidas de capital. Utilice esta guía bajo su propia deliberación y riesgo. Empiece siempre con el capital mínimo admitido por el exchange (aprox. 50-100 USDT).

---

## 1. Configuración de API Keys (Binance)

Para permitir que el Bot interactúe con el mercado sin comprometer su seguridad, debe establecer una barrera de permisos (*Least Privilege Principle*).

1. Acceda a la sección **API Management** de Binance.
2. Haga clic en *Create API*.
3. **MANDATORIO:** Desactive absolutamente las casillas `Enable Withdrawals` y `Enable Vanilla Options`.
4. **MANDATORIO:** Restrinja la API a una IP de confianza (la IP estática de su VPS). El bot fallará si esto no está configurado (Binance desactiva APIs sin IP tras 90 días).
5. Active únicamente:
   - `Enable Reading` (Lectura de precios y saldo)
   - `Enable Futures` (Operativa en Binance Futures)

Copie la `API Key` y el `API Secret`.

---

## 2. Configuración de Archivos del Bot

En su sistema local, abra el archivo secreto excluido de GitHub (`user_data/config_secrets.json`). Debe rellenar exactamente esta plantilla:

```json
{
    "telegram": {
        "enabled": true,
        "token": "SU_TOKEN_BOT_TELEGRAM",
        "chat_id": "SU_ID_DE_CHAT"
    },
    ...
    "exchange": {
        "key": "SU_BINANCE_API_KEY",
        "secret": "SU_BINANCE_API_SECRET"
    }
}
```

Luego, en `user_data/config.json`, modifique:
- `"dry_run": false` (Apaga el simulador. Esto es el punto de no retorno).

---

## 3. Despliegue Ininterrumpido en la Nube (VPS)

No ejecute el bot con dinero real en un ordenador portátil; un corte de luz o de hibernación le impedirá gestionar un *Stop Loss* crítico. El bot requiere 24/7.

**Servidor recomendado:** Hetzner Cloud (ARM CAX11 o CPX21) / Contabo.
**Requisitos mínimos:** 4GB RAM, 2 vCPU.

Una vez tenga acceso SSH al servidor virgen:

1. Suba todo su código fuente.
2. Ejecute el instalador autónomo:
   ```bash
   chmod +x deploy_ubuntu.sh
   ./deploy_ubuntu.sh
   ```
3. El script instalará automáticamente Docker, configurará el Firewall (solo puertos 22, 3000, 8081) y levantará los 6 microservicios.

---

## 4. Control Integral (El Archivo Makefile)

El `Makefile` en la raíz del proyecto permite operar el servidor con los siguientes comandos:

- Comando para arrancar el ecosistema en segundo plano:
  ```bash
  make start
  ```
- Comando para detener todas las operaciones temporalmente:
  ```bash
  make stop
  ```
- Para auditar por qué la IA (LightGBM) toma decisiones o está bloqueando operaciones en vivo vía MLOps:
  ```bash
  make logs
  ```
- Para limpiar la caché de modelos aprendidos y forzar un re-entrenamiento con datos nuevos de las últimas horas:
  ```bash
  make clean && make restart
  ```

---

## 5. El Sistema Nervioso Central: Telegram & Grafana

Una de las premisas del TFG (y aplicable a la vida real) es supeditar la acción humana a la supervisión remota.

- **Telegram:** Usted no necesita la terminal para saber qué pasa. Su *Bot de Telegram* le avisará de:
  1. *Entradas:* "LONG ETH/USDT (Risk: 5%)".
  2. *Salidas:* "PROFIT BTC/USDT +12%".
  3. *Mensajes de Alerta del Circuit Breaker.*
  
- **Grafana Inteligente:** 
  Puede escribir la dirección `http://<IP_VPS>:3000` en su navegador.
  Visualizará instantáneamente:
  1. Paneles de rentabilidad del Bot en tiempo real extraídos de `TimescaleDB`.
  2. El puntaje NLP per-coin en esa misma curva, determinando visualmente qué noticia disparó qué operación.

---

> [!TIP]
> **Checklist Final antes de inyectar dinero:**
> 1. ¿Está el firewall del VPS bloqueando la DB Postgres al exterior (`ufw status`)?
> 2. ¿Binance está amarrado únicamente a la IP del VPS?
> 3. ¿El `.env` o `config_secrets.json` NO han sido empujados accidentalmente a GitHub? (Compruebe escribiendo `git status`).
