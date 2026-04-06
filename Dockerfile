FROM freqtradeorg/freqtrade:stable_freqai

# Cambiar a usuario root para instalar paquetes del sistema
USER root

# Instalar dependencias del sistema necesarias para compilar librerías
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Volver al usuario ftuser para instalar paquetes de Python
USER ftuser

# --- INSTALACIÓN DE DEPENDENCIAS ---
# PyTorch se instala aparte con CPU-only (sin CUDA/NVIDIA)
# Mac Apple Silicon no necesita las librerías NVIDIA (~1.5GB menos)
RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg2-binary \
    lightgbm \
    scikit-learn \
    pandas \
    xgboost \
    tensorboard

# Torch CPU separado para evitar arrastrar CUDA
RUN pip install --no-cache-dir "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || \
    pip install --no-cache-dir "torch>=2.6.0"

# Parche para bug datasieve 0.1.9 (features_in → feature_list)
USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER ftuser

ENTRYPOINT ["/entrypoint.sh"]