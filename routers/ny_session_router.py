from fastapi import APIRouter
from datetime import datetime, time

router = APIRouter()

@router.get("/ny-session")
def ny_session():
    """Verifica si estamos dentro de la sesión de Nueva York (7:00–11:30 COL)"""
    ahora = datetime.now().time()
    inicio = time(7, 0)
    fin = time(11, 30)

    dentro_sesion = inicio <= ahora <= fin
    estado = "✅ Dentro de la sesión NY" if dentro_sesion else "🕒 Fuera de la sesión NY"

    return {
        "hora_actual": ahora.strftime("%H:%M:%S"),
        "sesion_NY": estado
    }
