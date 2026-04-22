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

# Parche para bug datasieve 0.1.9: features_in no existe, debe ser feature_list
USER root
RUN sed -i 's/self\.features_in/self.feature_list/g' /home/ftuser/.local/lib/python3.13/site-packages/datasieve/pipeline.py && \
    echo "datasieve parcheado en buildtime"
USER ftuser

ENTRYPOINT ["freqtrade"]