import requests
import time

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde la API pública de Binance.
    Incluye 3 intentos de reconexión con espera incremental.
    """
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    headers = {"User-Agent": "TESLABTC-API/1.1"}
    intentos = 3

    for intento in range(intentos):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                precio = float(data.get("price", 0))
                if precio > 0:
                    return round(precio, 2)
            print(f"⚠️ Intento {intento+1}: Binance no respondió correctamente ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Intento {intento+1}: error de conexión {e}")
        time.sleep(2 * (intento + 1))
    return None


def obtener_hora_colombia():
    from datetime import datetime
    import pytz
    tz = pytz.timezone("America/Bogota")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

