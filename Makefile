.PHONY: dev compose-up compose-down backup show-metrics

dev: compose-up

compose-up:
	bash scripts/up.sh

compose-down:
	bash scripts/down.sh

backup:
	bash backup/run-backup.sh

show-metrics:
	@if [ -f backups/metrics.csv ]; then \
		echo "Contenido de backups/metrics.csv:"; \
		cat backups/metrics.csv; \
	else \
		echo "No hay métricas aún. Ejecuta 'make backup' primero."; \
	fi
