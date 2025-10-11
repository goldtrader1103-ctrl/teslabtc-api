# ============================================================
# ✅ TESLABTC A.P. — Estado de la Sesión NY
# ============================================================

from fastapi import APIRouter
from utils.price_utils import sesion_ny_activa, TZ_COL
from datetime import datetime

router = APIRouter()

@router.get("/ny-session", tags=["TESLABTC"])
def ny_session_status():
    """Estado actual de la sesión de Nueva York (TESLABTC A.P.)"""
    ahora = datetime.now(TZ_COL)
    activa = sesion_ny_activa(ahora)
    return {
        "timestamp": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "America/Bogota (UTC-5)",
        "sesion_NY_activa": bool(activa),
        "ventana": "07:00–13:30 COL",
        "mensaje": "✅ Activa" if activa else "❌ Fuera de sesión"
    }

