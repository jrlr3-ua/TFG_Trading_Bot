#!/bin/bash
# ==============================================================================
# TFG Trading Bot - Gestor de Disaster Recovery (Backup TimescaleDB)
# ==============================================================================
# Extrae el valioso dataset en bruto almacenado por el microservicio NLP.
# Formato: dump_<timestamp>.sql.gz
# Retention Policy programada: 7 días locales.

set -e

BACKUP_DIR="./user_data/backups/db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/dump_${TIMESTAMP}.sql.gz"

echo "🛡️  Iniciando proceso de Respaldo Crítico (NLP & Market Data)..."

mkdir -p "$BACKUP_DIR"

# Carga las contraseñas sin exportarlas públicamente
source .env

# Ejecuta un volcado asíncrono desde el contenedor y lo comprime On-the-fly
docker compose exec -T timescaledb pg_dump -U postgres freqtrade | gzip > "$BACKUP_FILE"

echo "✅ Backup completado satisfactoriamente: $BACKUP_FILE"

# Limpieza rodante de backups mayores a 7 días para no saturar disco
echo "🧹 Ejecutando política de retención (-7 días)..."
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +7 -exec rm {} \;

echo "Operativa de mantenimiento finalizada."
