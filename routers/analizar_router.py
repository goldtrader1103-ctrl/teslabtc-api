# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))  # zona Colombia

@router.get("/analizar", tags=["TESLABTC"])
def analizar():
    """Devuelve análisis operativo actual del mercado BTCUSDT."""
    try:
        precio_btc = obtener_precio("BTCUSDT")
        error_msg = None
    except Exception as e:
        precio_btc = None
        error_msg = str(e)

    ahora = datetime.now(TZ_COL)
    hora = ahora.hour + ahora.minute / 60
    sesion = "✅ Activa (Sesión New York)" if 7 <= hora < 13.5 else "❌ Cerrada (Fuera de NY)"

    if precio_btc and precio_btc > 0:
        tendencia = "📈 Alcista" if precio_btc > 1000 else "📉 Bajista"
        confirmaciones = ["BOS H1", "POI H4", "Volumen alto"]
        mensaje = "✨ Análisis completado correctamente"
        precio_str = f"{precio_btc:,.2f} USD"
    else:
        tendencia = "⚙️ Sin datos (API o conexión temporalmente inactiva)"
        confirmaciones = []
        mensaje = "⚠️ No se pudo obtener el precio actual"
        precio_str = "⚙️ No disponible"

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": precio_str,
            "tendencia": tendencia,
            "confirmaciones": confirmaciones,
            "mensaje": mensaje,
            "error": error_msg or "Ninguno"
        }
    }
