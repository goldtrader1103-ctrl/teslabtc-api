import requests
from datetime import datetime, timedelta, timezone, time
from typing import List, Dict

# Zona horaria Colombia
TZ_COL = timezone(timedelta(hours=-5))

# =====================================================
# PRECIO Y DATOS DE BINANCE
# =====================================================

def obtener_precio():
    """Precio actual BTCUSDT desde Binance."""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        r = requests.get(url, timeout=10)
        data = r.json()
        return round(float(data["price"]), 2)
    except Exception as e:
        print("Error al obtener precio:", e)
        return None


def obtener_klines(intervalo="5m", limite=200):
    """Velas históricas de Binance."""
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={intervalo}&limit={limite}"
    r = requests.get(url, timeout=10)
    data = r.json()
    return [
        {
            "open_time": datetime.fromtimestamp(x[0] / 1000, tz=TZ_COL),
            "open": float(x[1]),
            "high": float(x[2]),
            "low": float(x[3]),
            "close": float(x[4])
        } for x in data
    ]


# =====================================================
# DETECCIÓN DE ESTRUCTURA TESLABTC A.P.
# =====================================================

def detectar_bos(data: List[Dict]):
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


def detectar_barrida(data: List[Dict]):
    """Detecta si hubo barrida reciente de altos o bajos."""
    high = [x["high"] for x in data[-10:]]
    low = [x["low"] for x in data[-10:]]
    if high[-1] > max(high[:-1]):
        return "Barrida de Altos"
    elif low[-1] < min(low[:-1]):
        return "Barrida de Bajos"
    return "Sin barrida"


def _pdh_pdl(velas_1h: List[Dict]):
    """PDH/PDL del día anterior."""
    hoy = datetime.now(TZ_COL).date()
    ayer = hoy - timedelta(days=1)
    velas_ayer = [v for v in velas_1h if v["open_time"].date() == ayer]
    if not velas_ayer:
        return None, None
    pdh = max(v["high"] for v in velas_ayer)
    pdl = min(v["low"] for v in velas_ayer)
    return pdh, pdl


def _asia_range(velas_15m: List[Dict]):
    """Rango Asia (19:00–03:00 COL)."""
    hoy = datetime.now(TZ_COL).date()
    ayer = hoy - timedelta(days=1)
    inicio = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=19)
    fin = datetime.combine(hoy, datetime.min.time(), tzinfo=TZ_COL).replace(hour=3)
    bloque = [v for v in velas_15m if inicio <= v["open_time"] <= fin]
    if not bloque:
        return None, None
    return max(v["high"] for v in bloque), min(v["low"] for v in bloque)


# =====================================================
# SESIÓN NY
# =====================================================

def sesion_ny_activa() -> bool:
    """Verifica si la sesión NY está activa (07:00–13:30 COL)."""
    ahora = datetime.now(TZ_COL).time()
    return time(7, 0) <= ahora <= time(13, 30)

