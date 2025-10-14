# ============================================================
# 💰 UTILIDADES DE PRECIO — TESLABTC.KG (compatible global)
# ============================================================

import time
import requests
from datetime import datetime, timedelta, timezone
from binance.exceptions import BinanceAPIException, BinanceOrderException

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.5"}
BINANCE_STATUS = "⏳ Inicializando conexión Binance..."

# ============================================================
# 🧠 FUNCIÓN PRINCIPAL DE CONEXIÓN CON FALLBACK AUTOMÁTICO
# ============================================================

def obtener_precio(simbolo: str = "BTCUSDT") -> dict:
    """
    Intenta obtener el precio actual usando:
      1. Binance API (privada)
      2. Binance público (fallback)
      3. Coinbase (respaldo)
    """
    global BINANCE_STATUS

    # --- 1️⃣ Intentar con Binance (API privada o pública) ---
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo}"
        r = requests.get(url, headers=UA, timeout=5)
        r.raise_for_status()
        precio = float(r.json()["price"])
        BINANCE_STATUS = "✅ Binance (modo público)"
        return {"precio": precio, "fuente": "Binance"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ Error conexión Binance: {e}"
        print(f"[obtener_precio] Binance falló: {e}")

    # --- 2️⃣ Intentar con Coinbase ---
    try:
        pair = simbolo.replace("USDT", "-USD")
        url = f"https://api.coinbase.com/v2/prices/{pair}/spot"
        r = requests.get(url, headers=UA, timeout=5)
        r.raise_for_status()
        data = r.json()
        precio = float(data["data"]["amount"])
        BINANCE_STATUS = "🪙 Coinbase (modo respaldo)"
        return {"precio": precio, "fuente": "Coinbase"}
    except Exception as e:
        BINANCE_STATUS = f"❌ Sin conexión disponible: {e}"
        print(f"[obtener_precio] Error final: {e}")
        return {"precio": None, "fuente": "Error"}

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA (Lunes–Viernes, 07:00–13:30 COL)
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()
    if weekday >= 5:
        return False
    return 7 <= h < 13.5

# ============================================================
# 📊 OBTENER KLINES BINANCE (modo público, sin API key)
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "5m", limite: int = 200):
    """
    Obtiene velas OHLC desde Binance público (sin restricciones).
    Compatible globalmente.
    """
    global BINANCE_STATUS
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"

    try:
        r = requests.get(url, timeout=10, headers=UA)
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

        BINANCE_STATUS = "✅ Velas cargadas correctamente"
        return velas

    except Exception as e:
        BINANCE_STATUS = f"⚠️ Error al obtener klines: {e}"
        print(f"[obtener_klines_binance] Error: {e}")
        return None

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

        return {
            "PDH": max(highs) if highs else None,
            "PDL": min(lows) if lows else None
        }

    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}

# ============================================================
# 📈 DETECTAR ESTRUCTURA SIMPLE (fallback temporal)
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    if not velas:
        return {"estado": "sin_datos"}
    closes = [v["close"] for v in velas[-30:]]
    if len(closes) < 5:
        return {"estado": "sin_datos"}
    up = closes[-1] > closes[0]
    return {"estado": "alcista" if up else "bajista"}
