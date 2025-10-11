# utils/price_utils.py
import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

def obtener_precio(simbolo: str) -> float:
    """
    Obtiene el precio actual del símbolo desde Binance (API pública).
    Compatible con Render y FastAPI TESLABTC A.P.
    """
    try:
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Accept": "application/json"
        }
        response = requests.get(
            f"{BINANCE_URL}?symbol={simbolo.upper()}",
            headers=headers,
            timeout=15
        )

        # Si Binance responde correctamente
        if response.status_code == 200:
            data = response.json()
            return float(data.get("price", 0.0))
        else:
            print(f"[ERROR Binance] Código: {response.status_code}")
            return 0.0

    except requests.exceptions.RequestException as e:
        print(f"[ERROR conexión Binance] {e}")
        return 0.0
