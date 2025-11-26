#!/usr/bin/env python3
"""
Aplicación web principal del proyecto Secure Logs & Backup Stack.

- Expone el endpoint /health para verificar el estado del servicio.
- Genera logs con campos sensibles simulados (email, token, customer_id)
  y los escribe en un archivo dentro del volumen de logs crudos.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from faker import Faker

# crear instancia de la aplicación fastapi
app = FastAPI(title="Secure Logs & Backup Stack - Web")

# información falsa
fake = Faker()

# directorio donde se guardarán los logs crudos
# este directorio debe mapearse a un volumen en docker-compose
RAW_LOG_DIR = os.getenv("RAW_LOG_DIR", "/var/log/app/raw")

# asegurarnos de que el directorio exista al iniciar el contenedor
os.makedirs(RAW_LOG_DIR, exist_ok=True)

# ruta completa del archivo de logs.
LOG_FILE_PATH = os.path.join(RAW_LOG_DIR, "app.log")

# configuración básica del logger de la aplicación.
logger = logging.getLogger("secure_logs_app")
logger.setLevel(logging.INFO)

# evitar agregar múltiples handlers si el módulo se importa varias veces.
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    # formato simple para facilitar el procesamiento posterior.
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


@app.get("/health")
async def health():
    """
    Endpoint de salud del servicio.

    Retorna 200 OK si la aplicación está levantada correctamente.
    """
    return {"status": "ok"}


@app.post("/event")
async def event():
    """
    Genera un evento con datos sensibles aleatorios usando Faker
    y escribe un log estructurado para que el log-processor pueda procesarlo.
    """

    # Datos sensibles falsos
    full_name = fake.name()
    email = fake.email()
    token = fake.sha256()
    customer_id = fake.random_int(min=10000, max=99999)
    ip_address = fake.ipv4_public()

    # Línea estructurada para posterior anonimización
    logger.info(
        "login_attempt name=%s email=%s token=%s customer_id=%s ip=%s",
        full_name,
        email,
        token,
        customer_id,
        ip_address,
    )

    return JSONResponse(
        status_code=201,
        content={
            "message": "Evento registrado",
            "generated": {
                "name": full_name,
                "email": email,
                "customer_id": customer_id,
                "ip": ip_address,
            },
        },
    )


# punto de entrada opcional para correr localmente con python app/web.py
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("web:app", host="0.0.0.0", port=port, reload=False)
