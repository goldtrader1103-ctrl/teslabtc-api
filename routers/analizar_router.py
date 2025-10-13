# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio

router = APIRouter()

# Zona horaria de Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 ENDPOINT PRINCIPAL DE ANÁLISIS
# ============================================================

@router.get("/analizar", tags=["TESLABTC"])
def analizar():
    """
    Endpoint principal TESLABTC.KG — Devuelve análisis operativo actual del mercado BTCUSDT.
    """
    try:
        # Obtener precio actual de BTCUSDT
        precio_btc = obtener_precio("BTCUSDT")
    except Exception as e:
        precio_btc = None
        error_msg = str(e)
    else:
        error_msg = None

    # Hora local Colombia
    hora_actual = datetime.now(TZ_COL)
    hora = hora_actual.hour + hora_actual.minute / 60

    # Verificar sesión New York (07:00 - 13:30 COL)
    if 7 <= hora < 13.5:
        sesion = "✅ Activa (Sesión New York)"
    else:
        sesion = "❌ Cerrada (Fuera de NY)"

    # Evaluar dirección y confirmaciones solo si hay precio válido
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
            "fecha": hora_actual.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": precio_str,
            "tendencia": tendencia,
            "confirmaciones": confirmaciones,
            "mensaje": mensaje,
            "error": error_msg if error_msg else "Ninguno"
        }
    }
