# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (versión final estable)
# ============================================================

import os
import time
import requests
from datetime import datetime, timedelta, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.5"}

# ============================================================
# 🔐 CONEXIÓN BINANCE (usando claves del entorno)
# ============================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

BINANCE_STATUS = "⚙️ Inicializando conexión Binance..."
client = None

try:
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    client.ping()  # verifica conexión
    BINANCE_STATUS = "✅ Conectado correctamente a Binance"
except Exception as e:
    BINANCE_STATUS = f"⚠️ Error conexión Binance: {e}"
    client = None

# ============================================================
# 💰 OBTENER PRECIO ACTUAL
# ============================================================

def obtener_precio(simbolo: str = "BTCUSDT") -> dict:
    """
    Devuelve el precio actual de BTCUSDT desde Binance.
    Si Binance falla, usa CoinGecko o Coinbase como respaldo.
    """
    global BINANCE_STATUS
    try:
        if client:
            ticker = client.get_symbol_ticker(symbol=simbolo)
            precio = float(ticker["price"])
            return {"precio": precio, "fuente": "Binance"}
        else:
            raise ConnectionError("Cliente Binance no disponible")
    except (BinanceAPIException, BinanceOrderException, Exception) as e:
        BINANCE_STATUS = f"⚠️ Error conexión Binance: {e}"
        # --- Fallback 1: Coinbase ---
        try:
            pair = simbolo.replace("USDT", "-USD")
            r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=5, headers=UA)
            r.raise_for_status()
            data = r.json()
            return {"precio": float(data["data"]["amount"]), "fuente": "Coinbase"}
        except Exception:
            # --- Fallback 2: CoinGecko ---
            try:
                r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
                data = r.json()
                return {"precio": float(data["bitcoin"]["usd"]), "fuente": "CoinGecko"}
            except Exception:
                return {"precio": None, "fuente": "No disponible"}

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA (Lunes–Viernes, 07:00–13:30 COL)
# ============================================================

def sesion_ny_activa() -> bool:
    """
    Verifica si la sesión de New York está activa
    considerando hora Colombia (UTC-5) y días hábiles.
    Activa: Lunes a Viernes entre 07:00 y 13:30.
    """
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()  # 0 = Lunes ... 6 = Domingo
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES (velas históricas)
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "5m", limite: int = 200):
    """
    Devuelve velas de Binance en formato limpio para análisis.
    """
    global BINANCE_STATUS
    try:
        if client:
            klines = client.get_klines(symbol=simbolo, interval=intervalo, limit=limite)
            velas = [{
                "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
                "open": float(k[1]), "high": float(k[2]),
                "low": float(k[3]), "close": float(k[4]), "volume": float(k[5])
            } for k in klines]
            return velas
        else:
            raise ConnectionError("Cliente Binance no disponible")
    except (BinanceAPIException, Exception) as e:
        BINANCE_STATUS = f"⚠️ Error klines Binance: {e}"
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
# 🟣 PDH / PDL (High & Low últimas 24h)
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT") -> dict:
    try:
        if client:
            klines = client.get_klines(symbol=simbolo, interval="15m", limit=96)
            cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
            data_filtrada = [k for k in klines if datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL) > cutoff]
            highs = [float(k[2]) for k in data_filtrada]
            lows = [float(k[3]) for k in data_filtrada]
            return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
        else:
            raise ConnectionError("Cliente Binance no disponible")
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
