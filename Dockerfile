# ============================================================
# 🧠 TESLABTC.KG - Dockerfile para despliegue en Fly.io
# ============================================================

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copia todos los archivos al contenedor
COPY . /app

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de FastAPI
EXPOSE 8080

# Ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
