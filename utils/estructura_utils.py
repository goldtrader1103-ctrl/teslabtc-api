import requests
from datetime import datetime, timezone, timedelta

BINANCE_URL = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=200"

def obtener_klines(intervalo="5m", limite=200):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={intervalo}&limit={limite}"
    r = requests.get(url, timeout=10)
    data = r.json()
    return [
        {
            "open_time": datetime.fromtimestamp(x[0] / 1000, tz=timezone(timedelta(hours=-5))),
            "open": float(x[1]),
            "high": float(x[2]),
            "low": float(x[3]),
            "close": float(x[4])
        } for x in data
    ]

def detectar_bos(data):
    """Detecta rupturas de estructura (BOS) básicas."""
    ultima = data[-1]
    max_prev = max(x["high"] for x in data[-6:-1])
    min_prev = min(x["low"] for x in data[-6:-1])
    if ultima["close"] > max_prev:
        return "BOS Alcista"
    elif ultima["close"] < min_prev:
        return "BOS Bajista"
    else:
        return "Sin BOS"

def detectar_barrida(data):
    """Detecta si hubo barrida reciente de altos o bajos."""
    high = [x["high"] for x in data[-10:]]
    low = [x["low"] for x in data[-10:]]
    if high[-1] > max(high[:-1]):
        return "Barrida de Altos"
    elif low[-1] < min(low[:-1]):
        return "Barrida de Bajos"
    return "Sin barrida"
