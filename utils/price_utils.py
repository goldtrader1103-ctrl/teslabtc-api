import requests

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde Binance API con compatibilidad Render.
    """
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    headers = {
        "User-Agent": "TESLABTC-API/1.1",
        "Accept": "application/json",
        "Cache-Control": "no-cache"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        precio = float(data.get("price", 0))
        if precio <= 0:
            raise ValueError("Precio inválido o cero.")
        print(f"✅ Precio Binance obtenido: {precio}")
        return round(precio, 2)

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error HTTP Binance: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error inesperado Binance: {e}")
        return None
