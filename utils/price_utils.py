import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

# ==============================
# ⚙️ CONFIGURACIÓN BASE
# ==============================

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# ==============================
# 🔹 FUNCIONES DE CONSULTA BINANCE
# ==============================

def _req(url: str, params: Optional[dict] = None, timeout: int = 10):
    """Petición GET simple con headers estándar."""
    headers = {"User-Agent": "TESLABTC-API/2.3"}
    return requests.get(url, params=params or {}, headers=headers, timeout=timeout)


def obtener_precio() -> Optional[float]:
    """Obtiene el precio actual de BTCUSDT desde Binance."""
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
    """Obtiene velas (klines) de Binance con horario de Colombia."""
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


# ==============================
# 🔹 SESIÓN NY (07:00 – 13:30 COL)
# ==============================

def sesion_ny_activa(ahora_col: datetime) -> bool:
    start = datetime.combine(ahora_col.date(), datetime.min.time(), tzinfo=TZ_COL).replace(hour=7)
    end = datetime.combine(ahora_col.date(), datetime.min.time(), tzinfo=TZ_COL).replace(hour=13, minute=30)
    return start <= ahora_col <= end


# ==============================
# 🔹 PDH / PDL (día anterior)
# ==============================

def _pdh_pdl(velas_1h: List[Dict]):
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


# ==============================
# 🔹 RANGO ASIA (19:00 – 03:00 COL)
# ==============================

def _asia_range(velas_15m: List[Dict]):
    if not velas_15m:
        return None, None

    ahora = datetime.now(TZ_COL)
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)

    inicio = datetime.combine(ayer, datetime.min.time(), tzinfo=TZ_COL).replace(hour=19)
    fin = datetime.combine(hoy, datetime.min.time(), tzinfo=TZ_COL).replace(hour=3)

    bloque = [v for v in velas_15m if inicio <= v["open_time"] <= fin]
    if not bloque:
        return None, None

    high_a = max(v["high"] for v in bloque)
    low_a = min(v["low"] for v in bloque)
    return high_a, low_a


# ==============================
# 🔹 DETECCIÓN DE ESTRUCTURA
# ==============================

def detectar_estructura(velas: List[Dict], lookback: int = 20) -> Dict:
    """
    TESLABTC A.P. — Detección de estructura avanzada:
    - BOS confirmado
    - CHoCH (cambio de carácter)
    - Tendencia real según secuencia de altos/bajos
    """
    if len(velas) < lookback + 5:
        return {"BOS": False, "tipo_BOS": None, "rango": True, "tendencia": "indefinida"}

    highs = [v["high"] for v in velas[-(lookback + 5):]]
    lows = [v["low"] for v in velas[-(lookback + 5):]]
    closes = [v["close"] for v in velas[-(lookback + 5):]]

    prev_max = max(highs[:-2])
    prev_min = min(lows[:-2])
    close_actual = closes[-1]
    high_actual = highs[-1]
    low_actual = lows[-1]

    bos_up = close_actual > prev_max
    bos_dn = close_actual < prev_min

    # Secuencia estructural (altos/bajos)
    altos = highs[-6:]
    bajos = lows[-6:]
    hh = sum(1 for i in range(1, len(altos)) if altos[i] > altos[i - 1])
    ll = sum(1 for i in range(1, len(bajos)) if bajos[i] < bajos[i - 1])

    if hh >= 3 and ll <= 1:
        tendencia = "alcista"
    elif ll >= 3 and hh <= 1:
        tendencia = "bajista"
    else:
        tendencia = "rango"

    choch = None
    if bos_up and tendencia == "bajista":
        choch = "alcista"
    elif bos_dn and tendencia == "alcista":
        choch = "bajista"

    return {
        "BOS": bool(bos_up or bos_dn),
        "tipo_BOS": "alcista" if bos_up else "bajista" if bos_dn else None,
        "CHoCH": choch,
        "tendencia": tendencia,
        "rango": not (bos_up or bos_dn),
        "prev_max": prev_max,
        "prev_min": prev_min,
    }
