# ============================================================
# 🐳 TESLABTC.KG — Dockerfile (v3.6.0 PRO STABLE)
# Compatible con Fly.io y Uvicorn 24/7
# ============================================================

FROM python:3.12-slim

# ===============================
# 🔧 Variables de entorno
# ===============================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=2

# ===============================
# 📁 Directorio de trabajo
# ===============================
WORKDIR /app

# ===============================
# 📦 Instalación de dependencias
# ===============================
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===============================
# 📄 Copiar el código de la API
# ===============================
COPY . .

# ===============================
# 🌍 Puerto para Fly.io
# ===============================
EXPOSE 8080

# ===============================
# 🚀 Comando de inicio del servidor
# ===============================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
