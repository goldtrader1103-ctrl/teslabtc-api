from utils.price_utils import detectar_estructura, obtener_klines_binance

def analisis_multi_tf():
    """
    TESLABTC A.P. — Análisis multitemporal (H1, M15, M5).
    """
    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)
    velas_m5 = obtener_klines_binance("5m", 150)

    estr_h1 = detectar_estructura(velas_h1, lookback=20)
    estr_m15 = detectar_estructura(velas_m15, lookback=20)
    estr_m5 = detectar_estructura(velas_m5, lookback=20)

    return {
        "H1": estr_h1,
        "M15": estr_m15,
        "M5": estr_m5
    }
