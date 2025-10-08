# utils/price_utils.py
import requests

def obtener_precio(simbolo: str):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo.upper()}"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])
