from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.ny_router import router as ny_router   # 👈 o ny_session_status según tu nombre

app = FastAPI(
    title="TESLABTC A.P. API",
    description="Price Action Puro — BTCUSDT NY Session",
    version="3.0.0"
)

# Incluir routers
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
app.include_router(analizar_router, prefix="/analizar", tags=["TESLABTC"])
app.include_router(ny_router, prefix="/", tags=["TESLABTC"])  # 👈 este es el que activa /ny-session

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a TESLABTC A.P. API"}
