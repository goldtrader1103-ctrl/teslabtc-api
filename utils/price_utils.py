import requests
import pytz
from datetime import datetime

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde la API pública de Binance.
    Incluye manejo de errores, tiempo de espera y compatibilidad con Render.
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        headers = {"User-Agent": "TESLABTC-API/1.0"}
        response = requests.get(url, headers=headers, timeout=10)

        # Si Binance devuelve error o tarda demasiado
        if response.status_code != 200:
            print("⚠️ Error al conectar con Binance:", response.text)
            return None

        data = response.json()
        precio = float(data.get("price", 0))
        if precio <= 0:
            raise ValueError("Precio inválido")
        return round(precio, 2)

    except requests.exceptions.RequestException as e:
        print("⚠️ Error de conexión con Binance:", e)
        return None
    except Exception as e:
        print("⚠️ Error inesperado:", e)
        return None


def obtener_hora_colombia():
    """
    Devuelve la hora actual en Colombia en formato YYYY-MM-DD HH:MM:SS
    """
    tz = pytz.timezone("America/Bogota")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
