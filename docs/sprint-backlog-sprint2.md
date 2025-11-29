# Sprint Backlog — Integrante A

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
