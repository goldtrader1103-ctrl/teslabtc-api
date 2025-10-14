# ============================================================
# 📡 TESLABTC.KG — Live Monitoring (BOS + Zona + Sesgo)
# ============================================================

import asyncio
from collections import deque
from datetime import datetime, timezone, timedelta

from utils.price_utils import obtener_klines_binance, obtener_precio, BINANCE_STATUS
from utils.estructura_utils import evaluar_estructura

TZ_COL = timezone(timedelta(hours=-5))

# Estado en memoria (simple y eficiente)
_ALERTS = deque(maxlen=50)       # últimas 50 alertas
_STATUS = {
    "running": False,
    "last_run": None,
    "interval_min": 5,
    "binance_status": None,
    "last_error": None,
}
_PREV = {
    "h1_state": None,            # para detectar cambio de sesgo (CHoCH H1)
}

def _now_str():
    return datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

def _make_alert(kind: str, detail: str, extra: dict | None = None):
    payload = {
        "ts": _now_str(),
        "tipo": kind,
        "detalle": detail,
    }
    if extra:
        payload.update(extra)
    _ALERTS.appendleft(payload)

def _bos_signal(velas: list[dict], lookback: int = 10) -> str | None:
    """
    BOS simple: última close rompe el máximo/mínimo de las últimas N-1 velas.
    """
    if not velas or len(velas) < (lookback + 2):
        return None
    sub = velas[-(lookback+1):]           # N-1 velas + última
    highs = [v["high"] for v in sub[:-1]]
    lows  = [v["low"]  for v in sub[:-1]]
    last_close = sub[-1]["close"]

    if last_close > max(highs):
        return "BOS_ALCISTA"
    if last_close < min(lows):
        return "BOS_BAJISTA"
    return None

def _in_zone(price: float, zona: dict | None) -> bool:
    if not zona: return False
    hi = zona.get("High")
    lo = zona.get("Low")
    if hi is None or lo is None: return False
    return lo <= price <= hi

async def _tick_once():
    """
    Ejecuta una pasada del monitor:
    - Lee velas H4/H1/M15/M5 de Binance
    - Evalúa estructura y zonas
    - Detecta BOS en M15/M5
    - Lanza alertas según reglas TESLABTC
    """
    try:
        _STATUS["binance_status"] = BINANCE_STATUS

        # 1) Velas
        velas_h4  = obtener_klines_binance("BTCUSDT", "4h", 120)
        velas_h1  = obtener_klines_binance("BTCUSDT", "1h", 120)
        velas_m15 = obtener_klines_binance("BTCUSDT", "15m", 200)
        velas_m5  = obtener_klines_binance("BTCUSDT", "5m", 200)

        if not velas_h1 or not velas_m15 or not velas_m5:
            _make_alert("SISTEMA", "No hay velas suficientes para evaluar M5/M15/H1.")
            return

        # 2) Estructura + zonas
        resultado = evaluar_estructura(velas_h4, velas_h1, velas_m15)
        estructura = resultado["estructura"]                     # {"H4 (macro)": "...", "H1 (intradía)": "...", "M15 (reacción)": "..."}
        zonas = resultado["zonas"]                               # {"ZONA H4...": {...}, "ZONA H1...": {...}, "ZONA M15...": {...}}
        zona_m15 = zonas.get("ZONA M15 (reacción)")

        h1_state = estructura.get("H1 (intradía)")
        m15_state = estructura.get("M15 (reacción)")

        # 3) Precio actual
        p = obtener_precio("BTCUSDT")
        price = p.get("precio")

        # 4) BOS
        bos_m15 = _bos_signal(velas_m15, lookback=12)  # velas recientes
        bos_m5  = _bos_signal(velas_m5,  lookback=20)

        # 5) Reglas de alertas TESLABTC
        #   A+ → BOS M5 en dirección de H1 y dentro de zona M15
        if price and _in_zone(price, zona_m15) and bos_m5:
            if (bos_m5 == "BOS_ALCISTA" and h1_state == "alcista") or (bos_m5 == "BOS_BAJISTA" and h1_state == "bajista"):
                _make_alert(
                    "A_PLUS",
                    f"BOS {('ALCISTA' if 'ALCISTA' in bos_m5 else 'BAJISTA')} M5 dentro de ZONA M15",
                    extra={
                        "precio": round(price, 2),
                        "h1": h1_state,
                        "m15": m15_state,
                        "zona_M15": zona_m15
                    }
                )

        #   SCALPING → BOS M5 en contra de H1 pero a favor de M15 (micro de retroceso)
        if price and _in_zone(price, zona_m15) and bos_m5:
            if (bos_m5 == "BOS_ALCISTA" and h1_state == "bajista" and m15_state == "alcista") or \
               (bos_m5 == "BOS_BAJISTA" and h1_state == "alcista" and m15_state == "bajista"):
                _make_alert(
                    "SCALPING",
                    f"BOS {('ALCISTA' if 'ALCISTA' in bos_m5 else 'BAJISTA')} M5 contra H1 pero con M15",
                    extra={
                        "precio": round(price, 2),
                        "h1": h1_state,
                        "m15": m15_state,
                        "zona_M15": zona_m15
                    }
                )

        #   CHoCH / Cambio de sesgo H1
        prev = _PREV.get("h1_state")
        if prev and prev != h1_state and h1_state in ("alcista", "bajista"):
            _make_alert("CHOCH_H1", f"Cambio de sesgo H1: {prev} → {h1_state}")
        _PREV["h1_state"] = h1_state

        #   BOS M15 informativo (ruido/confirmación de intención)
        if bos_m15:
            _make_alert("INFO_M15", f"Ruptura M15: {('ALCISTA' if 'ALCISTA' in bos_m15 else 'BAJISTA')} ({bos_m15})")

    except Exception as e:
        _STATUS["last_error"] = str(e)
        _make_alert("ERROR", f"Excepción en monitor: {e}")

async def live_monitor_loop(interval_min: int = 5):
    """
    Bucle principal del monitor. Llama _tick_once() cada 'interval_min' minutos.
    """
    _STATUS["running"] = True
    _STATUS["interval_min"] = interval_min
    _make_alert("SISTEMA", f"Live monitor iniciado. Intervalo: {interval_min} min. Estado Binance: {BINANCE_STATUS}")

    while _STATUS["running"]:
        _STATUS["last_run"] = _now_str()
        await _tick_once()
        await asyncio.sleep(interval_min * 60)

def stop_monitor():
    _STATUS["running"] = False

def get_alerts():
    """Devuelve estado y últimas alertas."""
    return {
        "status": _STATUS,
        "ultimas_alertas": list(_ALERTS),
    }
