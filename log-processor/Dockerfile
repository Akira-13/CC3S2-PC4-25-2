FROM python:3.12-slim

# RUN useradd -m processoruser

WORKDIR /processor

# Copiar requirements e instalar 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del processor
COPY . .

# Cambiar propietario de la carpeta
#RUN chown -R processoruser:processoruser /processor

#USER processoruser

CMD ["python", "processor.py"]
