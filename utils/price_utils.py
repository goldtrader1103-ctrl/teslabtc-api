# utils/price_utils.py
import requests

# ✅ API alternativa (idéntica estructura que la de Binance oficial)
BINANCE_URL = "https://data-api.binance.vision/api/v3/ticker/price"

def obtener_precio(simbolo: str) -> float:
    """
    Obtiene el precio actual del símbolo desde la API pública de Binance Vision.
    Compatible con Render (evita bloqueos del dominio principal).
    """
    try:
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Accept": "application/json"
        }
        response = requests.get(
            f"{BINANCE_URL}?symbol={simbolo.upper()}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "price" in data:
                return float(data["price"])
        print(f"[WARN] BinanceVision respondió {response.status_code}: {response.text}")
        return 0.0

    except Exception as e:
        print(f"[ERROR obtener_precio] {e}")
        return 0.0

