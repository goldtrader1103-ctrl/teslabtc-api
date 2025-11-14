# ==============================================
# 📦 TESLABTC.KG — utils/price_utils.py (REAL v5.2)
# 1) Precio actual (Binance → CoinGecko fallback)
# 2) Klines (Binance REST → Binance Vision → CoinGecko)
# 3) Sesión NY (07:00–13:30 COL)
# 4) PDH/PDL día operativo CERRADO (7PM–7PM COL)
# 5) Rango asiático CERRADO (5PM–2AM COL)
# ==============================================
from __future__ import annotations
import requests, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Tuple, Optional

from utils.time_utils import (
    TZ_COL, now_col, last_closed_daily_window_col, last_closed_asian_window_col
)

BINANCE_STATUS = "🦎 Fallback CoinGecko activo"
UA = {"User-Agent": "teslabtc-kg/5.2"}

BINANCE_REST_BASE = "https://api.binance.com"
BINANCE_VISION_BASE = "https://data-api.binance.vision"

# -----------------------------
# 💰 Precio
# -----------------------------
def obtener_precio(simbolo: str = "BTCUSDT") -> Dict[str, Any]:
    global BINANCE_STATUS
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/ticker/price",
            params={"symbol": simbolo.upper()},
            headers=UA, timeout=6
        )
        r.raise_for_status()
        price = float(r.json()["price"])
        BINANCE_STATUS = "✅ Conectado a Binance REST"
        return {"precio": price, "fuente": "Binance (REST)"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ Binance REST: {e}"

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=UA, timeout=6
        )
        r.raise_for_status()
        data = r.json()
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            BINANCE_STATUS = "🦎 CoinGecko (fallback)"
            return {"precio": float(data["bitcoin"]["usd"]), "fuente": "CoinGecko"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ CoinGecko: {e}"

    BINANCE_STATUS = "⛔ Sin conexión de precio"
    return {"precio": None, "fuente": "⚙️ No conectado"}

# -----------------------------
# 🕒 Sesión NY
# -----------------------------
def sesion_ny_activa() -> bool:
    now = now_col()
    h = now.hour + now.minute / 60
    return 7 <= h < 13.5  # 13:30 COL

# -----------------------------
# 📊 Klines
# -----------------------------
def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=120) -> List[Dict[str, Any]]:
    global BINANCE_STATUS
    simbolo = simbolo.upper()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Connection": "keep-alive",
    }
    urls = [
        ("Binance Global", f"{BINANCE_REST_BASE}/api/v3/klines"),
        ("Binance Vision", f"{BINANCE_VISION_BASE}/api/v3/klines"),
    ]
    last_err = None
    for src, url in urls:
        try:
            for _ in range(3):
                r = requests.get(url, params={
                    "symbol": simbolo, "interval": intervalo, "limit": limite
                }, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        BINANCE_STATUS = f"✅ Klines desde {src}"
                        out = []
                        for k in data:
                            out.append({
                                "open_time": k[0],
                                "open": float(k[1]),
                                "high": float(k[2]),
                                "low": float(k[3]),
                                "close": float(k[4]),
                                "volume": float(k[5]),
                            })
                        return out
                elif r.status_code in (403, 429):
                    time.sleep(1.5)
                    continue
                elif r.status_code == 451:
                    break
                else:
                    last_err = f"{src} HTTP {r.status_code}"
                    break
        except Exception as e:
            last_err = f"{src}: {type(e).__name__} {e}"

    # Fallback CoinGecko (aprox)
    try:
        cg_interval = "hourly" if ("m" in intervalo or "h" in intervalo) else "daily"
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": 7, "interval": cg_interval},
            headers=headers, timeout=10
        )
        r.raise_for_status()
        prices = r.json().get("prices", [])
        if prices:
            BINANCE_STATUS = "🦎 Fallback CoinGecko (sim)"
            out = []
            for ts, price in prices[-limite:]:
                out.append({
                    "open_time": ts,
                    "open": float(price),
                    "high": float(price),
                    "low": float(price),
                    "close": float(price),
                    "volume": 0.0
                })
            return out
    except Exception as e:
        last_err = f"CoinGecko: {e}"

    BINANCE_STATUS = f"⛔ Sin datos válidos ({last_err})"
    return []

# -----------------------------
# 🧊 Zonas reales (CERRADAS)
# -----------------------------
def _pdh_pdl_anterior_col(simbolo="BTCUSDT") -> Dict[str, Optional[float]]:
    """
    PDH / PDL del ÚLTIMO DÍA OPERATIVO CERRADO (7PM–7PM COL).
    """
    kl = obtener_klines_binance(simbolo, "15m", 400)
    if not kl:
        return {"PDH": None, "PDL": None}

    start, end = last_closed_daily_window_col()
    highs, lows = [], []
    for k in kl:
        t = datetime.fromtimestamp(k["open_time"] / 1000, tz=TZ_COL)
        if start <= t <= end:
            highs.append(float(k["high"]))
            lows.append(float(k["low"]))
    if not highs or not lows:
        return {"PDH": None, "PDL": None}
    return {"PDH": round(max(highs), 2), "PDL": round(min(lows), 2)}

def _asian_range_anterior_col(simbolo="BTCUSDT") -> Dict[str, Optional[float]]:
    """
    ASIAN HIGH/LOW de la ÚLTIMA SESIÓN ASIÁTICA CERRADA (5PM→2AM COL).
    """
    kl = obtener_klines_binance(simbolo, "15m", 400)
    if not kl:
        return {"ASIAN_HIGH": None, "ASIAN_LOW": None}

    start, end = last_closed_asian_window_col()
    highs, lows = [], []
    for k in kl:
        t = datetime.fromtimestamp(k["open_time"] / 1000, tz=TZ_COL)
        if start <= t <= end:
            highs.append(float(k["high"]))
            lows.append(float(k["low"]))
    if not highs or not lows:
        return {"ASIAN_HIGH": None, "ASIAN_LOW": None}
    return {"ASIAN_HIGH": round(max(highs), 2), "ASIAN_LOW": round(min(lows), 2)}

def obtener_datos_sesion_colombia(simbolo="BTCUSDT") -> Dict[str, Any]:
    """
    Paquete completo de zonas: PDH/PDL (día operador cerrado) + Asia cerrado.
    Incluye etiquetas de horario.
    """
    pd = _pdh_pdl_anterior_col(simbolo)
    asia = _asian_range_anterior_col(simbolo)
    d_start, d_end = last_closed_daily_window_col()
    a_start, a_end = last_closed_asian_window_col()
    out = {
        **pd, **asia,
        "horario_dia": f"{d_start.strftime('%a %d %H:%M')} → {d_end.strftime('%a %d %H:%M')} COL",
        "horario_asia": f"{a_start.strftime('%a %d %H:%M')} → {a_end.strftime('%a %d %H:%M')} COL",
    }
    return out

def estado_binance() -> str:
    return BINANCE_STATUS
