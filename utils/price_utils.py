# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (v3.2 con API Key real)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# Claves privadas seguras (Render → Environment)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

UA = {"User-Agent": "teslabtc-kg/3.2", "X-MBX-APIKEY": BINANCE_API_KEY}

# ============================================================
# 💰 OBTENER PRECIO ACTUAL (con API Key y fallback)
# ============================================================

def obtener_precio(symbol: str = "BTCUSDT") -> dict:
    """
    Obtiene el precio actual desde Binance usando tu API Key real.
    Si falla, usa Coinbase, CoinGecko o Bybit como respaldo.
    """
    fuentes = [
        _get_binance,
        _get_coinbase,
        _get_coingecko,
        _get_bybit
    ]
    for intento in range(2):
        for fuente in fuentes:
            try:
                precio, origen = fuente(symbol)
                if precio:
                    return {"precio": precio, "fuente": origen}
            except Exception as e:
                print(f"[obtener_precio] {fuente.__name__} falló: {e}")
        time.sleep(0.5)
    return {"precio": None, "fuente": "Sin conexión"}

# ============================================================
# 🌐 FUENTES DE PRECIO
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url, headers=UA, timeout=5)
    r.raise_for_status()
    return float(r.json()["price"]), "Binance"

def _get_coinbase(symbol="BTCUSDT"):
    pair = symbol.replace("USDT", "-USD").replace("USDC", "-USD")
    r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=5)
    r.raise_for_status()
    data = r.json()
    return float(data["data"]["amount"]), "Coinbase"

def _get_coingecko(symbol="BTCUSDT"):
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=5
    )
    r.raise_for_status()
    data = r.json()
    return float(data["bitcoin"]["usd"]), "CoinGecko"

def _get_bybit(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}",
        timeout=5
    )
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["list"][0]["lastPrice"]), "Bybit"

# ============================================================
# 📊 OBTENER KLINES DE BINANCE (segura)
# ============================================================

def obtener_klines_binance(symbol="BTCUSDT", intervalo="15m", limite=200):
    """
    Devuelve velas OHLC del símbolo dado con soporte de API real.
    """
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={intervalo}&limit={limite}"
        r = requests.get(url, headers=UA, timeout=10)
        r.raise_for_status()
        data = r.json()
        velas = [{
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        } for k in data]
        return velas
    except Exception as e:
        print(f"[obtener_klines_binance] Error: {e}")
        return None

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    weekday = now.weekday()  # 0=Lunes, 6=Domingo
    h = now.hour + now.minute / 60
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📈 DETECTAR ESTRUCTURA SIMPLE (fallback)
# ============================================================

def detectar_estructura(velas: Optional[list]) -> dict:
    """
    Estructura básica de respaldo.
    """
    if not velas:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    if len(closes) < 5:
        return {"estado": "insuficiente"}
    return {"estado": "alcista" if closes[-1] > closes[0] else "bajista"}

# ============================================================
# 🟣 PDH / PDL ÚLTIMAS 24H
# ============================================================

def _pdh_pdl(symbol="BTCUSDT") -> dict:
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=96"
        r = requests.get(url, headers=UA, timeout=10)
        r.raise_for_status()
        data = r.json()
        cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
        filtradas = [k for k in data if datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL) > cutoff]
        highs = [float(k[2]) for k in filtradas]
        lows = [float(k[3]) for k in filtradas]
        return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
