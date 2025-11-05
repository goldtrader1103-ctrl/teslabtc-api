# utils/liquidez.py
from datetime import timedelta
from utils.time_utils import now_col, col_dt, window_inclusive

def rango_asiatico_hilo(klines_15m):
    """
    Rango Asiático (COL): 17:00 → 02:00 (del día siguiente).
    klines_15m: [{"open_time": datetime tz-aware, "high": float, "low": float}, ...]
    Devuelve {"ASIAN_HIGH": float, "ASIAN_LOW": float}
    """
    if not klines_15m:
        return None

    ref = now_col()
    start = ref.replace(hour=17, minute=0, second=0, microsecond=0)
    end = (ref + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)

    hi, lo = None, None
    for k in klines_15m:
        t = k["open_time"]
        if window_inclusive(start, end, t):
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)

    if hi is None or lo is None:
        return None
    return {"ASIAN_HIGH": hi, "ASIAN_LOW": lo}

def rango_dia_previo_hilo(klines_15m):
    """
    Día previo (COL): 19:00 → 19:00.
    Devuelve {"PDH": float, "PDL": float}
    """
    if not klines_15m:
        return None

    ref = now_col()
    end = ref.replace(hour=19, minute=0, second=0, microsecond=0)
    start = (end - timedelta(days=1))

    hi, lo = None, None
    for k in klines_15m:
        t = k["open_time"]
        if start <= t < end:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)

    if hi is None or lo is None:
        return None
    return {"PDH": hi, "PDL": lo}

# ==== Alias de compatibilidad para analisis_premium ====
def asian_range(klines_15m):
    return rango_asiatico_hilo(klines_15m)

def niveles_liquidez_horas(klines_15m=None, symbol="BTCUSDT"):
    """
    Compat: en esta versión devolvemos las claves que usa analisis_premium.
    Preferimos el cálculo real con klines_15m; si no vienen, devolvemos None.
    """
    out = {"Asia": {"High": None, "Low": None},
           "London": {"High": None, "Low": None},
           "NewYork": {"High": None, "Low": None}}
    if klines_15m:
        dp = rango_dia_previo_hilo(klines_15m)
        if dp:
            out["PrevDay"] = {"PDH": dp["PDH"], "PDL": dp["PDL"]}
    return out
