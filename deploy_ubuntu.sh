#!/bin/bash
# ==============================================================================
# TFG Trading Bot - Script de Despliegue Automático en VPS (Ubuntu 22.04+)
# ==============================================================================
# Este script automatiza la instalación de dependencias en un servidor virgen en
# la Nube (AWS, Hetzner, Contabo) para poder hostear el bot 24/7.
#
# Autor: Joan
# ==============================================================================

set -e

echo "🚀 Iniciando el Despliegue del Sistema TFG Trading Bot..."
echo "------------------------------------------------------------"

# 1. Actualizar el sistema e instalar prerequisitos
echo "📦 Actualizando paquetes del sistema..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git ufw

# 2. Configurar el Firewall (Seguridad Básica)
echo "🛡️ Configurando Firewall (UFW)..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 3000/tcp # Grafana Web UI
sudo ufw allow 8081/tcp # Freqtrade Web UI (TFG)
sudo ufw --force enable

# 3. Instalación de Docker y Docker Compose
if ! command -v docker &> /dev/null
then
    echo "🐳 Instalando Docker..."
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    echo "🐳 Docker ya está instalado. Omitiendo."
fi

# Añadir el usuario actual al grupo docker para no usar sudo
sudo usermod -aG docker $USER

# 4. Iniciar el demonio (Daemon) del Bot
echo "⚙️ Levantando la arquitectura de Microservicios..."
echo "Asegúrate de haber copiado tu 'user_data/config_secrets.json' y '.env' antes de este paso."
echo "Levantando Docker Compose en modo 'Detached' (Background)..."

docker compose up --build -d

echo "------------------------------------------------------------"
echo "✅ ¡Despliegue finalizado exitosamente!"
echo "📡 Revisa los logs en vivo ejecutando: docker compose logs -f"
echo "📊 Grafana Dashboard expuesto en: http://<tu-ip-publica>:3000"
echo "🤖 Freqtrade UI expuesto en: http://<tu-ip-publica>:8081"
echo "============================================================"
