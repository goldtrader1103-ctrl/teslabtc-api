# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio
from utils.estructura_utils import evaluar_estructura

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))

@router.get("/analizar", tags=["TESLABTC"])
def analizar(tipo_operacion: str = "institucional"):
    """
    Devuelve análisis operativo actual del mercado BTCUSDT,
    identificando escenarios conservadores, reentrada y scalping.
    """
    try:
        precio_data = obtener_precio("BTCUSDT")
        precio_btc = precio_data["precio"]
        fuente = precio_data["fuente"]
        error_msg = None
    except Exception as e:
        precio_btc = None
        fuente = "Ninguna"
        error_msg = str(e)

    ahora = datetime.now(TZ_COL)
    hora = ahora.hour + ahora.minute / 60
    sesion = "✅ Activa (Sesión New York)" if 7 <= hora < 13.5 else "❌ Cerrada (Fuera de NY)"

    # ===============================
    # Simulación de lectura estructural real (por ahora mock)
    # ===============================
    H4_dir = "bajista"
    H1_dir = "bajista"
    M15_dir = "alcista"  # microimpulso de retroceso

    estructura = evaluar_estructura(H4_dir, H1_dir, M15_dir, tipo_operacion)

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:,.2f} USD" if precio_btc else "⚙️ No disponible",
            "fuente": fuente,
            "estructura": estructura,
            "mensaje": "✨ Análisis completado correctamente" if not error_msg else "⚠️ Error parcial",
            "error": error_msg or "Ninguno"
        }
    }
