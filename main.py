# ============================================================
# 🚀 TESLABTC A.P. — API Principal
# ============================================================
# Descripción:
#   API para análisis de mercado BTCUSDT basada en Price Action Puro.
#   Incluye módulos de análisis, alertas y sesión NY.
# ============================================================

from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.ny_session_status import router as ny_session_router

# --- Instancia principal de la aplicación FastAPI ---
app = FastAPI(
    title="TESLABTC A.P. — Dashboard API",
    description=(
        "Sistema de análisis estructural TESLABTC A.P. (Price Action Puro) "
        "para BTCUSDT — incluye detección de BOS, confirmaciones, alertas "
        "y estado de sesión NY (07:00–13:30 COL)."
    ),
    version="3.0.0",
    contact={
        "name": "Katherinne Galvis",
        "email": "goldtrader1103@gmail.com",
    },
)

# ============================================================
# 🔹 REGISTRO DE ROUTERS
# ============================================================

# --- Rutas principales TESLABTC ---
app.include_router(analizar_router, prefix="/analizar", tags=["Análisis TESLABTC"])
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas TESLABTC"])
app.include_router(ny_session_router, prefix="/ny-session", tags=["Sesión NY"])

# ============================================================
# 🔹 ENDPOINT RAÍZ
# ============================================================
@app.get("/", tags=["Root"])
def root():
    """
    Endpoint raíz para verificar el estado de la API.
    """
    return {
        "mensaje": "✅ API TESLABTC A.P. operativa",
        "endpoints_disponibles": {
            "Análisis": "/analizar",
            "Alertas": "/alertas",
            "Sesión NY": "/ny-session"
        }
    }

# ============================================================
# 🔹 EJECUCIÓN LOCAL (solo para desarrollo)
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
