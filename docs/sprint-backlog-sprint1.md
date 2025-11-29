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

---

## **5. Mejora de anonimización en el log-processor**

**Estado:** Completado  
**Descripción:**  
Implementar y mejorar la lógica de anonimización en `log-processor/processor.py` para proteger datos sensibles presentes en los logs crudos generados por el módulo web. Se utilizan expresiones regulares y hashing determinístico para reemplazar valores sensibles por tokens anonimizados.

**Criterios de aceptación cumplidos:**

* El log-processor lee archivos de logs desde el directorio configurado en `RAW_LOGS_DIR`.
* Se detectan y anonimiza al menos los siguientes tipos de datos:
  * emails (`usuario@dominio.com`),
  * DNI de 8 dígitos,
  * teléfonos celulares en formato `9XXXXXXXX`,
  * direcciones IP IPv4.
* En los archivos generados en `SANITIZED_LOGS_DIR` **no aparecen** emails, DNIs, teléfonos ni IPs en texto plano.
* Los valores sensibles se reemplazan por tokens del tipo `<email:HASH>`, `<dni:HASH>`, `<phone:HASH>`, `<ip:HASH>`.
* El formato general del log (`timestamp LEVEL message ...`) se mantiene legible.

**Entregables:**

* `log-processor/processor.py` (lógica de anonimización mejorada).

---

## **6. Manejo robusto de errores y documentación del log-processor**

**Estado:** Completado  
**Descripción:**  
Fortalecer el manejo de errores en `log-processor/processor.py` para que el procesamiento de logs no se detenga ante archivos o líneas problemáticas, y documentar el comportamiento del módulo en la visión del proyecto y en este backlog.

**Criterios de aceptación cumplidos:**

* Si `RAW_LOGS_DIR` no existe o no es accesible, el log-processor registra un error en `ERROR_LOG_PATH` y termina de forma controlada.
* Errores al leer archivos individuales (por ejemplo, permisos) se registran en `ERROR_LOG_PATH` sin interrumpir el procesamiento del resto de archivos.
* Errores al escribir los archivos anonimizados se registran en `ERROR_LOG_PATH`.
* Errores al procesar líneas individuales no detienen el procesamiento del archivo completo; solo se registra la línea problemática.
* Se registra un archivo de errores `processor_errors.log` dentro de `SANITIZED_LOGS_DIR` (o ruta configurada mediante `ERROR_LOG_PATH`).
* Se añade una sección en `docs/vision.md` describiendo:
  * el propósito del log-processor,
  * el flujo de datos entre logs crudos y anonimizados,
  * las reglas de anonimización implementadas en el Sprint 1,
  * el manejo de errores.

**Entregables:**

* `log-processor/processor.py` con manejo de errores robusto.
* Sección “Módulo log-processor” en `docs/vision.md`.
* Historias actualizadas en `docs/sprint-backlog-sprint1.md`.


