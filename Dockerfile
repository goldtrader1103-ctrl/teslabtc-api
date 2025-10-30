# ============================================================
# 🚀 TESLABTC.KG — Dockerfile SOLO API (FASTAPI)
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Copiar todo el proyecto de la API
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpeta persistente
RUN mkdir -p /app/data

# Exponer el puerto de la API
EXPOSE 8080

# Comando de ejecución (solo la API)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
