# main.py
from fastapi import FastAPI
from routers.alertas_router import router as alertas_router

app = FastAPI(
    title="TESLABTC A.P. API",
    description="Price Action Puro — BTCUSDT NY Session",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "✨ TESLABTC A.P. API activa y lista 🚀"}

# 👇 Este prefijo hace que tu ruta sea /alertas/precio/{simbolo}
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
