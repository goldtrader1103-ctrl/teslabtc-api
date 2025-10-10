from fastapi import APIRouter
from utils.price_utils import sesion_ny_activa, ahora_col, TZ_COL

router = APIRouter()

@router.get("/ny-session", tags=["TESLABTC"])
def ny_session_status():
    ahora = ahora_col()
    activa = sesion_ny_activa()
    return {
        "timestamp": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "America/Bogota (UTC-5)",
        "sesion_NY_activa": bool(activa),
        "ventana": "07:00–13:30 COL",
    }
