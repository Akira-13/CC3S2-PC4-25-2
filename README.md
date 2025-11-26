# Secure Logs & Backup Stack

Stack local con `docker-compose` y app que genera logs sensibles que necesita backups encriptados.

## `app/web.py`

El archivo `web.py` implementa un servicio FastAPI con dos endpoints:

### `/health`

Devuelve un JSON `{"status": "ok"}` para confirmar que el contenedor está funcionando correctamente.

### `/event`

Genera un evento simulado que incluye información sensible falsa utilizando **Faker**, como:

* nombre completo
* correo
* token
* customer_id
* dirección IP pública

Cada request genera una entrada de log estructurada con el siguiente formato:

```
timestamp LEVEL login_attempt name=<name> email=<email> token=<token> customer_id=<id> ip=<ip>
```

Los logs se escriben en el archivo:

```
$RAW_LOG_DIR/app.log
```

Normalmente, `RAW_LOG_DIR` se asigna en Docker a un volumen donde se almacenan los logs crudos del sistema.

## Tests incluidos

### Test 1: `/health`

Verifica que:

* responde 200
* devuelve `{"status": "ok"}`

### Test 2: `/event`

Valida que:

* responde 201
* se crea un archivo de log en un directorio temporal
* el log contiene la entrada esperada (`login_attempt`, email, customer_id, etc.)

Las pruebas usan fixtures para:

* crear un directorio temporal de logs,
* configurar la variable de entorno `RAW_LOG_DIR`,
* importar `app/web.py` después de configurar el entorno (import diferido).

Esto evita escribir en volúmenes reales y garantiza que las pruebas sean reproducibles.