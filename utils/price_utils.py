# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (conexión real Binance)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone
from binance import Client

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.0"}

# ============================================================
# 🔐 CREDENCIALES BINANCE (seguras por variables de entorno)
# ============================================================

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

try:
    client = Client(API_KEY, API_SECRET)
    print("✅ [TESLABTC.KG] Cliente Binance inicializado correctamente.")
except Exception as e:
    print(f"⚠️ [TESLABTC.KG] Error iniciando cliente Binance: {e}")
    client = None

# ============================================================
# 💰 OBTENER PRECIO ACTUAL (API Key o fuentes públicas)
# ============================================================

def _get_binance_real(symbol="BTCUSDT"):
    """Obtiene precio real desde cuenta de Binance con API Key."""
    if not client:
        raise ValueError("Cliente Binance no disponible.")
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"]), "Binance (API)"

def _get_binance_public(symbol="BTCUSDT"):
    """Fuente pública si falla la autenticada."""
    r = requests.get(
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        timeout=5, headers=UA
    )
    r.raise_for_status()
    return float(r.json()["price"]), "Binance (pública)"

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
    1️⃣ Binance API Key (autenticado)
    2️⃣ Binance pública
    3️⃣ Coinbase
    4️⃣ CoinGecko
    5️⃣ Bybit
    """
    fuentes = (_get_binance_real, _get_binance_public, _get_coinbase, _get_coingecko, _get_bybit)
    for intento in range(2):
        for fuente in fuentes:
            try:
                precio, origen = fuente(simbolo)
                return {"precio": precio, "fuente": origen}
            except Exception as e:
                print(f"[obtener_precio] {fuente.__name__} falló: {e}")
                continue
        time.sleep(0.5)
    return {"precio": None, "fuente": "Ninguna"}

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA (Lunes–Viernes, 07:00–13:30 COL)
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()  # 0 = Lunes ... 6 = Domingo
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES (preferencia Binance API Key)
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "15m", limite: int = 200):
    try:
        if client:
            klines = client.get_klines(symbol=simbolo, interval=intervalo, limit=limite)
            velas = [{
                "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
                "open": float(k[1]), "high": float(k[2]),
                "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
            } for k in klines]
            return velas
        else:
            raise Exception("Cliente Binance no disponible.")
    except Exception as e:
        print(f"[obtener_klines_binance] Error con API: {e}")
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"
            r = requests.get(url, timeout=10, headers=UA)
            r.raise_for_status()
            data = r.json()
            velas = [{
                "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
                "open": float(k[1]), "high": float(k[2]),
                "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
            } for k in data]
            return velas
        except Exception as e2:
            print(f"[obtener_klines_binance] Error total: {e2}")
            return None

# ============================================================
# 📈 DETECTAR ESTRUCTURA
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    if not velas or len(velas) < 10:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    up = closes[-1] > closes[0]
    return {"estado": "alcista" if up else "bajista"}

# ============================================================
# 🟣 PDH/PDL ÚLTIMAS 24H
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT") -> dict:
    try:
        velas = obtener_klines_binance(simbolo, "15m", 96)
        if not velas:
            return {"PDH": None, "PDL": None}
        highs = [v["high"] for v in velas]
        lows = [v["low"] for v in velas]
        return {"PDH": max(highs), "PDL": min(lows)}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}

# ============================================================
# 🧪 TEST LOCAL
# ============================================================

if __name__ == "__main__":
    print("🔍 Test obtener_precio:", obtener_precio())
    print("🔍 NY activa:", sesion_ny_activa())
    velas = obtener_klines_binance()
    print("🔍 Estructura:", detectar_estructura(velas))
    print("🔍 PDH/PDL:", _pdh_pdl())
