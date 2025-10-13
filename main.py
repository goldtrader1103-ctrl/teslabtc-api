# ============================================================
# 🚀 TESLABTC.KG — FastAPI principal
# ============================================================

from fastapi import FastAPI
from routers.analizar_router import router as analizar_router

app = FastAPI(
    title="TESLABTC.KG Dashboard",
    description="PA pura — estructura, liquidez y POI (OB/FVG) para BTCUSDT. Sesión NY 07:00–13:30 COL.",
    version="3.0.2"
)

# Incluye routers
app.include_router(analizar_router, prefix="/analizar", tags=["TESLABTC"])

@app.get("/", tags=["Root"])
def root():
    return {
        "TESLABTC.KG": "API operativa ✅",
        "version": "3.0.2",
        "autor": "Katherinne Galvis"
    }
