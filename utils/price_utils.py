import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

# Zona horaria Colombia (UTC-5) sin DST
TZ_COL = timezone(timedelta(hours=-5))


def _req(url: str, params: Optional[dict] = None, timeout: int = 10):
    headers = {"User-Agent": "TESLABTC-API/1.1"}
    return requests.get(url, params=params or {}, headers=headers, timeout=timeout)


def obtener_precio() -> Optional[float]:
    """
    Precio actual BTCUSDT desde Binance.
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        r = _req(url, {"symbol": "BTCUSDT"}, timeout=10)
        if r.status_code != 200:
            print("⚠️ Binance ticker error:", r.text)
            return None
        data = r.json()
        px = float(data.get("price", 0))
        return round(px, 2) if px > 0 else None
    except Exception as e:
        print("⚠️ obtener_precio error:", e)
        return None


def obtener_klines_binance(interval: str, limit: int = 200) -> List[Dict]:
    """
    Velas de Binance: open_time, open, high, low, close, volume, close_time (en tz COL).
    interval: '1h', '15m', '5m', etc.
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        r = _req(url, {"symbol": "BTCUSDT", "interval": interval, "limit": limit}, timeout=12)
        if r.status_code != 200:
            print("⚠️ Binance klines error:", r.text)
            return []
        raw = r.json()
        out = []
        for k in raw:
            # k = [openTime, open, high, low, close, volume, closeTime, ...]
            o_time_utc = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc)
            c_time_utc = datetime.fromtimestamp(k[6] / 1000, tz=timezone.utc)
            out.append({
                "open_time": o_time_utc.astimezone(TZ_COL),
                "close_time": c_time_utc.astimezone(TZ_COL),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            })
        return out
    except Exception as e:
        print("⚠️ obtener_klines_binance error:", e)
        return []


def _highs_lows(velas: List[Dict]):
    if not velas:
        return None, None
    return max(v["high"] for v in velas), min(v["low"] for v in velas)


def _pdh_pdl(velas_1h: List[Dict]):
    """
    PDH/PDL del día anterior en COL.
    """
    if not velas_1h:
        return None, None

    hoy = datetime.now(TZ_COL).date()
    ayer = hoy - timedelta(days=1)

    velas_ayer = [v for v in velas_1h if v["open_time"].date() == ayer]
    if not velas_ayer:
        return None, None

    pdh = max(v["high"] for v in velas_ayer)
    pdl = min(v["low"] for v in velas_ayer)
    return pdh, pdl


def _asia_range(velas_15m: List[Dict]):
    """
    Rango aproximado de ASIA (COL):
    - tramo 19:00–23:59 del día anterior
    - + tramo 00:00–03:00 del día actual
    Se toma el bloque más reciente que cruce medianoche.
    """
    if not velas_15m:
        return None, None

    ahora = datetime.now(TZ_COL)
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)

    def hora_en(h: int, m: int = 0, d: datetime = None):
        base = datetime.now(TZ_COL)
        d = d or base
        return d.replace(hour=h, minute=m, second=0, microsecond=0)

    inicio_a = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=19)  # 19:00 ayer
    fin_a_1 = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=23, minute=59)
    fin_a_2 = datetime.combine(hoy, datetime.min.time(), tzinfo=TZ_COL).replace(hour=3)   # 03:00 hoy

    tramo1 = [v for v in velas_15m if inicio_a <= v["open_time"] <= fin_a_1]
    tramo2 = [v for v in velas_15m if v["open_time"].date() == hoy and v["open_time"].hour <= 3]

    bloque = tramo1 + tramo2
    if not bloque:
        return None, None

    high_a = max(v["high"] for v in bloque)
    low_a = min(v["low"] for v in bloque)
    return high_a, low_a


def detectar_estructura(velas: List[Dict], lookback: int = 20) -> Dict:
    """
    Detección simple de estructura (PA puro):
    - BOS: close actual > máx prev (lookback) o < mín prev
    - Barridas: high actual > máx prev sin cierre por encima (alcista) / low actual < mín prev sin cierre por debajo (bajista).
    - Rango: si no hay BOS.
    """
    if len(velas) < max(lookback + 1, 5):
        return {
            "BOS": False,
            "tipo_BOS": None,
            "rango": True,
            "barrida_alcista": False,
            "barrida_bajista": False
        }

    highs = [v["high"] for v in velas]
    lows = [v["low"] for v in velas]
    closes = [v["close"] for v in velas]

    prev_max = max(highs[-(lookback + 1):-1])
    prev_min = min(lows[-(lookback + 1):-1])

    high_actual = highs[-1]
    low_actual = lows[-1]
    close_actual = closes[-1]

    bos_up = close_actual > prev_max
    bos_dn = close_actual < prev_min

    # Barrida: mecha cruza pero NO cierra más allá
    sweep_up = high_actual > prev_max and not bos_up
    sweep_dn = low_actual < prev_min and not bos_dn

    return {
        "BOS": bool(bos_up or bos_dn),
        "tipo_BOS": "alcista" if bos_up else "bajista" if bos_dn else None,
        "rango": not (bos_up or bos_dn),
        "barrida_alcista": bool(sweep_up),
        "barrida_bajista": bool(sweep_dn),
        "prev_max": prev_max,
        "prev_min": prev_min,
    }
# Alias para compatibilidad con versiones previas
detectar_bos = detectar_estructura

