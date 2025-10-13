# ============================================================
# 🚀 TESLABTC.KG – API PRINCIPAL
# ============================================================

from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.dashboard_router import router as dashboard_router
from routers.ny_session_status import router as ny_session_router

# ============================================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ============================================================

app = FastAPI(
    title="TESLABTC.KG",
    description=(
        "API de análisis operativo para el sistema TESLABTC.KG – "
        "Basado en Price Action puro, liquidez, BOS, POI, y sesión de Nueva York."
    ),
    version="3.0.0"
)

# ============================================================
# 🔗 REGISTRO DE ROUTERS
# ============================================================

app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
app.include_router(analizar_router, prefix="/analizar", tags=["TESLABTC"])
app.include_router(confirmaciones_router, prefix="/confirmaciones", tags=["TESLABTC"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard TESLABTC"])
app.include_router(ny_session_router, prefix="/ny-session", tags=["TESLABTC"])

# ============================================================
# 🌐 ENDPOINT DE ESTADO GENERAL
# ============================================================

@app.get("/")
def estado_general():
    """
    Verifica si la API TESLABTC.KG está funcionando correctamente.
    """
    return {
        "estado": "✅ TESLABTC.KG activo",
        "mensaje": "API funcionando correctamente",
        "version": "3.0.0",
        "autor": "Katherinne Galvis"
    }
