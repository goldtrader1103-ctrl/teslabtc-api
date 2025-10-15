# ============================================================
# 🧠 TESLABTC.KG — Dockerfile oficial (v3.6.3)
# Author: Katherinne Galvis
# Despliegue: Fly.io
# ============================================================

# Imagen base oficial de Python 3.12 optimizada
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Actualizar pip y dependencias del sistema
RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV TZ=America/Bogota

# Exponer el puerto correcto para Fly.io
EXPOSE 8080

# Comando de arranque (Gunicorn no es necesario; Uvicorn directo)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
