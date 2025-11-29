# Sprint Backlog

**Proyecto:** Secure Logs & Backup Stack
**Sprint:** 2
**Rol:** Desarrollo del módulo de backups e instrumentación de métricas


# Historias / Issues del Sprint

## **1. Instrumentación de tiempo de ejecución del proceso de backup**

**Descripción:**
Se agregó medición de tiempo al proceso completo de backup, envolviendo las etapas de empaquetado y cifrado.
El flujo ahora captura:

* `start_time` antes de iniciar `create_tar_gz`
* `end_time` inmediatamente después del cifrado
* `duration_seconds = end_time - start_time`

Esta métrica permite evaluar la eficiencia del proceso y es registrada de manera estructurada.

**Criterios de aceptación cumplidos:**

* Se mide el tiempo real de ejecución del backup.
* El valor `duration_seconds` se refleja en logs y en el diccionario de métricas.
* El cálculo captura el tiempo completo del flujo (empaquetado + cifrado).

**Entregables:**

* Instrumentación dentro de `backup/main()`
* Logs estructurados con duración del backup

## **2. Cálculo del tamaño total de los logs anonimizados (size_before_bytes)**

**Descripción:**
Se implementó la función utilitaria:

```python
get_dir_size_bytes(path: Path) -> int
```

que suma el tamaño total de los archivos dentro de `SANITIZED_LOG_DIR`.
Este valor es registrado tanto en logs como en métricas.

**Criterios de aceptación cumplidos:**

* Se calcula correctamente el tamaño total en bytes del directorio.
* Manejo seguro para:

  * directorios inexistentes,
  * errores al leer tamaños,
  * directorios vacíos.
* Se vuelve parte del diccionario de métricas en `main()`.

**Entregables:**

* `get_dir_size_bytes()` dentro de `backup.py` ()

---

## **3. Cálculo del tamaño del archivo cifrado final (size_after_bytes)**

**Descripción:**
Una vez generado el archivo `.tar.gz.enc`, se obtiene su tamaño real en bytes para registrar su peso final.

**Criterios de aceptación cumplidos:**

* Se obtiene el tamaño mediante `enc_path.stat().st_size`.
* Si el archivo no es accesible, se captura el error y se asigna `0` de forma controlada.
* El valor `size_after_bytes` se integra correctamente en logs y métricas.

**Entregables:**

* Lógica de tamaño dentro de `main()` → `size_after_bytes` ()

---

## **4. Generación de estructura de métricas consolidada**

**Descripción:**
Se implementó un diccionario de métricas generado al final de `main()` con todos los valores relevantes del backup:

```python
metrics = {
    "timestamp": <UTC ISO-8601>,
    "backup_file": <nombre del .enc>,
    "duration_seconds": <float>,
    "size_before_bytes": <int>,
    "size_after_bytes": <int>,
}
```

Incluye un timestamp en UTC, información del archivo generado y métricas de tiempo y tamaño.

**Criterios de aceptación cumplidos:**

* Se construye una estructura clara y consistente.
* Cada campo está correctamente poblado.
* La métrica se registra en logs en formato clave-valor.

**Entregables:**

* Diccionario de métricas en `main()`, retornado al final ()

---

## **5. Retorno del diccionario de métricas desde `main()`**

**Descripción:**
La función `main()` ahora retorna el diccionario de métricas para permitir:

* persistirlo como archivo JSON en otro componente,
* consumirlo en scripts como `run-backup.sh`,
* integrarlo en flujos posteriores del proyecto.

**Criterios de aceptación cumplidos:**

* `main()` retorna `metrics` cuando hay backup, y `None` si no hay archivos.
* Los consumidores externos pueden acceder directamente a la estructura.
* El retorno no rompe la ejecución standalone de `backup.py`.

**Entregables:**

* Implementación del retorno en `backup/main()` ()


# Sprint Backlog — Sandro Carrillo

**Proyecto:** Secure Logs & Backup Stack  
**Sprint:** 2  
**Rol:** Métricas de backups, persistencia y tooling de soporte

## **6. Persistencia de métricas de backup en CSV**

**Descripción:**  
Implementar la persistencia de las métricas generadas por `backup/main()` en un archivo CSV alojado en el host, de forma que cada ejecución de backup deje un registro histórico. El archivo se encuentra en el directorio de backups y puede ser consumido por herramientas externas (Excel, pandas, etc.).

Las métricas se almacenan en:

- `backups/metrics.csv` (ruta por defecto),
- usando las mismas claves del diccionario retornado por `main()`:
  - `timestamp`
  - `backup_file`
  - `duration_seconds`
  - `size_before_bytes`
  - `size_after_bytes`

**Criterios de aceptación cumplidos:**

* Se crea el archivo `backups/metrics.csv` si no existe.
* La primera vez que se escribe, se incluye una cabecera con los nombres de las columnas.
* Cada ejecución exitosa de backup agrega una nueva fila con las métricas correspondientes.
* El archivo `backups/metrics.csv` es visible en el host (no solo dentro del contenedor).
* El flujo no se rompe si la escritura de métricas falla; el error se registra en logs y el backup sigue su curso.

**Entregables:**

* Función `append_metrics_csv(record: dict, path: Path = METRICS_FILE_PATH)` en `backup/backup.py`.
* Llamada a `append_metrics_csv(metrics)` dentro de `main()` después de construir el diccionario de métricas.
* Archivo de ejemplo `backups/metrics.csv` generado durante las pruebas.

---

## **7. Comandos de Makefile para backups y visualización de métricas**

**Descripción:**  
Exponer comandos simples en el `Makefile` de la raíz del proyecto para que cualquier integrante del equipo pueda:

* ejecutar el proceso de backup de forma estándar, y
* revisar rápidamente las métricas registradas.

Se agregan los targets:

* `make backup` → ejecuta el script `backup/run-backup.sh`.
* `make show-metrics` → muestra el contenido de `backups/metrics.csv` (si existe).

**Criterios de aceptación cumplidos:**

* `make backup` ejecuta el contenedor de backup y genera:
  * un nuevo archivo `.enc` en `backups/`,
  * y una nueva fila en `backups/metrics.csv`.
* `make show-metrics`:
  * imprime el contenido de `backups/metrics.csv` si el archivo existe,
  * imprime un mensaje amigable si aún no hay métricas.
* Los comandos funcionan desde la raíz del proyecto, sin necesidad de navegar a subdirectorios.

**Entregables:**

* `Makefile` actualizado con los targets `backup` y `show-metrics`.
* Evidencia de ejecución (logs o capturas) mostrando:
  * creación de backups,
  * actualización de `backups/metrics.csv`,
  * salida de `make show-metrics`.

