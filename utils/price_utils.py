import requests
from datetime import datetime, timedelta, timezone, time
from typing import List, Dict, Optional

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))


# ============================================================
# UTILIDADES DE CONEXIÓN
# ============================================================

def _req(url: str, params: Optional[dict] = None, timeout: int = 10):
    headers = {"User-Agent": "TESLABTC-API/1.1"}
    proxies = {
        "http": "http://proxy.render.com:8080",
        "https": "http://proxy.render.com:8080"
    }
    return requests.get(url, params=params or {}, headers=headers, timeout=timeout, proxies=proxies)


def obtener_precio() -> Optional[float]:
    """
    Obtiene el precio actual de BTCUSDT desde Binance con headers y proxy.
    Compatible con Render.
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        headers = {
            "User-Agent": "TESLABTC-API/1.0",
            "Cache-Control": "no-cache",
            "Accept": "application/json",
        }
        proxies = {
            "http": "http://proxy.render.com:8080",
            "https": "http://proxy.render.com:8080"
        }

        response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        if response.status_code != 200:
            print("Error Binance:", response.text)
            return None

        data = response.json()
        precio = float(data.get("price", 0))
        if precio <= 0:
            raise ValueError("Precio inválido")
        return round(precio, 2)
    except Exception as e:
        print(⚠️ Error al obtener precio:", e)
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


# ============================================================
# ESTRUCTURA Y LIQUIDEZ
# ============================================================

def detectar_estructura(velas: List[Dict], lookback: int = 20) -> Dict:
    """
    Detección simple de estructura (PA puro):
    - BOS: close actual > máx prev (lookback) o < mín prev
    - Barridas: high actual > máx prev sin cierre por encima / low actual < mín prev sin cierre por debajo.
    - Rango: si no hay BOS.
    """
    if len(velas) < max(lookback + 1, 5):
        return {"BOS": False, "tipo_BOS": None, "rango": True, "barrida_alcista": False, "barrida_bajista": False}

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


def _pdh_pdl(velas_1h: List[Dict]):
    """PDH/PDL del día anterior (COL)."""
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
    """Rango aproximado de ASIA (19:00–03:00 COL)."""
    if not velas_15m:
        return None, None
    ahora = datetime.now(TZ_COL)
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)
    inicio_a = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=19)
    fin_a_1 = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=23, minute=59)
    fin_a_2 = datetime.combine(hoy, datetime.min.time(), tzinfo=TZ_COL).replace(hour=3)
    tramo1 = [v for v in velas_15m if inicio_a <= v["open_time"] <= fin_a_1]
    tramo2 = [v for v in velas_15m if v["open_time"].date() == hoy and v["open_time"].hour <= 3]
    bloque = tramo1 + tramo2
    if not bloque:
        return None, None
    high_a = max(v["high"] for v in bloque)
    low_a = min(v["low"] for v in bloque)
    return high_a, low_a


# ============================================================
# SESIÓN NY
# ============================================================

def ahora_col() -> datetime:
    """Devuelve la hora actual en zona Colombia."""
    return datetime.now(TZ_COL)


def sesion_ny_activa() -> bool:
    """
    Verifica si la sesión de Nueva York está activa (hora COL).
    """
    ahora = ahora_col().time()
    return time(6, 0) <= ahora <= time(13, 30)


# Alias para compatibilidad
detectar_bos = detectar_estructura


__all__ = [
    "obtener_precio",
    "obtener_klines_binance",
    "detectar_estructura",
    "_pdh_pdl",
    "_asia_range",
    "TZ_COL",
    "ahora_col",
    "sesion_ny_activa",
]
