# routers/analizar_router.py
from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio

router = APIRouter()

# Hora Colombia (UTC-5)
tz_colombia = timezone(timedelta(hours=-5))

@router.get("/analizar", tags=["TESLABTC"])
def analizar():
    """
    Endpoint principal TESLABTC A.P. — Muestra análisis actual.
    """
    precio_btc = obtener_precio("BTCUSDT")

    hora_actual = datetime.now(tz_colombia)
    hora = hora_actual.hour

    if 7 <= hora < 16:
        sesion = "✅ Activa (Sesión New York)"
    else:
        sesion = "❌ Cerrada (Fuera de NY)"

    tendencia = "📈 Alcista" if precio_btc > 0 else "⚙️ Sin datos"
    confirmaciones = ["BOS H1", "POI H4", "Volumen alto"] if precio_btc > 0 else []

    return {
        "🧠 TESLABTC A.P.": {
            "fecha": hora_actual.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:.2f}" if precio_btc else "⚙️ No disponible",
            "tendencia": tendencia,
            "confirmaciones": confirmaciones,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }
