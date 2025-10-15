# ==============================================
# 📦 TESLABTC.KG — utils/price_utils.py (v3.6.0)
# ==============================================
# 1) Precio actual (Binance Vision REST -> CoinGecko fallback)
# 2) Klines multi-timeframe usando data mirror oficial
# 3) Sesión NY
# 4) PDH/PDL últimas 24h
# ==============================================

import requests
from datetime import datetime, timezone, timedelta

BINANCE_STATUS = "⚙️ No conectado"
TZ_COL = timezone(timedelta(hours=-5))

UA = {"User-Agent": "teslabtc-kg/3.6"}

# Endpoints (data mirror público de Binance)
BINANCE_VISION_BASE = "https://data-api.binance.vision"
BINANCE_REST_BASE = "https://api.binance.com"

# ===============================
# 🔹 FUNCIÓN PRINCIPAL DE PRECIO
# ===============================

def obtener_precio(simbolo="BTCUSDT"):
    """
    Intenta precio desde Binance (REST público) y cae a CoinGecko.
    No requiere API Keys.
    """
    global BINANCE_STATUS

    # Intento 1: Binance REST público
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/ticker/price",
            params={"symbol": simbolo},
            headers=UA, timeout=6
        )
        r.raise_for_status()
        price = float(r.json()["price"])
        BINANCE_STATUS = "✅ Conectado a Binance REST"
        return {"precio": price, "fuente": "Binance (REST)"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ Binance REST: {e}"

    # Intento 2: CoinGecko fallback
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=UA, timeout=6
        )
        r.raise_for_status()
        data = r.json()
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            price = float(data["bitcoin"]["usd"])
            BINANCE_STATUS = "🦎 CoinGecko (fallback)"
            return {"precio": price, "fuente": "CoinGecko"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ CoinGecko: {e}"

    BINANCE_STATUS = "⛔ Sin conexión de precio"
    return {"precio": None, "fuente": "⚙️ No conectado"}

# ===================================
# 🔹 FUNCIÓN DE SESIÓN NEW YORK
# ===================================

def sesion_ny_activa():
    """
    NY: 07:00–13:30 COL (horario operativo PA Puro)
    *Si deseas extender a 16:00 COL, cambia el fin a 16:00.
    """
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    return 7 <= h < 13.5  # 13:30

# ===================================
# 🔹 FUNCIÓN DE VELAS (klines)
# ===================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=120):
    """
    Devuelve velas desde el mirror público (data-api.binance.vision) y si falla, usa api.binance.com.
    Formato de retorno: lista de velas Kline como en Binance REST.
    """
    # Intento 1: data mirror
    try:
        url = f"{BINANCE_VISION_BASE}/api/v3/klines"
        r = requests.get(url, params={"symbol": simbolo, "interval": intervalo, "limit": limite},
                         headers=UA, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        pass

    # Intento 2: REST directo
    try:
        url = f"{BINANCE_REST_BASE}/api/v3/klines"
        r = requests.get(url, params={"symbol": simbolo, "interval": intervalo, "limit": limite},
                         headers=UA, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

# ===================================
# 🔹 FUNCIÓN PDH / PDL 24h
# ===================================

def _pdh_pdl(simbolo="BTCUSDT"):
    """
    Máximo y mínimo de últimas 24h usando klines 1h x 24.
    """
    try:
        klines = obtener_klines_binance(simbolo, "1h", 24)
        highs = [float(k[2]) for k in klines] if klines else []
        lows  = [float(k[3]) for k in klines] if klines else []
        return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
    except Exception:
        return {"PDH": None, "PDL": None}
