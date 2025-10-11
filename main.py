# ============================================================
# 🚀 TESLABTC A.P. — API PRINCIPAL
# ============================================================

from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.dashboard_router import router as dashboard_router
from routers.ny_session_status import router as ny_session_router   # ✅ router NY corregido

# ============================================================
# APP PRINCIPAL
# ============================================================

app = FastAPI(
    title="TESLABTC A.P. API",
    description="Price Action Puro — BTCUSDT NY Session",
    version="3.0.0"
)

# ============================================================
# INCLUSIÓN DE ROUTERS
# ============================================================

app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
app.include_router(analizar_router, prefix="/analizar", tags=["Análisis"])
app.include_router(confirmaciones_router, prefix="/confirmaciones", tags=["Confirmaciones"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ny_session_router, prefix="/", tags=["TESLABTC"])  # ✅ activa /ny-session

# ============================================================
# ENDPOINT RAÍZ
# ============================================================

@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a TESLABTC A.P. API — Price Action Puro",
        "endpoints_disponibles": {
            "alertas": "/alertas",
            "analizar": "/analizar",
            "confirmaciones": "/confirmaciones",
            "dashboard": "/dashboard",
            "sesion_NY": "/ny-session"
        }
    }
