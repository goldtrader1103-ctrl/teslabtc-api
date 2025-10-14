# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (versión con API Binance autenticada)
# ============================================================

import time
import requests
import os
from datetime import datetime, timedelta, timezone

# ============================================================
# 🕐 CONFIGURACIÓN GENERAL
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))  # zona horaria Colombia
UA = {"User-Agent": "teslabtc-kg/3.0"}

# ============================================================
# 🔐 CLAVES API BINANCE (Render Env + Secret File)
# ============================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = None

# Render guarda los secretos en /etc/secrets/<NOMBRE>
try:
    with open("/etc/secrets/BINANCE_API_SECRET", "r") as f:
        BINANCE_API_SECRET = f.read().strip()
except Exception:
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# ============================================================
# 💰 OBTENER PRECIO ACTUAL (multifuente con fallback)
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    """Obtiene el precio actual desde Binance (público o autenticado si es posible)."""
    headers = {"User-Agent": "teslabtc-kg/3.0"}
    if BINANCE_API_KEY:
        headers["X-MBX-APIKEY"] = BINANCE_API_KEY
    r = requests.get(
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        timeout=5, headers=headers
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
    data = r.json()
    return float(data["data"]["amount"]), "Coinbase"

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
    Intenta obtener el precio desde varias fuentes:
    Binance → Coinbase → CoinGecko → Bybit
    Devuelve dict con {'precio': float | None, 'fuente': str}
    """
    fuentes = (_get_binance, _get_coinbase, _get_coingecko, _get_bybit)
    for intento in range(2):  # 2 rondas de prueba
        for fuente in fuentes:
            try:
                precio, origen = fuente(simbolo)
                return {"precio": precio, "fuente": origen}
            except Exception as e:
                print(f"[obtener_precio] {fuente.__name__} falló: {e}")
        time.sleep(0.5)
    return {"precio": None, "fuente": "Ninguna"}

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA (Lunes–Viernes, 07:00–13:30 COL)
# ============================================================

def sesion_ny_activa() -> bool:
    """
    Verifica si la sesión de New York está activa.
    Activa: Lunes a Viernes entre 07:00 y 13:30 COL.
    """
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()  # 0 = Lunes ... 6 = Domingo
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES DE BINANCE
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "5m", limite: int = 200):
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"
    try:
        headers = {"User-Agent": "teslabtc-kg/3.0"}
        if BINANCE_API_KEY:
            headers["X-MBX-APIKEY"] = BINANCE_API_KEY
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        data = r.json()
        velas = [{
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]), "high": float(k[2]),
            "low": float(k[3]), "close": float(k[4]),
            "volume": float(k[5]),
        } for k in data]
        return velas
    except Exception as e:
        print(f"[obtener_klines_binance] Error: {e}")
        return None

# ============================================================
# 📈 DETECTAR ESTRUCTURA SIMPLE
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    """Analiza los últimos 30 cierres para determinar estructura básica."""
    if not velas:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    if len(closes) < 5:
        return {"estado": "insuficiente"}
    up = closes[-1] > closes[0]
    return {"estado": "alcista" if up else "bajista"}

# ============================================================
# 🟣 PDH / PDL ÚLTIMAS 24H
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT") -> dict:
    """Obtiene los puntos altos y bajos de las últimas 24h desde Binance."""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=96"
        headers = {"User-Agent": "teslabtc-kg/3.0"}
        if BINANCE_API_KEY:
            headers["X-MBX-APIKEY"] = BINANCE_API_KEY
        r = requests.get(url, timeout=10, headers=headers)
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
