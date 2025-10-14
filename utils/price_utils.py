# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (versión 3.1 estable)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone

# ============================================================
# 🌎 Configuración base
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "TESLABTC-KG/3.1"}

# ============================================================
# 💰 Fuentes de precio (multifuente con fallback)
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    return float(r.json()["price"]), "Binance"

def _get_coinbase(symbol="BTCUSDT"):
    pair = symbol.replace("USDT", "-USD").replace("USDC", "-USD")
    r = requests.get(
        f"https://api.coinbase.com/v2/prices/{pair}/spot",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    return float(r.json()["data"]["amount"]), "Coinbase"

def _get_coingecko(symbol="BTCUSDT"):
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    data = r.json()
    return float(data["bitcoin"]["usd"]), "CoinGecko"

def _get_bybit(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["list"][0]["lastPrice"]), "Bybit"

def obtener_precio(simbolo: str = "BTCUSDT") -> dict:
    """
    Intenta obtener el precio desde varias fuentes.
    Orden de prioridad: Binance → Coinbase → CoinGecko → Bybit.
    """
    fuentes = (_get_binance, _get_coinbase, _get_coingecko, _get_bybit)
    for intento in range(2):
        for fuente in fuentes:
            try:
                precio, origen = fuente(simbolo)
                return {"precio": precio, "fuente": origen}
            except Exception as e:
                print(f"[obtener_precio] {fuente.__name__} falló: {e}")
        time.sleep(0.5)
    return {"precio": None, "fuente": "Ninguna"}

# ============================================================
# 🕐 Sesión New York Activa
# ============================================================

def sesion_ny_activa() -> bool:
    """
    Verifica si la sesión de New York está activa (Colombia 07:00–13:30).
    """
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 Obtener velas desde Binance (con autenticación real)
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "15m", limite: int = 200):
    """
    Obtiene velas desde Binance con autenticación API Key real.
    Si hay error de autorización, usa fallback público.
    """
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY} if BINANCE_API_KEY else UA

    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"

    try:
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        data = r.json()
        velas = [{
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
        } for k in data]
        return velas
    except Exception as e:
        print(f"[obtener_klines_binance] Error primario: {e}")
        # Fallback público
        try:
            r = requests.get(
                f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit=100",
                timeout=10, headers=UA
            )
            r.raise_for_status()
            data = r.json()
            velas = [{
                "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
            } for k in data]
            return velas
        except Exception as e2:
            print(f"[obtener_klines_binance] Error secundario: {e2}")
            return None

# ============================================================
# 🧩 Detector estructural simplificado (macro e intradía)
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    """
    Analiza una lista de velas y devuelve si la estructura es alcista, bajista o neutra.
    Criterio: compara los últimos cierres + máximos/mínimos.
    """
    if not velas or len(velas) < 10:
        return {"estado": "sin_datos"}

    closes = [v["close"] for v in velas[-20:]]
    highs = [v["high"] for v in velas[-20:]]
    lows = [v["low"] for v in velas[-20:]]

    tendencia = "neutra"
    if closes[-1] > max(closes[:-5]) and closes[-1] > closes[0]:
        tendencia = "alcista"
    elif closes[-1] < min(closes[:-5]) and closes[-1] < closes[0]:
        tendencia = "bajista"

    zona_high = max(highs[-5:])
    zona_low = min(lows[-5:])

    return {
        "estado": tendencia,
        "zona_high": round(zona_high, 2),
        "zona_low": round(zona_low, 2)
    }

# ============================================================
# 🟣 PDH / PDL (últimas 24 horas)
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT") -> dict:
    """
    Calcula el máximo (PDH) y mínimo (PDL) de las últimas 24h.
    """
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
