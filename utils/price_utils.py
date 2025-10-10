import requests
from datetime import datetime, timedelta, timezone, time
from typing import List, Dict  # ✅ Necesario para las anotaciones de tipo

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# =====================================================
# PRECIO Y DATOS DE BINANCE
# =====================================================

def obtener_precio():
    """Obtiene el precio actual de BTCUSDT desde Binance."""
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
# DETECCIÓN DE ESTRUCTURA TESLABTC A.P v2.1
# =====================================================

def detectar_bos(data: List[Dict], base_lookback: int = 20) -> Dict:
    """
    TESLABTC A.P v2.1 — Detección avanzada de BOS y flujo direccional.
    Combina:
      - BOS clásico (ruptura de extremos previos)
      - Flujo direccional (pendiente de swing y momentum)
      - Ajuste dinámico del lookback según volatilidad
    """
    if len(data) < base_lookback + 5:
        return {
            "BOS": False,
            "tipo_BOS": None,
            "rango": True,
            "flujo": None,
            "barrida_alcista": False,
            "barrida_bajista": False
        }

    closes = [x["close"] for x in data]
    highs = [x["high"] for x in data]
    lows = [x["low"] for x in data]

    # ====== Volatilidad dinámica ======
    avg_range = sum((h - l) for h, l in zip(highs[-base_lookback:], lows[-base_lookback:])) / base_lookback
    volatilidad_alta = avg_range > (sum(highs[-base_lookback:]) / base_lookback) * 0.004  # 0.4 %
    lookback = 10 if volatilidad_alta else base_lookback

    # ====== Estructura previa ======
    prev_max = max(highs[-(lookback + 1):-1])
    prev_min = min(lows[-(lookback + 1):-1])
    close_actual = closes[-1]
    high_actual = highs[-1]
    low_actual = lows[-1]

    bos_up = close_actual > prev_max
    bos_dn = close_actual < prev_min

    # ====== Barridas ======
    sweep_up = high_actual > prev_max and not bos_up
    sweep_dn = low_actual < prev_min and not bos_dn

    # ====== Flujo direccional (momentum) ======
    sub = closes[-5:]
    tendencia_alcista = all(sub[i] < sub[i + 1] for i in range(4))
    tendencia_bajista = all(sub[i] > sub[i + 1] for i in range(4))
    flujo = "alcista" if tendencia_alcista else "bajista" if tendencia_bajista else None

    # ====== Swing progresivo ======
    swing_alcista = highs[-1] > highs[-2] > highs[-3] and lows[-1] > lows[-2] > lows[-3]
    swing_bajista = highs[-1] < highs[-2] < highs[-3] and lows[-1] < lows[-2] < lows[-3]

    # ====== Resultado final ======
    return {
        "BOS": bool(bos_up or bos_dn),
        "tipo_BOS": "alcista" if bos_up else "bajista" if bos_dn else None,
        "rango": not (bos_up or bos_dn or swing_alcista or swing_bajista),
        "flujo": flujo,
        "swing_alcista": swing_alcista,
        "swing_bajista": swing_bajista,
        "barrida_alcista": sweep_up,
        "barrida_bajista": sweep_dn,
        "prev_max": prev_max,
        "prev_min": prev_min,
    }

# =====================================================
# LIQUIDEZ — PDH / PDL / ASIA RANGE
# =====================================================

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

# =====================================================
# TEST LOCAL OPCIONAL
# =====================================================

if __name__ == "__main__":
    print("⏳ Probando módulo price_utils...")
    precio = obtener_precio()
    print("Precio actual BTCUSDT:", precio)
    velas = obtener_klines("1h", 50)
    estructura = detectar_bos(velas)
    print("Estructura H1:", estructura)
    print("✅ Módulo cargado correctamente.")
# =====================================================
# HORA LOCAL COLOMBIA
# =====================================================

def ahora_col() -> datetime:
    """Devuelve la hora actual en zona Colombia (UTC-5)."""
    return datetime.now(TZ_COL)
