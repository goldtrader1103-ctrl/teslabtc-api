import requests
import pytz
from datetime import datetime

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde la API pública de Binance.
    Retorna un número decimal (float) con el precio actual.
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        precio = float(data["price"])
        return round(precio, 2)
    except Exception as e:
        print("Error al obtener precio de Binance:", e)
        return None


def obtener_hora_colombia():
    """
    Devuelve la hora actual en Colombia en formato YYYY-MM-DD HH:MM:SS
    """
    tz = pytz.timezone("America/Bogota")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
