# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (v3.6.0)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.6"}

# ============================================================
# 🔐 CONEXIÓN BINANCE
# ============================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

BINANCE_STATUS = "⚙️ Inicializando conexión Binance..."
client = None

try:
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    client.ping()
    BINANCE_STATUS = "✅ Conectado correctamente a Binance"
except Exception as e:
    BINANCE_STATUS = f"⚠️ Error conexión Binance: {e}"
    client = None

# ============================================================
# 💰 OBTENER PRECIO ACTUAL
# ============================================================

def obtener_precio(simbolo: str = "BTCUSDT") -> dict:
    global BINANCE_STATUS
    try:
        if client:
            ticker = client.get_symbol_ticker(symbol=simbolo)
            return {"precio": float(ticker["price"]), "fuente": "Binance"}
        raise Exception("Cliente Binance no disponible")
    except Exception as e:
        BINANCE_STATUS = f"⚠️ Error Binance: {e}"
        # fallback rápido
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                timeout=5, headers=UA
            )
            data = r.json()
            return {"precio": float(data["bitcoin"]["usd"]), "fuente": "CoinGecko"}
        except Exception:
            return {"precio": None, "fuente": "No disponible"}

# ============================================================
# 📊 OBTENER KLINES
# ============================================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=100):
    try:
        if client:
            kl = client.get_klines(symbol=simbolo, interval=intervalo, limit=limite)
            return [{
                "open_time": datetime.fromtimestamp(k[0]/1000, tz=TZ_COL),
                "open": float(k[1]), "high": float(k[2]),
                "low": float(k[3]), "close": float(k[4])
            } for k in kl]
        raise Exception("Cliente Binance no disponible")
    except Exception as e:
        print(f"[obtener_klines_binance] Error: {e}")
        return None

# ============================================================
# 🕐 SESIÓN NY ACTIVA
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute/60
    return now.weekday() < 5 and 7 <= h < 13.5

# ============================================================
# 🟣 PDH / PDL
# ============================================================

def _pdh_pdl(simbolo="BTCUSDT"):
    try:
        kl = client.get_klines(symbol=simbolo, interval="15m", limit=96)
        cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
        f = [k for k in kl if datetime.fromtimestamp(k[0]/1000, tz=TZ_COL) > cutoff]
        highs = [float(k[2]) for k in f]; lows = [float(k[3]) for k in f]
        return {"PDH": max(highs), "PDL": min(lows)} if highs and lows else {"PDH": None, "PDL": None}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
