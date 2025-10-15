# ============================================================
# 🧠 TESLABTC.KG — utils/estructura_multi_tf.py (v3.6.0)
# ============================================================
# 1) Lee velas reales desde price_utils (Binance / CoinGecko)
# 2) Calcula estructura por timeframe (H4, H1, M15)
# 3) Devuelve precios high/low/close recientes
# ============================================================

from utils.price_utils import obtener_klines_binance

# ============================================================
# 🔹 PROCESADOR DE ESTRUCTURA SIMPLE
# ============================================================

def _procesar_estructura(data: list):
    """
    Procesa lista de velas [{open, high, low, close}] y devuelve
    los niveles principales de la estructura reciente.
    """
    if not data or len(data) < 5:
        return {"estado": "sin_datos", "high": None, "low": None, "close": None}

    try:
        highs = [float(k["high"]) for k in data[-20:]]
        lows = [float(k["low"]) for k in data[-20:]]
        last_close = float(data[-1]["close"])

        return {
            "estado": "ok",
            "high": round(max(highs), 2),
            "low": round(min(lows), 2),
            "close": round(last_close, 2)
        }
    except Exception as e:
        return {"estado": f"error: {e}", "high": None, "low": None, "close": None}


# ============================================================
# 🔹 ANÁLISIS MULTITEMPORAL
# ============================================================

def analizar_estructura_multi_tf(simbolo="BTCUSDT"):
    """
    Analiza la estructura multitemporal del símbolo dado:
    H4 (macro), H1 (intradía), M15 (reacción).
    """
    # Obtener velas desde Binance o fallback
    h4 = obtener_klines_binance(simbolo, "4h", 120)
    h1 = obtener_klines_binance(simbolo, "1h", 120)
    m15 = obtener_klines_binance(simbolo, "15m", 120)

    estructura = {
        "H4 (macro)": _procesar_estructura(h4),
        "H1 (intradía)": _procesar_estructura(h1),
        "M15 (reacción)": _procesar_estructura(m15)
    }

    return estructura
