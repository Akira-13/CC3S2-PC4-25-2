#!/usr/bin/env python3
"""
backup.py - Servicio de backup para Secure Logs & Backup Stack.

- Leer los logs ANONIMIZADOS desde SANITIZED_LOG_DIR.
- Empaquetar todos los archivos en un .tar.gz.
- "Cifrar" el tar.gz usando base64.
- Guardar el artefacto final en BACKUP_OUTPUT_DIR con extensión .enc.
"""

import base64
import datetime
import logging
import os
import tarfile
import time
from pathlib import Path
from typing import Optional

SANITIZED_LOG_DIR = Path(os.getenv("SANITIZED_LOG_DIR", "/var/log/app/sanitized"))
BACKUP_OUTPUT_DIR = Path(os.getenv("BACKUP_OUTPUT_DIR", "/backups"))
BACKUP_ENCRYPTION = os.getenv("BACKUP_ENCRYPTION", "base64").lower()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [backup] %(message)s",
)


def ensure_directories() -> None:
    """Verifica que existan los directorios necesarios."""
    if not SANITIZED_LOG_DIR.exists():
        logging.error("El directorio de logs anonimizados no existe: %s", SANITIZED_LOG_DIR)
        raise SystemExit(1)

    BACKUP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_files_to_backup() -> list[Path]:
    """Encuentra todos los archivos dentro de SANITIZED_LOG_DIR."""
    files = [p for p in SANITIZED_LOG_DIR.rglob("*") if p.is_file()]
    if not files:
        logging.warning("No se encontraron archivos para respaldar en %s", SANITIZED_LOG_DIR)
    else:
        logging.info("Se encontraron %d archivos para respaldar.", len(files))
    return files


def get_dir_size_bytes(path: Path) -> int:
    """Calcula el tamaño total (en bytes) de todos los archivos dentro de un directorio.

    - Si el directorio no existe, retorna 0 y registra un warning.
    - Ignora subdirectorios vacíos.
    """
    try:
        if not path.exists():
            logging.warning("Directorio no existe para cálculo de tamaño: %s", path)
            return 0

        total = 0
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except Exception as e:
                    logging.warning("No se pudo obtener tamaño de %s: %s", p, e)
        return total
    except Exception as e:
        logging.error("Error calculando tamaño de %s: %s", path, e)
        return 0


def create_tar_gz(files: list[Path]) -> Optional[Path]:
    """Crea un archivo .tar.gz con los archivos de entrada."""
    if not files:
        logging.info("No hay archivos para empaquetar. No se generará backup.")
        return None

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    tar_path = BACKUP_OUTPUT_DIR / f"backup-{timestamp}.tar.gz"

    logging.info("Creando archivo tar.gz en: %s", tar_path)

    with tarfile.open(tar_path, mode="w:gz") as tar:
        for f in files:
            arcname = f.relative_to(SANITIZED_LOG_DIR)
            tar.add(f, arcname=arcname)

    logging.info("Archivo tar.gz creado correctamente.")
    return tar_path


def encrypt_base64(source: Path) -> Path:
    """
    "Cifra" el archivo usando base64:
    - Lee el .tar.gz
    - Codifica a base64
    - Escribe en .enc
    - Elimina el tar.gz original
    """
    enc_path = source.with_suffix(source.suffix + ".enc")  # backup-xxxx.tar.gz.enc

    logging.info("Iniciando cifrado base64 de %s -> %s", source, enc_path)

    data = source.read_bytes()
    encoded = base64.b64encode(data)

    with enc_path.open("wb") as f:
        f.write(encoded)

    # Eliminamos el archivo sin cifrar
    source.unlink(missing_ok=True)

    logging.info("Cifrado simulado completado. Archivo final: %s", enc_path)
    return enc_path


def encrypt_backup(tar_path: Path) -> Path:
    """Selecciona el modo de 'cifrado'. Por ahora solo base64."""
    if BACKUP_ENCRYPTION == "base64":
        return encrypt_base64(tar_path)

    logging.warning(
        "Modo de cifrado '%s' no soportado. Usando base64 por defecto.",
        BACKUP_ENCRYPTION,
    )
    return encrypt_base64(tar_path)


def main() -> None:
    logging.info("Iniciando proceso de backup.")
    ensure_directories()
    files = find_files_to_backup()

    # Medición de tiempo: justo antes de iniciar el empaquetado
    start_time = time.time()

    # Métrica de tamaño antes: suma de los archivos anonimizados
    size_before_bytes = get_dir_size_bytes(SANITIZED_LOG_DIR)
    logging.info("metrics size_before_bytes=%d", size_before_bytes)

    tar_path = create_tar_gz(files)

    if tar_path is None:
        logging.info("No se generó backup (no había archivos para empaquetar).")
        return

    enc_path = encrypt_backup(tar_path)
    # Medición de tiempo: justo después de finalizar el cifrado
    end_time = time.time()
    duration_seconds = end_time - start_time

    # Log de métricas estructuradas (clave=valor) para fácil ingesta
    logging.info(
        "metrics backup_duration_seconds=%.3f start_time=%.6f end_time=%.6f",
        duration_seconds,
        start_time,
        end_time,
    )

    # Métrica de tamaño después: tamaño del archivo cifrado final
    try:
        size_after_bytes = enc_path.stat().st_size
    except Exception as e:
        logging.error("No se pudo obtener tamaño de backup cifrado %s: %s", enc_path, e)
        size_after_bytes = 0
    logging.info(
        "metrics size_after_bytes=%d size_before_bytes=%d",
        size_after_bytes,
        size_before_bytes,
    )
    logging.info("Backup completado con éxito: %s", enc_path)


if __name__ == "__main__":
    main()
