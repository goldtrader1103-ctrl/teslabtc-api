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
        headers = {"User-Agent": "TESLABTC-API/1.0"}
        response = requests.get(url, headers=headers, timeout=10)

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


def obtener_klines_binance(intervalo="1h", limite=100):
    """
    Obtiene datos históricos de velas (klines) desde Binance.
    intervalos válidos: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d, etc.
    """
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={intervalo}&limit={limite}"
        headers = {"User-Agent": "TESLABTC-API/1.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print("⚠️ Error al obtener klines:", response.text)
            return []

        data = response.json()
        velas = [
            {
                "open_time": datetime.fromtimestamp(v[0] / 1000, pytz.timezone("America/Bogota")),
                "open": float(v[1]),
                "high": float(v[2]),
                "low": float(v[3]),
                "close": float(v[4]),
                "volume": float(v[5]),
            }
            for v in data
        ]

        return velas

    except Exception as e:
        print("⚠️ Error inesperado al obtener klines:", e)
        return []
