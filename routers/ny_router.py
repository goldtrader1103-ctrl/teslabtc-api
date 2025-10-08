from fastapi import APIRouter
from utils.price_utils import obtener_hora_colombia
import pytz
from datetime import datetime

router = APIRouter()

@router.get("/ny-session")
def verificar_sesion_ny():
    """
    Verifica si actualmente estamos dentro de la sesión de Nueva York (7:00–13:00 hora Colombia).
    """
    tz = pytz.timezone("America/Bogota")
    hora_actual = datetime.now(tz)
    hora_formateada = obtener_hora_colombia()

    inicio_ny = hora_actual.replace(hour=7, minute=0, second=0)
fin_ny = hora_actual.replace(hour=13, minute=30, second=0)


    if inicio_ny <= hora_actual <= fin_ny:
        estado = "✅ Activa (7:00–13:00 COL)"
        recomendacion = "Puedes ejecutar setups TESLABTC A.P."
    else:
        estado = "🕓 Fuera de sesión (7:00–13:00 COL)"
        recomendacion = "Evita operar; espera la próxima sesión de Nueva York."

    return {
        "timestamp": hora_formateada,
        "sesion_NY": estado,
        "recomendacion": recomendacion,
        "nota": "Si faltan confirmaciones, espera BOS M15 o retroceso M5."
    }
