import requests

def obtener_precio():
    """
    Obtiene el precio actual de BTCUSDT desde la API pública de Binance.
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

    except requests.exceptions.Timeout:
        print("⚠️ Binance no respondió a tiempo.")
        return None
    except requests.exceptions.RequestException as e:
        print("⚠️ Error de conexión con Binance:", e)
        return None
    except Exception as e:
        print("⚠️ Error inesperado al obtener precio:", e)
        return None

