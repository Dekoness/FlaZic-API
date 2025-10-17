FROM python:3.10.9-slim

WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]