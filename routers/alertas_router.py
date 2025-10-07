from fastapi import APIRouter
from datetime import datetime
import pytz
import requests

router = APIRouter(prefix="/alertas", tags=["Alertas TESLABTC"])

# Configuración de zona horaria (Colombia)
tz = pytz.timezone("America/Bogota")

# Función para obtener el precio real de BTC desde Binance
def obtener_precio_btc():
    try:
        resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = resp.json()
        return float(data["price"])
    except Exception:
        return None

# Definimos las zonas de interés (puedes modificarlas según tus análisis)
ZONAS_LIQUIDEZ = {
    "PDH": 126000,  # Previous Day High
    "PDL": 122000,  # Previous Day Low
}

@router.get("/")
def alertas_teslabtc():
    """Genera alertas automáticas de TESLABTC A.P según precio y sesión NY."""
    hora_actual = datetime.now(tz)
    precio_actual = obtener_precio_btc()

    if not precio_actual:
        return {"error": "No se pudo obtener el precio real de BTCUSDT."}

    # Verificar si estamos en sesión NY (7:00–13:30 COL)
    hora_num = hora_actual.hour + hora_actual.minute / 60
    sesion_ny = 7 <= hora_num <= 13.5
    estado_sesion = "✅ Activa (7:00–13:30 COL)" if sesion_ny else "❌ Fuera de sesión NY"

    # Detectar si el precio toca zonas de liquidez
    alerta = None
    if precio_actual >= ZONAS_LIQUIDEZ["PDH"]:
        alerta = f"🔴 BTCUSDT tocó PDH ({ZONAS_LIQUIDEZ['PDH']}) — posible barrida de liquidez superior."
    elif precio_actual <= ZONAS_LIQUIDEZ["PDL"]:
        alerta = f"🔵 BTCUSDT tocó PDL ({ZONAS_LIQUIDEZ['PDL']}) — posible barrida de liquidez inferior."
    else:
        alerta = "🟢 Sin alertas activas."

    return {
        "timestamp": hora_actual.strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio_actual,
        "sesion_NY": estado_sesion,
        "alerta": alerta,
        "estado_alerta": "ACTIVA" if "tocó" in alerta else "SILENCIO",
        "confirmaciones": {
            "Sesión NY": "✅" if sesion_ny else "❌",
            "Zonas de Liquidez": ZONAS_LIQUIDEZ,
        },
        "mensaje": "📊 TESLABTC A.P: Monitoreo automático de zonas y sesión NY listo."
    }
