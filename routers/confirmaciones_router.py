from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import obtener_precio

router = APIRouter()

@router.get("/confirmaciones")
def confirmaciones_teslabtc():
    precio_actual = obtener_precio()
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "par": "BTCUSDT",
        "precio_actual": precio_actual,
        "confirmaciones": {
            "Tendencia H4": "✅",
            "BOS M15": "⚠️ Pendiente",
            "POI/OB/FVG": "✅",
            "Retroceso < 61.8%": "✅",
            "Volumen": "⚠️",
            "Sesión NY": "✅"
        },
        "veredicto": "Setup potencial — esperar retroceso M5 (Level Entry).",
        "gestion": "Riesgo 0.5–0.7 %, RRR mínimo 1:3"
    }
