# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (versión estable)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.1"}

# ============================================================
# 🔐 CONEXIÓN BINANCE REAL
# ============================================================

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = None
BINANCE_STATUS = "❌ Sin conexión"

try:
    if not API_KEY or not API_SECRET:
        raise ValueError("API Key o Secret no configurados")

    from binance import Client
    client = Client(API_KEY, API_SECRET)

    test_conn = client.ping()
    print("✅ [TESLABTC.KG] Conexión básica con Binance establecida.")

    server_time = client.get_server_time()
    latencia = abs(server_time["serverTime"] - int(datetime.now().timestamp() * 1000))
    print(f"🕓 Binance operativo — Latencia: {latencia} ms")

    BINANCE_STATUS = "✅ API conectada correctamente"

except Exception as e:
    print("⚠️ [TESLABTC.KG] Binance no accesible o error en API Key:")
    print("   →", e)
    print("🔁 Modo público activado temporalmente (Coinbase / Bybit / CoinGecko)")
    BINANCE_STATUS = f"⚠️ Error API: {e}"
    client = None

# ============================================================
# 💰 OBTENER PRECIO ACTUAL (multifuente con fallback)
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    if client:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"]), "Binance (API)"
    raise RuntimeError("Cliente Binance no disponible")

def _get_coinbase(symbol="BTCUSDT"):
    pair = symbol.replace("USDT", "-USD")
    r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=5, headers=UA)
    r.raise_for_status()
    data = r.json()
    return float(data["data"]["amount"]), "Coinbase"

def _get_coingecko(symbol="BTCUSDT"):
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=5, headers=UA)
    r.raise_for_status()
    data = r.json()
    return float(data["bitcoin"]["usd"]), "CoinGecko"

def _get_bybit(symbol="BTCUSDT"):
    r = requests.get(
        f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}",
        timeout=5, headers=UA)
    r.raise_for_status()
    data = r.json()
    return float(data["result"]["list"][0]["lastPrice"]), "Bybit"

def obtener_precio(simbolo="BTCUSDT") -> dict:
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
# 🕐 SESIÓN NEW YORK ACTIVA
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    wd = now.weekday()
    if wd >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES BINANCE
# ============================================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=200):
    try:
        if client:
            data = client.get_klines(symbol=simbolo, interval=intervalo, limit=limite)
        else:
            url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"
            r = requests.get(url, timeout=10, headers=UA)
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
    if not velas:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    if len(closes) < 5:
        return {"estado": "sin_datos"}
    up = closes[-1] > closes[0]
    return {"estado": "alcista" if up else "bajista"}

# ============================================================
# 🟣 PDH/PDL ÚLTIMAS 24H
# ============================================================

def _pdh_pdl(simbolo="BTCUSDT") -> dict:
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=96"
        r = requests.get(url, timeout=10, headers=UA)
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
