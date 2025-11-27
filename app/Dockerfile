FROM python:3.12-slim

# Crear usuario no root
RUN useradd -m appuser

# Crear directorio de la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear directorio para logs crudos dentro del contenedor (el volumen lo usará aquí)
RUN mkdir -p /var/log/app/raw && chown -R appuser:appuser /var/log/app

# Cambiar al usuario no root (obligatorio por el examen)
USER appuser

# Exponer el puerto interno usado por uvicorn
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000"]
