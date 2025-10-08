from fastapi import APIRouter
from utils.price_utils import sesion_ny_activa, ahora_col

router = APIRouter()

@router.get("/ny-session")
def ny_session():
    sesion = "✅ Activa (07:00–13:30 COL)" if sesion_ny_activa() else "❌ Fuera de sesión NY"
    return {
        "timestamp": ahora_col().strftime("%Y-%m-%d %H:%M:%S"),
        "sesion_NY": sesion,
        "nota": "Operar TESLABTC A.P. preferiblemente dentro de sesión NY (07:00–13:30 COL)."
    }
