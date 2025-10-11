# ============================================================
# 🚀 TESLABTC A.P. — API PRINCIPAL
# ============================================================

from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.analizar_router import router as analizar_router
from routers.dashboard_router import router as dashboard_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.ny_session_status import router as ny_session_router   # ✅ nombre correcto

# ============================================================
# ⚙️ CONFIGURACIÓN DE LA APP
# ============================================================

app = FastAPI(
    title="TESLABTC A.P. API",
    description="📊 Price Action Puro — BTCUSDT | Sesión NY (07:00–13:30 COL)",
    version="3.0.0"
)

# ============================================================
# 🔗 REGISTRO DE ROUTERS
# ============================================================

# 📡 Alertas automáticas (PDH/PDL, Asia Range, etc.)
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas TESLABTC"])

# 📈 Análisis principal del mercado
app.include_router(analizar_router, prefix="/analizar", tags=["Análisis TESLABTC"])

# 📊 Dashboard general de rendimiento
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard TESLABTC"])

# ✅ Confirmaciones PA Puro (BOS, POI, FVG)
app.include_router(confirmaciones_router, prefix="/confirmaciones", tags=["Confirmaciones TESLABTC"])

# 🕓 Estado de la sesión de Nueva York (07:00–13:30 COL)
app.include_router(ny_session_router, prefix="/", tags=["Sesión NY TESLABTC"])

# ============================================================
# 🌐 ENDPOINT PRINCIPAL (HOME)
# ============================================================

@app.get("/")
def root():
    return {
        "sistema": "TESLABTC A.P. — Price Action Puro",
        "version": "3.0.0",
        "mensaje": "Bienvenido al motor TESLABTC A.P. (PA Puro + Gestión NY)",
        "rutas_disponibles": {
            "📡 Alertas": "/alertas",
            "📈 Análisis": "/analizar",
            "🧠 Confirmaciones": "/confirmaciones",
            "📊 Dashboard": "/dashboard",
            "🕓 Sesión NY": "/ny-session"
        }
    }
