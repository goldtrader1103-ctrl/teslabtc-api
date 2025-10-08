import requests
from datetime import datetime, timedelta, timezone

BINANCE_BASE = "https://api.binance.com"
CG_BASE = "https://api.coingecko.com/api/v3"

COMMON_HEADERS = {
    "User-Agent": "TESLABTC-API/1.0 (+https://teslabtc-api.onrender.com)"
}

def _get(url, params=None, timeout=10):
    try:
        r = requests.get(url, headers=COMMON_HEADERS, params=params or {}, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def obtener_precio():
    # Binance spot price
    data = _get(f"{BINANCE_BASE}/api/v3/ticker/price", {"symbol": "BTCUSDT"}, timeout=10)
    if data and "price" in data:
        try:
            p = float(data["price"])
            if p > 0:
                return round(p, 2)
        except Exception:
            pass
    # Fallback: CoinGecko
    data2 = _get(f"{CG_BASE}/simple/price", {"ids": "bitcoin", "vs_currencies": "usd"}, timeout=10)
    if data2 and "bitcoin" in data2 and "usd" in data2["bitcoin"]:
        try:
            p = float(data2["bitcoin"]["usd"])
            if p > 0:
                return round(p, 2)
        except Exception:
            pass
    return None

def obtener_klines_binance(symbol="BTCUSDT", interval="1h", limit=200):
    kl = _get(f"{BINANCE_BASE}/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit}, timeout=12)
    # Cada kline: [open_time, open, high, low, close, volume, close_time, ...]
    return kl or []

def high_low_anterior_dia(symbol="BTCUSDT"):
    # Trae 2 velas diarias y devuelve high/low del día anterior
    d = obtener_klines_binance(symbol=symbol, interval="1d", limit=2)
    if len(d) >= 2:
        prev = d[-2]
        high = float(prev[2]); low = float(prev[3])
        return round(high, 2), round(low, 2)
    return None, None

def detectar_bos(klines, bullish=True):
    """
    BOS simple:
      - bullish=True: último cierre > máximo de las n velas previas (estructura rompe arriba)
      - bullish=False: último cierre < mínimo de las n velas previas (estructura rompe abajo)
    """
    if len(klines) < 10:
        return False
    closes = [float(k[4]) for k in klines]
    highs  = [float(k[2]) for k in klines]
    lows   = [float(k[3]) for k in klines]
    last_close = closes[-1]
    prev_high  = max(highs[-6:-1])
    prev_low   = min(lows[-6:-1])
    if bullish:
        return last_close > prev_high
    else:
        return last_close < prev_low

def detectar_fvg_m15():
    """
    FVG aproximado M15: busca último gap de 3 velas (A,B,C) donde:
      - Bullish: low(B) > high(A) y low(C) > high(A)  -> hueco sin llenar
      - Bearish: high(B) < low(A) y high(C) < low(A)
    Retorna dict: {"bullish": [(hi, lo), ...], "bearish": [(hi, lo), ...]} con rangos de FVG recientes.
    """
    m15 = obtener_klines_binance(interval="15m", limit=50)
    res = {"bullish": [], "bearish": []}
    if len(m15) < 5:
        return res
    for i in range(2, len(m15)):
        A = m15[i-2]; B = m15[i-1]; C = m15[i]
        A_hi, A_lo = float(A[2]), float(A[3])
        B_hi, B_lo = float(B[2]), float(B[3])
        C_hi, C_lo = float(C[2]), float(C[3])
        # bullish gap (hueco arriba)
        if B_lo > A_hi and C_lo > A_hi:
            # rango no llenado por abajo: [A_hi, min(B_lo, C_lo)]
            res["bullish"].append((round(A_hi,2), round(min(B_lo, C_lo),2)))
        # bearish gap (hueco abajo)
        if B_hi < A_lo and C_hi < A_lo:
            # rango no llenado por arriba: [max(B_hi, C_hi), A_lo]
            res["bearish"].append((round(max(B_hi, C_hi),2), round(A_lo,2)))
    # Dejar solo los últimos 2 por lado para no saturar
    res["bullish"] = res["bullish"][-2:]
    res["bearish"] = res["bearish"][-2:]
    return res

def detectar_ob_h1_h4():
    """
    OB aproximado:
    - Busca la última vela de impulso (cuerpo grande) que precede a un BOS, y usa su rango como OB.
    Simplificado: toma últimas 50 velas de H1 y H4, detecta vela con cuerpo grande y dirección.
    """
    def ob_from_klines(klines, factor=1.5):
        if len(klines) < 20:
            return None, None
        bodies = []
        for k in klines[-20:]:
            o = float(k[1]); c = float(k[4]); h = float(k[2]); l = float(k[3])
            bodies.append(abs(c - o))
        avg_body = sum(bodies)/len(bodies)
        # busca vela con cuerpo > factor*promedio (impulso)
        for k in reversed(klines[-20:]):
            o = float(k[1]); c = float(k[4]); h = float(k[2]); l = float(k[3])
            body = abs(c - o)
            if body > factor*avg_body:
                # OB = rango de esa vela (para PA pura)
                return round(min(o,c),2), round(max(o,c),2)
        return None, None

    h1 = obtener_klines_binance(interval="1h", limit=60)
    h4 = obtener_klines_binance(interval="4h", limit=60)
    h1_ob = ob_from_klines(h1)
    h4_ob = ob_from_klines(h4)
    return {"H1": h1_ob, "H4": h4_ob}

def ahora_col():
    # Hora COL (America/Bogota = UTC-5 sin DST fijo)
    return datetime.now(timezone.utc) - timedelta(hours=5)

def sesion_ny_activa():
    """
    Sesión NY TESLABTC A.P: 07:00–13:30 COL
    """
    t = ahora_col().time()
    start = (7, 0)    # 07:00
    end   = (13, 30)  # 13:30
    if (t.hour, t.minute) < start:
        return False
    if (t.hour, t.minute) > end:
        return False
    if (t.hour, t.minute) == end and t.second > 0:
        return False
    return True

