#!/usr/bin/env python3
"""
Log processor 
"""

import os
from pathlib import Path
import logging
import re

# Directorios configurables vía variables de entorno (pero con defaults)
RAW_LOG_DIR = Path(os.getenv("RAW_LOG_DIR", "/var/log/app/raw"))
SANITIZED_LOG_DIR = Path(os.getenv("SANITIZED_LOG_DIR", "/var/log/app/sanitized"))

RAW_LOG_FILE = RAW_LOG_DIR / "app.log"
SANITIZED_LOG_FILE = SANITIZED_LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [log-processor] %(message)s",
)


def ensure_directories() -> None:
    """Asegura que los directorios existan."""
    if not RAW_LOG_DIR.exists():
        logging.error("El directorio de logs crudos no existe: %s", RAW_LOG_DIR)
        raise SystemExit(1)

    SANITIZED_LOG_DIR.mkdir(parents=True, exist_ok=True)


def simple_anonymize_line(line: str) -> str:
    """
    Aplica una anonimización simple a la línea.

    """
    # Reemplazar email=..., name=..., token=..., customer_id=..., ip=... por ***
    patterns = ["email", "name", "token", "customer_id", "ip"]
    sanitized = line

    for field in patterns:
        # Coincide con field=ALGO 
        sanitized = re.sub(rf"({field}=)(\S+)", rf"\1***", sanitized)

    return sanitized


def process_logs() -> None:
    """Lee el log crudo y genera el log anonimizado."""
    if not RAW_LOG_FILE.exists():
        logging.warning("No se encontró el archivo de log crudo: %s", RAW_LOG_FILE)
        logging.warning("Nada que procesar en este momento.")
        return

    logging.info("Procesando log crudo: %s", RAW_LOG_FILE)

    with RAW_LOG_FILE.open("r", encoding="utf-8") as src, \
            SANITIZED_LOG_FILE.open("w", encoding="utf-8") as dst:
        count = 0
        for line in src:
            sanitized_line = simple_anonymize_line(line)
            dst.write(sanitized_line)
            count += 1

    logging.info(
        "Procesamiento completado. %d líneas procesadas. Archivo anonimizad"
        "o: %s",
        count,
        SANITIZED_LOG_FILE,
    )


def main() -> None:
    logging.info("Iniciando log-processor.")
    ensure_directories()
    process_logs()
    logging.info("Finalizado log-processor.")


if __name__ == "__main__":
    main()
