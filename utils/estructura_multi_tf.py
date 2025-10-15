# utils/estructura_multi_tf.py
from utils.price_utils import get_klines

def estructura_desde_klines(data):
    """
    Procesa las velas y devuelve los precios relevantes (High, Low, Close actuales).
    """
    if not data:
        return {"estado": "sin_datos", "high": None, "low": None, "close": None}

    last = data[-1]
    high = max(v["high"] for v in data[-20:])  # últimos 20
    low = min(v["low"] for v in data[-20:])
    return {
        "estado": "ok",
        "high": round(high, 2),
        "low": round(low, 2),
        "close": round(last["close"], 2)
    }

def analizar_estructura(symbol="BTCUSDT"):
    """
    Analiza estructura multitemporal (H4, H1, M15)
    """
    data_h4 = get_klines(symbol, "4h", 200)
    data_h1 = get_klines(symbol, "1h", 200)
    data_m15 = get_klines(symbol, "15m", 200)

    return {
        "H4 (macro)": estructura_desde_klines(data_h4),
        "H1 (intradía)": estructura_desde_klines(data_h1),
        "M15 (reacción)": estructura_desde_klines(data_m15)
    }
