# Setup de Servidor "On-Premise" (Ordenador Casero dedicado al TFG)

Montar tu propio servidor en casa es una práctica increíble y totalmente profesional (se conoce en el sector como contar con infraestructura *On-Premise* o un *Home Lab*). 

Sin embargo, para que funcione a la perfección y no ponga en riesgo tu capital financiero, tu ordenador de repuesto necesita cumplir con unas arquitecturas mínimas. Sigue estos pasos para convertir ese equipo en la fortaleza del Bot V4.

## 1. Reglas de Oro Financieras (Hardware y Red)
- **Cable, nunca Wi-Fi:** Conecta el ordenador directamente a tu router de casa mediante un cable Ethernet. Las redes Wi-Fi sufren latencia o se apagan por la noche. En el trading, la latencia te puede liquidar.
- **Energía y Suspensión:** Ve a la configuración de energía de ese ordenador y desactiva, bajo cualquier concepto, que la pantalla, el disco duro o el procesador entren en suspensión o hibernación.

## 2. El Sistema Operativo (Ubuntu Linux)
Si el ordenador antiguo tiene Windows, consumirá RAM inútilmente (con su antivirus y recursos de escritorio). Como ingeniero, la mejor opción es **instalarle Linux (Ubuntu Server 22.04 o superior)**.

1. Descarga la imagen ISO de Ubuntu en un Pendrive USB.
2. Inicia el ordenador desde el pendrive e instala el sistema operativo borrando por completo Windows.
3. Esto garantizará que el ordenador dedique el 100% de su RAM a la Inteligencia Artificial (LightGBM).

> *Nota rápida:* Si no quieres instalar Linux y prefieres mantener Windows 10/11 o macOS Antiguo, debes descargar a la fuerza **Docker Desktop** e instalarlo allí.

## 3. Traslado del Código
Una vez tengas tu ordenador antiguo encendido (si es Linux o Windows):
1. Copia toda esta carpeta `TFG_Trading_Bot` a dicho ordenador (puedes usar un Pendrive, o clonar tu repositorio desde GitHub).
2. Si has instalado Ubuntu, simplemente abre una terminal allí dentro y ejecuta el programa que habíamos creado:
   ```bash
   chmod +x deploy_ubuntu.sh
   ./deploy_ubuntu.sh
   ```
3. Si está en Windows, levántalo todo haciendo doble clic o ejecutando la orden en el powershell: `docker-compose up -d`.

## 4. Telesupervisión Segura (Tailscale)
El problema de dejar el ordenador en tu casa operando, es qué haces si te vas de viaje a la universidad y quieres mirar tu Grafana. Abrir los puertos de tu router a internet es **peligrosísimo**.

Para solucionarlo, debes usar una Red Zero-Trust:
1. Instala en tu móvil/portátil y en el ordenador antiguo la app **Tailscale**.
2. Tailscale creará un túnel privado y encriptado entre los dos. Esto le asignará a tu "Servidor Casero" una IP especial (ej. `100.101.44.2`).
3. Te vayas a China o a la biblioteca, solo tendrás que escribir en tu navegador `http://100.101.44.2:3000` y verás mágicamente tu cuadro de mandos de Grafana con toda seguridad. 
