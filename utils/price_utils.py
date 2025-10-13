# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG
# ============================================================

import time
import requests
from datetime import datetime, timedelta, timezone

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

UA = {"User-Agent": "teslabtc-kg/1.0"}

# ============================================================
# 💰 OBTENER PRECIO ACTUAL (multifuente)
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    return float(r.json()["price"])

def _get_coinbase(symbol="BTCUSDT"):
    # Coinbase usa pares con guión
    pair = symbol.replace("USDT", "-USDT").replace("USD", "-USD").replace("USDC", "-USDC")
    r = requests.get(
        f"https://api.exchange.coinbase.com/products/{pair}/ticker",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    return float(r.json()["price"])

def _get_bybit(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.bytick.com/spot/v3/public/quote/ticker/price?symbol={symbol}",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["price"])

def obtener_precio(simbolo: str = "BTCUSDT") -> float | None:
    """
    Intenta obtener el precio desde varias fuentes (Binance → Coinbase → Bybit)
    con pequeños reintentos (backoff). Retorna None si todas fallan.
    """
    fuentes = (_get_binance, _get_coinbase, _get_bybit)
    for intento in range(2):              # 2 rondas
        for fuente in fuentes:
            try:
                return fuente(simbolo)
            except Exception as e:
                print(f"[obtener_precio] {fuente.__name__} fallo: {e}")
        time.sleep(0.8)                    # pequeño backoff
    return None

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA (07:00–13:30 COL)
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES DE BINANCE (simple)
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "5m", limite: int = 200):
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"
    try:
        r = requests.get(url, timeout=10, headers=UA)
        r.raise_for_status()
        data = r.json()
        velas = [{
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]), "high": float(k[2]),
            "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
        } for k in data]
        return velas
    except Exception as e:
        print(f"[obtener_klines_binance] Error: {e}")
        return None

# ============================================================
# 📈 DETECTAR ESTRUCTURA (muy simplificado)
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    if not velas:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    if len(closes) < 5:
        return {"estado": "insuficiente"}
    up = closes[-1] > closes[0]
    return {"estado": "alcista" if up else "bajista"}

# ============================================================
# 🟣 PDH/PDL ÚLTIMAS 24H
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT") -> dict:
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=96"
        r = requests.get(url, timeout=10, headers=UA)
        r.raise_for_status()
        data = r.json()
        cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
        data_filtrada = [k for k in data if datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL) > cutoff]
        highs = [float(k[2]) for k in data_filtrada]
        lows = [float(k[3]) for k in data_filtrada]
        return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
