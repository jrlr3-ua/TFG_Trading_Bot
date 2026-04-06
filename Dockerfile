FROM freqtradeorg/freqtrade:develop

# Cambiar a usuario root para instalar paquetes del sistema
USER root

# Instalar dependencias del sistema necesarias para compilar librerías
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Volver al usuario ftuser para instalar paquetes de Python
USER ftuser

# --- INSTALACIÓN DE DEPENDENCIAS ÉLITE ---
# Añadimos xgboost y torch para satisfacer al motor de logs de FreqAI
# Mantenemos torch actualizado por seguridad (CVE-2025-32434)
RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg2-binary \
    datasieve \
    lightgbm \
    scikit-learn \
    pandas \
    xgboost \
    "torch>=2.6.0" \
    tensorboard