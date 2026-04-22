# ==============================================================================
# TFG Trading Bot - Gestor de Entorno
# ==============================================================================
# Este Makefile proporciona atajos para administrar fácilmente la operativa 24/7.
# Uso: `make <comando>`

.PHONY: start stop restart logs reset-db ui help clean

help:
	@echo "🤖 TFG Trading Bot - Comandos Disponibles:"
	@echo "--------------------------------------------------------"
	@echo "make start    - Inicia todos los servicios en background"
	@echo "make stop     - Detiene todos los contenedores"
	@echo "make restart  - Reinicia la arquitectura completa"
	@echo "make logs     - Muestra el log centralizado del Bot principal"
	@echo "make nlp-logs - Muestra los logs del motor FinBERT"
	@echo "make db-logs  - Muestra los logs de TimescaleDB"
	@echo "make backup   - Crea una instantánea SQL comprimida de Postgres"
	@echo "make test     - Lanza la suite de Pruebas Unitaria Local (Pytest)"
	@echo "make clean    - Borra modelos y logs obsoletos (recomendado antes de backtests)"
	@echo "--------------------------------------------------------"

start:
	docker compose up -d
	@echo "✅ Bot iniciado en modo detached. Usa 'make logs' para ver la actividad."

stop:
	docker compose down
	@echo "🛑 Todos los servicios han sido detenidos."

restart: stop start

logs:
	docker compose logs -f freqtrade

nlp-logs:
	docker compose logs -f sentiment_analysis

db-logs:
	docker compose logs -f timescaledb

backup:
	./backup_db.sh

test:
	export PYTHONPATH=./ && pytest tests/ -v

clean:
	@echo "🧹 Limpiando modelos obsoletos de la IA..."
	rm -rf user_data/models/tfg-bot-v3*
	rm -rf user_data/freqaimodels/*
	@echo "✅ Limpieza completada."
