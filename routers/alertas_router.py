from fastapi import APIRouter
from datetime import datetime
import requests
import pytz
import os

router = APIRouter()

# URL sonido de alerta
ALERTA_SONIDO_URL = "https://teslabtc-api.onrender.com/static/beep.mp3"

# Configurar zona horaria Colombia
tz_col = pytz.timezone("America/Bogota")

# Rango NY (7:00–13:30 COL)
HORA_INICIO_NY = (7, 0)
HORA_FIN_NY = (13, 30)

def sesion_ny_activa():
    """Verifica si estamos dentro de la sesión NY"""
    ahora = datetime.now(tz_col)
    inicio = ahora.replace(hour=HORA_INICIO_NY[0], minute=HORA_INICIO_NY[1])
    fin = ahora.replace(hour=HORA_FIN_NY[0], minute=HORA_FIN_NY[1])
    return inicio <= ahora <= fin

@router.get("/alertas")
def alertas_teslabtc():
    """
    Endpoint principal para alertas TESLABTC A.P.
    Obtiene el precio actual de Binance, verifica zonas de liquidez
    y activa alerta si hay toque de PDH/PDL.
    """

    # Precio actual desde Binance
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    try:
        data = requests.get(url, timeout=5).json()
        precio_actual = float(data["price"])
    except Exception:
        return {"error": "No se pudo obtener el precio de Binance."}

    # Simular niveles de referencia (idealmente vienen del análisis)
    pdh = 126000  # High del día anterior
    pdl = 124000  # Low del día anterior

    # Comprobación de toque de liquidez
    alerta = None
    if precio_actual >= pdh:
        alerta = f"🔴 Precio tocó PDH ({pdh}) — posible reversión o barrida de liquidez"
    elif precio_actual <= pdl:
        alerta = f"🟢 Precio tocó PDL ({pdl}) — posible reacción alcista"

    # Sesión actual
    sesion = "✅ Activa (7:00–13:30 COL)" if sesion_ny_activa() else "❌ Fuera de sesión NY"

    # Resultado final
    return {
        "timestamp": datetime.now(tz_col).strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio_actual,
        "pdh": pdh,
        "pdl": pdl,
        "sesion_NY": sesion,
        "alerta": alerta if alerta else "Sin alertas activas",
        "estado_alerta": "ACTIVA" if alerta else "SILENCIO",
        "alert_sound": ALERTA_SONIDO_URL if alerta else None,
        "mensaje": "🧠 TESLABTC A.P. monitoreando zonas de liquidez en tiempo real"
    }
