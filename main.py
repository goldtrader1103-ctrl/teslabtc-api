from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.dashboard_router import router as dashboard_router
from routers.ny_session_status import router as ny_session_router

# ===============================================
# 🚀 TESLABTC A.P. — API de Análisis en Vivo
# ===============================================

app = FastAPI(
    title="TESLABTC A.P.",
    description=(
        "API de análisis operativo para el sistema TESLABTC A.P. — "
        "Basado en Price Action puro, liquidez, BOS, POI, y sesión de Nueva York."
    ),
    version="3.0.0"
)

# ===============================================
# 🔹 Registro de Routers
# ===============================================
# ✅ OJO: No usar 'prefix="/"', eso causa AssertionError.
app.include_router(alertas_router)
app.include_router(analizar_router)
app.include_router(confirmaciones_router)
app.include_router(dashboard_router)
app.include_router(ny_session_router)

# ===============================================
# 🏁 Ruta raíz — Verificación rápida
# ===============================================
@app.get("/")
def root():
    return {
        "estado": "✅ TESLABTC A.P. activo",
        "mensaje": "API funcionando correctamente",
        "version": "3.0.0",
        "autor": "Leidy Galvis"
    }
