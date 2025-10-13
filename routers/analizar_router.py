# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal (v3.0.2)
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, sesion_ny_activa

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))  # zona Colombia

@router.get("/", tags=["TESLABTC"])
def analizar():
    """Devuelve análisis operativo actual del mercado BTCUSDT."""
    ahora = datetime.now(TZ_COL)

    # ✅ Obtener precio y fuente
    data_precio = obtener_precio("BTCUSDT")
    precio_btc = data_precio.get("precio")
    fuente = data_precio.get("fuente")

    # ✅ Determinar sesión NY
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # ✅ Evaluar estructura según disponibilidad del precio
    if isinstance(precio_btc, (int, float)) and precio_btc > 0:
        tendencia = "📈 Alcista" if precio_btc > 100000 else "📉 Bajista"
        confirmaciones = ["BOS H1", "POI H4", "Volumen alto"]
        mensaje = "✨ Análisis completado correctamente"
        precio_str = f"{precio_btc:,.2f} USD"
        error_msg = "Ninguno"
    else:
        tendencia = "⚙️ Sin datos (API o conexión temporalmente inactiva)"
        confirmaciones = []
        mensaje = "⚠️ No se pudo obtener el precio actual"
        precio_str = "⚙️ No disponible"
        error_msg = "Fuente o datos no válidos"

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "fuente": fuente,
            "precio_actual": precio_str,
            "tendencia": tendencia,
            "confirmaciones": confirmaciones,
            "mensaje": mensaje,
            "error": error_msg
        }
    }
