# main.py
from fastapi import FastAPI
from routers.alertas_router import router as alertas_router

# 🚀 Instancia principal de la aplicación FastAPI
app = FastAPI(
    title="TESLABTC A.P. API",
    description="Price Action Puro — BTCUSDT NY Session",
    version="1.0.0"
)

# 🌐 Ruta raíz de prueba
@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "✨ TESLABTC A.P. API activa y lista 🚀"}

# 🔔 Incluimos el router de alertas (precio en vivo desde Binance)
# Esto hace que el endpoint quede como:
# 👉 /alertas/precio/BTCUSDT
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
