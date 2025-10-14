# ============================================================
# 🧠 TESLABTC.KG - Dockerfile para despliegue en Fly.io
# ============================================================

FROM python:3.12-slim

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copiar archivos al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto FastAPI
EXPOSE 8080

# Comando para ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
