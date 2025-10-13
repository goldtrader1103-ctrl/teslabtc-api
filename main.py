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
        "API de análisis operativo para el sistema TESLABTC.KG — "
        "Basado en Price Action Puro, liquidez, BOS, POI y sesión de Nueva York."
    ),
    version="3.0.0"
)

# ============================================================
# 🔗 REGISTRO DE ROUTERS
# ============================================================
# Nota: los routers internos están definidos con ruta "/".
app.include_router(analizar_router, tags=["TESLABTC"])                      # /analizar
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])     # /alertas/...
app.include_router(confirmaciones_router, prefix="/confirmaciones", tags=["TESLABTC"])  # /confirmaciones
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard TESLABTC"])   # /dashboard
app.include_router(ny_session_router, prefix="/ny-session", tags=["TESLABTC"])           # /ny-session

# ============================================================
# 🌐 ENDPOINT DE ESTADO GENERAL
# ============================================================

@app.get("/")
def estado_general():
    """Verifica si la API TESLABTC.KG está funcionando correctamente."""
    return {
        "estado": "✅ TESLABTC.KG activo",
        "mensaje": "API funcionando correctamente",
        "version": "3.0.0",
        "autor": "Katherinne Galvis"
    }

# ============================================================
# 🧪 ENDPOINTS DE DIAGNÓSTICO (ayuda a detectar bloqueos del host)
# ============================================================
import requests

@app.get("/test-binance")
def test_binance():
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=5,
            headers={"User-Agent": "teslabtc-kg/1.0"}
        )
        return {"status": r.status_code, "body": r.json()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-price")
def test_price():
    from utils.price_utils import obtener_precio
    p = obtener_precio("BTCUSDT")
    return {"precio": p}
