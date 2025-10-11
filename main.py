# main.py
from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router  # 👈 nuevo import

app = FastAPI(
    title="TESLABTC A.P. API",
    description="Price Action Puro — BTCUSDT NY Session",
    version="2.0.0"
)

@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "✨ TESLABTC A.P. API activa y lista 🚀"}

# Rutas principales
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
app.include_router(analizar_router, prefix="", tags=["TESLABTC"])
