# Secure Logs & Backup Stack — Visión del Módulo Web

## 1. Propósito del módulo web

El servicio web es el punto de entrada del flujo completo del proyecto *Secure Logs & Backup Stack*.
Su función principal es **generar eventos que simulan interacciones reales de usuarios**, produciendo **logs crudos** que contienen datos sensibles. 

## 2. Comportamiento general

El servicio expone dos endpoints:

### `/health`

Permite verificar que el contenedor está operativo.
Se usa para pruebas, monitoreo y para confirmar que la aplicación arranca correctamente dentro del stack.

### `/event`

Genera un evento falso utilizando **Faker**, incluyendo datos típicamente sensibles, como:

* nombre completo
* email
* token
* customer_id
* dirección IP pública

Cada llamada a `/event` produce una **entrada de log estructurada** que será escrita dentro del **volumen de logs crudos**.

Este diseño reproduce un caso realista donde un servicio genera datos que requieren tratamiento seguro posterior.

## 3. Generación de logs crudos

Los logs crudos representan información “sin procesar”, es decir, **antes de cualquier anonimización**.
El módulo web:

* utiliza un logger configurado para escribir a un archivo dentro del directorio apuntado por `RAW_LOG_DIR`,
* usa un formato claro y lineal:

  ```
  timestamp LEVEL message key=value key=value ...
  ```
* produce datos consistentes que el módulo `log-processor` puede leer, parsear y transformar.

El archivo final se guarda en un volumen Docker aislado, lo que evita fugas de datos hacia el sistema host.

## 4. Relación con el log-processor

El módulo web es el origen de datos del **log-processor**, encargado de:

* leer estos logs crudos,
* aplicar reglas de anonimización,
* generar la versión sanitizada.

Sin el módulo web, no existiría un flujo de datos realista para validar las operaciones del procesador.


## 5. Razón pedagógica del diseño

El módulo está construido para ofrecer un entorno que refleje **prácticas reales de ingeniería**, donde:

* los servicios producen logs con información sensible,
* los datos deben manejarse con cuidado,
* la estructura del log debe favorecer procesamiento automático,
* y el stack debe ser reproducible mediante Docker.