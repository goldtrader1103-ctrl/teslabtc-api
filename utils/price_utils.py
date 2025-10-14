# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (Conexión Binance Real)
# ============================================================

import os
import time
from datetime import datetime, timedelta, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ============================================================
# 🕐 CONFIGURACIÓN BASE
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Cliente autenticado
try:
    client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
    client.ping()
    BINANCE_STATUS = "✅ API Binance conectada correctamente"
except Exception as e:
    client = None
    BINANCE_STATUS = f"⚠️ Error conexión Binance: {e}"

# ============================================================
# 💰 PRECIO ACTUAL
# ============================================================

def obtener_precio(symbol="BTCUSDT"):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {"precio": float(ticker["price"]), "fuente": "Binance (API)"}
    except Exception as e:
        print(f"[obtener_precio] Error: {e}")
        return {"precio": None, "fuente": "Error Binance"}

# ============================================================
# 📊 VELAS
# ============================================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="15m", limite=200):
    try:
        data = client.get_klines(symbol=simbolo, interval=intervalo, limit=limite)
        velas = [{
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        } for k in data]
        return velas
    except BinanceAPIException as e:
        print(f"[obtener_klines_binance] Error API Binance: {e.message}")
        return None
    except Exception as e:
        print(f"[obtener_klines_binance] Error general: {e}")
        return None

# ============================================================
# 🕒 SESIÓN NY
# ============================================================

def sesion_ny_activa():
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()
    return weekday < 5 and 7 <= h < 13.5

# ============================================================
# 🟣 PDH / PDL
# ============================================================

def _pdh_pdl(simbolo="BTCUSDT"):
    try:
        data = client.get_klines(symbol=simbolo, interval="15m", limit=96)
        cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
        data_filtrada = [k for k in data if datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL) > cutoff]
        highs = [float(k[2]) for k in data_filtrada]
        lows = [float(k[3]) for k in data_filtrada]
        return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
