from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/ny-session")
def ny_session_teslabtc():
    hora_actual = datetime.now().hour
    if 13 <= hora_actual <= 17:
        sesion = "✅ Activa (13:30 – 17:00 COL)"
        recomendacion = "Puedes ejecutar setups TESLABTC A.P."
    else:
        sesion = "⏸️ Cerrada"
        recomendacion = "Fuera de horario NY. Evita operar."

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sesion_NY": sesion,
        "recomendacion": recomendacion,
        "nota": "Analiza estructuras antes del inicio de sesión."
    }
