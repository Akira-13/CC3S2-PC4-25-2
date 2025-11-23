# Sprint Backlog 

**Proyecto:** Secure Logs & Backup Stack
**Sprint:** 1
**Rol:** Desarrollo del servicio web generador de logs crudos


#  Historias / Issues del Sprint

## **1. Implementación de la aplicación web y generación de logs sensibles**

**Estado:** Completado
**Descripción:**
Implementación de la aplicación FastAPI (`web.py`) que expone `/health` y `/event`, generando datos sensibles con Faker y escribiéndolos en el volumen de logs crudos.
**Criterios de aceptación cumplidos:**

* `/health` responde 200 con JSON `{"status": "ok"}`
* `/event` genera datos sensibles falsos y los registra en un archivo dentro de `RAW_LOG_DIR`
* Logger configurado con formato consistente y volumen listo para el log-processor
  **Entregables:**
* `app/web.py`
* Configuración del logger y estructura de logs

## **2. Definición de requirements.txt para la app web**

**Estado:** Completado
**Descripción:**
Declaración de dependencias mínimas para la ejecución del módulo web, incluyendo FastAPI, Uvicorn, Faker y librerías internas.
**Criterios de aceptación cumplidos:**

* Solo contiene los paquetes realmente utilizados
  **Entregables:**
* `app/requirements.txt`

---

## **3. Pruebas básicas para /health y generación de logs**

**Estado:** Completado
**Descripción:**
Crear pruebas con pytest para verificar el correcto funcionamiento de los endpoints y validación del archivo de logs.
**Criterios de aceptación cumplidos:**

* Prueba de `/health` pasa correctamente
* Prueba de `/event` verifica creación del archivo y contenido del log
* Uso de un directorio temporal para evitar escribir en volúmenes reales
  **Entregables:**
* `tests/test_web.py`

---

## **4. Redacción de visión inicial del módulo web**

**Estado:** Completado
**Descripción:**
Documentar la visión arquitectónica y propósito del módulo web en `docs/vision.md`.
**Criterios de aceptación cumplidos:**

* Explica propósito, relación con log-processor, backups y razones pedagógicas
  **Entregables:**
* `docs/vision.md`


