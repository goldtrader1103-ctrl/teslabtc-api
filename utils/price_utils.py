# utils/price_utils.py
import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

def obtener_precio(simbolo: str) -> float:
    """
    Obtiene el precio actual del símbolo desde Binance (API pública).
    Compatible con Render (usa headers y timeout).
    """
    try:
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Accept": "application/json"
        }
        url = f"{BINANCE_URL}?symbol={simbolo.upper()}"
        response = requests.get(url, headers=headers, timeout=10)

        # Verifica respuesta válida
        if response.status_code == 200:
            data = response.json()
            if "price" in data:
                return float(data["price"])

        print(f"[WARN] Binance response: {response.status_code} - {response.text}")
        return 0.0

    except Exception as e:
        print(f"[ERROR obtener_precio] {e}")
        return 0.0
