import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def logs_dir(tmp_path_factory):
    """
    Crea un directorio temporal para los logs de prueba y
    configura la variable de entorno RAW_LOG_DIR antes de importar la app.

    De esta forma, web.py usará este directorio en lugar de /var/log/app/raw.
    """
    tmp_dir = tmp_path_factory.mktemp("logs")
    os.environ["RAW_LOG_DIR"] = str(tmp_dir)
    return tmp_dir


@pytest.fixture(scope="session")
def test_client(logs_dir):
    """
    Importa la aplicación FastAPI después de configurar RAW_LOG_DIR
    y devuelve un TestClient para hacer requests a la API.
    """
    # Importamos aquí, dentro del fixture, para garantizar que
    # RAW_LOG_DIR ya está seteada cuando se evalúa web.py
    from app import web

    client = TestClient(web.app)
    return client


def test_health_ok(test_client):
    """
    Verifica que el endpoint /health responda 200 y el JSON esperado.
    """
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_event_creates_log_file_and_line(test_client, logs_dir):
    """
    Verifica que al invocar /event:

    - se responda con 201,
    - se cree el archivo de logs en el directorio configurado,
    - y el archivo contenga al menos una línea con 'login_attempt'.
    """
    # Llamamos al endpoint que genera el evento y el log.
    response = test_client.post("/event")

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Evento registrado"
    assert "generated" in body

    # Importamos web para acceder a LOG_FILE_PATH
    from app import web

    log_path = Path(web.LOG_FILE_PATH)

    # El archivo de log debe existir dentro del directorio temporal
    assert log_path.exists()

    # Leer contenido del log y validar que haya una entrada de login_attempt
    log_content = log_path.read_text()
    assert "login_attempt" in log_content
    assert "email=" in log_content
    assert "customer_id=" in log_content
