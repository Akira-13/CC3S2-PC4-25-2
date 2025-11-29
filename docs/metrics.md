# Métricas de Backup - Documentación Técnica

## Descripción general

El módulo `backup/backup.py` captura y retorna métricas estructuradas sobre el proceso de backup, permitiendo al equipo analizar la eficiencia del empaquetado, cifrado y compresión de logs anonimizados.

## Estructura de métricas

Cada ejecución exitosa de `main()` retorna un diccionario con los siguientes campos:

```python
{
    "timestamp": "2025-11-28T10:30:45.123456",
    "backup_file": "backup-20251128-103045.tar.gz.enc",
    "duration_seconds": 1.234,
    "size_before_bytes": 524288,
    "size_after_bytes": 196608
}
```

## Campos y cálculos

### `timestamp`
- **Tipo**: `str` (ISO-8601)
- **Formato**: `YYYY-MM-DDTHH:MM:SS.ffffff` (UTC)
- **Cálculo**: `datetime.datetime.utcnow().isoformat()`
- **Descripción**: Momento exacto en que se completó el proceso de backup.

### `backup_file`
- **Tipo**: `str`
- **Formato**: `backup-YYYYMMDD-HHMMSS.tar.gz.enc`
- **Cálculo**: Nombre del archivo cifrado final generado por `encrypt_backup()`.
- **Descripción**: Identificador único del archivo de backup producido.

### `duration_seconds`
- **Tipo**: `float`
- **Precisión**: 3 decimales (milisegundos)
- **Cálculo**: 
  ```python
  start_time = time.time()  # Capturado antes de create_tar_gz()
  # ... proceso de empaquetado y cifrado ...
  end_time = time.time()    # Capturado después de encrypt_backup()
  duration_seconds = end_time - start_time
  ```
- **Descripción**: Tiempo total transcurrido desde el inicio del empaquetado hasta la finalización del cifrado, medido en segundos.
- **Incluye**:
  - Creación del archivo `.tar.gz`
  - Codificación Base64 (cifrado simulado)
  - I/O de disco para lectura y escritura

### `size_before_bytes`
- **Tipo**: `int`
- **Unidad**: Bytes
- **Cálculo**: Suma de `st_size` de todos los archivos en `SANITIZED_LOG_DIR`:
  ```python
  def get_dir_size_bytes(path: Path) -> int:
      total = 0
      for p in path.rglob("*"):
          if p.is_file():
              total += p.stat().st_size
      return total
  ```
- **Descripción**: Tamaño total en bytes de los logs anonimizados **antes** del empaquetado.
- **Consideraciones**:
  - Si el directorio no existe, retorna `0` y registra un warning.
  - Ignora subdirectorios vacíos.
  - Solo cuenta archivos regulares (no enlaces simbólicos ni pipes).

### `size_after_bytes`
- **Tipo**: `int`
- **Unidad**: Bytes
- **Cálculo**: `enc_path.stat().st_size` del archivo `.enc` final.
- **Descripción**: Tamaño en bytes del archivo de backup cifrado **después** del empaquetado y codificación Base64.
- **Consideraciones**:
  - Incluye el overhead de la codificación Base64 (~33% de incremento sobre el `.tar.gz`).
  - Si no se puede obtener el tamaño (permisos, archivo borrado), se registra como `0` con un error en logs.

## Integración

### Retorno de métricas

La función `main()` retorna:
- `dict` con las métricas si el backup se completa exitosamente.
- `None` si no hay archivos para respaldar.

### Logs estructurados

Adicionalmente, `backup.py` emite logs estructurados en formato `clave=valor` para ingesta por herramientas de monitoreo:

```
2025-11-28 10:30:45 INFO [backup] metrics size_before_bytes=524288
2025-11-28 10:30:46 INFO [backup] metrics backup_duration_seconds=1.234 start_time=1732790400.123456 end_time=1732790401.357910
2025-11-28 10:30:46 INFO [backup] metrics size_after_bytes=196608 size_before_bytes=524288
2025-11-28 10:30:46 INFO [backup] metrics summary backup_file=backup-20251128-103045.tar.gz.enc duration_seconds=1.234 size_before_bytes=524288 size_after_bytes=196608
```
## Persistencia en CSV

Además del retorno en memoria y de los logs estructurados, el servicio de backup **persiste las métricas en un archivo CSV** para facilitar su análisis posterior.

- **Ruta por defecto**: `backups/metrics.csv` (en el host).
- **Configuración**: controlada por la variable de entorno `BACKUP_METRICS_PATH`  
  (por defecto `BACKUP_OUTPUT_DIR / "metrics.csv"`).

Cada ejecución exitosa de `main()`:

- Crea el archivo `metrics.csv` si no existe.
- Escribe la cabecera una sola vez (nombres de columnas).
- Agrega una nueva fila con los campos:

  - `timestamp`
  - `backup_file`
  - `duration_seconds`
  - `size_before_bytes`
  - `size_after_bytes`

La escritura se realiza mediante la función utilitaria:

```python
def append_metrics_csv(record: dict, path: Path = METRICS_FILE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists()
    fieldnames = list(record.keys())

    logging.info("Escribiendo métricas de backup en: %s", path)

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)
```

## Uso práctico de las métricas

En el flujo normal del proyecto, los backups se ejecutan mediante:

```bash
make backup
# o directamente
bash backup/run-backup.sh
```

Cada ejecución de backup:

* genera un archivo `.enc` en `backups/`,
* y agrega un registro a `backups/metrics.csv`.

Para inspeccionar rápidamente las métricas desde la raíz del proyecto se expone el target:

```bash
make show-metrics
```

que muestra el contenido de `backups/metrics.csv` si existe.

El archivo CSV puede abrirse en herramientas externas (por ejemplo, Excel o pandas) para:

* contar el número de backups realizados,
* calcular el tiempo promedio de backup (`duration_seconds`),
* comparar tamaños antes y después (`size_before_bytes` vs `size_after_bytes`),
* detectar tendencias de crecimiento en los logs anonimizados.


