import requests

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde Binance API.
    Maneja errores, timeouts y cabeceras para compatibilidad con Render.
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print("⚠️ Error Binance:", response.text)
            return None

        data = response.json()
        precio = float(data.get("price", 0))
        if precio <= 0:
            raise ValueError("Precio inválido")
        return round(precio, 2)

    except Exception as e:
        print("⚠️ Error al obtener precio:", e)
        return None
