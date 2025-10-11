# --- Importaciones base ---
import requests
from datetime import datetime, time
import pytz

# Zona horaria Colombia (UTC-5)
TZ_COL = pytz.timezone("America/Bogota")

# --- 🔹 NUEVA FUNCIÓN: obtener_precio() ---
def obtener_precio(simbolo: str = "BTCUSDT") -> float:
    """
    Obtiene el precio actual del par solicitado desde la API pública de Binance.
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo.upper()}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"[Error obtener_precio] {e}")
        return None


# --- 🔹 Función para validar sesión NY ---
def sesion_ny_activa(ahora: datetime = None) -> bool:
    """
    Determina si la sesión de Nueva York está activa.
    Horario oficial TESLABTC A.P.: 07:00–13:30 COL (lunes a viernes)
    """
    if ahora is None:
        ahora = datetime.now(TZ_COL)

    dia_semana = ahora.weekday()  # 0 = lunes, 6 = domingo
    hora_actual = ahora.time()

    inicio = time(7, 0)
    fin = time(13, 30)

    # Si es sábado (5) o domingo (6), sesión cerrada
    if dia_semana >= 5:
        return False

    # Si está dentro del rango horario, sesión activa
    return inicio <= hora_actual <= fin


