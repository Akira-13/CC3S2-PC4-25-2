#!/usr/bin/env python3

import os
import re
import hashlib
from datetime import datetime
from typing import Dict, Pattern

# Directorios configurables vía variables de entorno
RAW_LOG_DIR = Path(os.getenv("RAW_LOG_DIR", "/var/log/app/raw"))
SANITIZED_LOG_DIR = Path(os.getenv("SANITIZED_LOG_DIR", "/var/log/app/sanitized"))
ERROR_LOG_PATH = os.getenv(
    "ERROR_LOG_PATH",
    os.path.join(SANITIZED_LOGS_DIR, "processor_errors.log"),
)

# Expresiones regulares para detectar datos sensibles
PATTERNS: Dict[str, Pattern[str]] = {
    # Correos electrónicos
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    # DNI con 8 dígitos (ej: 12345678)
    "dni": re.compile(r"\b\d{8}\b"),
    # Celular peruano típico: 9 + 8 dígitos (ej: 9XXXXXXXX)
    "phone": re.compile(r"\b9\d{8}\b"),
    # Dirección IP v4 simple
    "ip": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
}


def hash_value(value: str) -> str:
    """
    Genera un hash SHA-256 truncado para anonimizar un valor
    de forma determinística (misma entrada -> misma salida).
    """
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    # Truncamos para que sea más legible en los logs
    return digest[:12]


def anonymize_line(line: str) -> str:
    """
    Aplica anonimización a una línea de log, reemplazando
    valores sensibles por un marcador del tipo <tipo:hash>.

    Usamos pattern.sub para evitar reemplazos incorrectos
    (por ejemplo, que el DNI se reemplace dentro del teléfono).
    """
    sanitized = line

    for label, pattern in PATTERNS.items():
        def _replacer(match):
            original = match.group(0)
            masked = f"<{label}:{hash_value(original)}>"
            return masked

        sanitized = pattern.sub(_replacer, sanitized)

    return sanitized



def ensure_output_dirs():
    """
    Crea los directorios de salida si no existen.
    No lanza excepción si ya existen.
    """
    os.makedirs(SANITIZED_LOGS_DIR, exist_ok=True)


def log_error(message: str):
    """
    Registra un mensaje de error con timestamp en el archivo de errores.
    Nunca debe lanzar excepción (manejo defensivo).
    """
    try:
        os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
        timestamp = datetime.now().isoformat()
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Si fallara el log de errores, no hacemos nada más
        # para no romper el procesamiento principal.
        pass


def process_file(input_path: str, output_path: str):
    """
    Procesa un archivo de logs:
    - Lee todas las líneas.
    - Anonimiza cada línea.
    - Escribe el resultado en el archivo de salida.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        log_error(f"Archivo no encontrado: {input_path}")
        return
    except PermissionError:
        log_error(f"Permiso denegado al leer: {input_path}")
        return
    except Exception as e:
        log_error(f"Error leyendo {input_path}: {e}")
        return

    sanitized_lines = []

    for idx, line in enumerate(lines):
        try:
            sanitized = anonymize_line(line)
            sanitized_lines.append(sanitized)
        except Exception as e:
            # Si una línea falla, se registra y se continúa
            log_error(f"Error procesando línea {idx} en {input_path}: {e}")

    try:
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.writelines(sanitized_lines)
    except PermissionError:
        log_error(f"Permiso denegado al escribir: {output_path}")
    except Exception as e:
        log_error(f"Error escribiendo {output_path}: {e}")


def process_all_files():
    """
    Recorre el directorio de logs crudos y procesa cada archivo regular.
    """
    if not os.path.isdir(RAW_LOGS_DIR):
        log_error(f"Directorio de entrada no existe: {RAW_LOGS_DIR}")
        return

    ensure_output_dirs()

    for filename in os.listdir(RAW_LOGS_DIR):
        input_path = os.path.join(RAW_LOGS_DIR, filename)

        # Solo procesamos archivos regulares
        if not os.path.isfile(input_path):
            continue

        output_path = os.path.join(SANITIZED_LOGS_DIR, filename)
        process_file(input_path, output_path)


def main():
    """
    Punto de entrada del script.
    Pensado para ejecutarse dentro del contenedor de log-processor.
    """
    process_all_files()


if __name__ == "__main__":
    main()
