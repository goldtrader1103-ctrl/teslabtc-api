# utils/price_utils.py
"""
Módulo para obtener precios en tiempo real desde Binance (principal)
y Coinbase (respaldo automático) para el sistema TESLABTC A.P.

Compatible con despliegues en Render y entornos FastAPI.
"""

import requests

def obtener_precio(simbolo: str) -> float:
    """
    Devuelve el precio actual del par solicitado.
    Intenta primero desde Binance; si falla, usa Coinbase como respaldo.

    Parámetro:
        simbolo (str): Par de trading, ej. 'BTCUSDT', 'ETHUSDT', 'XAUUSDT'
    Retorna:
        float: Precio actual del activo. Si falla, devuelve 0.0
    """
    simbolo = simbolo.upper()

    # --- 1️⃣ Intento con Binance ---
    try:
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Accept": "application/json"
        }
        binance_url = f"https://data-api.binance.vision/api/v3/ticker/price?symbol={simbolo}"
        response = requests.get(binance_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "price" in data:
                print(f"[INFO] Precio obtenido desde Binance: {simbolo}")
                return float(data["price"])
        else:
            print(f"[WARN] Binance devolvió código {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[ERROR] Binance no disponible: {e}")

    # --- 2️⃣ Respaldo con Coinbase ---
    try:
        # Solo BTCUSDT tiene equivalencia directa BTC-USD
        if simbolo == "BTCUSDT":
            coinbase_url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
            response = requests.get(coinbase_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = float(data["data"]["amount"])
                print(f"[INFO] Precio obtenido desde Coinbase (respaldo): {price}")
                return price
            else:
                print(f"[WARN] Coinbase devolvió código {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[ERROR] Coinbase también falló: {e}")

    # --- 3️⃣ Si todo falla ---
    print(f"[FAIL] No se pudo obtener precio de {simbolo} desde ninguna fuente.")
    return 0.0

