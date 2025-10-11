# utils/price_utils.py
import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

def obtener_precio(simbolo: str) -> float:
    """
    Devuelve el precio actual del par solicitado desde la API pública de Binance.
    Ejemplo: BTCUSDT, ETHUSDT, XAUUSDT.
    """
    try:
        headers = {"User-Agent": "TESLABTC-API/1.0"}
        response = requests.get(f"{BINANCE_URL}?symbol={simbolo.upper()}", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data.get("price", 0.0))
    except Exception as e:
        print(f"[ERROR obtener_precio] {e}")
        return 0.0
