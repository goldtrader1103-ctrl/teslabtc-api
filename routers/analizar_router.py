# routers/analizar_router.py
from fastapi import APIRouter
from datetime import datetime
import pytz
from utils.price_utils import obtener_precio

router = APIRouter()

# Configuración de zona horaria Colombia
tz_colombia = pytz.timezone("America/Bogota")

@router.get("/analizar", tags=["TESLABTC"])
def analizar():
    """
    Endpoint principal de TESLABTC A.P.
    Devuelve:
      - Precio actual BTCUSDT
      - Estado de la sesión NY
      - Tendencia actual (placeholder)
      - Confirmaciones activas (placeholder)
    """
    # --- Precio actual ---
    precio_btc = obtener_precio("BTCUSDT")

    # --- Estado de sesión NY ---
    hora_actual = datetime.now(tz_colombia)
    hora = hora_actual.hour
    if 7 <= hora < 16:
        sesion = "✅ Activa (Sesión New York)"
    else:
        sesion = "❌ Cerrada (Fuera de NY)"

    # --- Placeholder de análisis técnico ---
    tendencia = "📈 Alcista" if precio_btc > 0 else "⚙️ Sin datos"
    confirmaciones = ["BOS H1", "POI H4", "Volumen alto"] if precio_btc > 0 else []

    # --- Construcción de respuesta ---
    resultado = {
        "🧠 TESLABTC A.P.": {
            "fecha": hora_actual.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:.2f}" if precio_btc else "⚙️ No disponible",
            "tendencia": tendencia,
            "confirmaciones": confirmaciones,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }

    return resultado
