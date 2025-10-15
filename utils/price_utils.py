import requests
from datetime import datetime, timezone, timedelta

# ==============================================
# 📦 TESLABTC.KG — price_utils.py (v3.6.0 PRO)
# ==============================================
# Módulo encargado de:
# 1️⃣ Obtener el precio actual de BTCUSDT.
# 2️⃣ Consultar velas (klines) para H4, H1, M15.
# 3️⃣ Verificar sesión de Nueva York.
# 4️⃣ Calcular PDH/PDL de las últimas 24h.
# ==============================================

BINANCE_STATUS = "⚙️ No conectado"
TZ_COL = timezone(timedelta(hours=-5))

# ===============================
# 🔹 FUNCIÓN PRINCIPAL DE PRECIO
# ===============================

def obtener_precio(simbolo="BTCUSDT"):
    """Obtiene el precio actual del símbolo desde Binance o CoinGecko (fallback)."""
    global BINANCE_STATUS

    # --- Intento 1: Binance Vision ---
    try:
        from binance.spot import Spot as Client
        client = Client()
        data = client.ticker_price(symbol=simbolo)
        precio = float(data["price"])
        BINANCE_STATUS = "✅ Conectado a Binance Vision"
        return {"precio": precio, "fuente": "Binance (Vision)"}

    except Exception as e:
        print(f"[⚠️ Binance Error]: {e}")
        BINANCE_STATUS = f"⚠️ Error de conexión Binance: {e}"

    # --- Intento 2: CoinGecko (fallback) ---
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=5,
        )
        data = r.json()
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            precio = float(data["bitcoin"]["usd"])
            BINANCE_STATUS = "🦎 Conectado a CoinGecko (fallback)"
            return {"precio": precio, "fuente": "CoinGecko"}

    except Exception as e:
        print(f"[⚠️ CoinGecko Error]: {e}")

    # --- Si ambas fuentes fallan ---
    BINANCE_STATUS = "⚙️ Sin conexión a fuentes válidas"
    return {"precio": None, "fuente": "⚙️ No conectado"}

# ===================================
# 🔹 FUNCIÓN DE SESIÓN NEW YORK
# ===================================

def sesion_ny_activa():
    """Verifica si la sesión de Nueva York está activa (07:00 - 16:00 hora Colombia)."""
    hora_local = datetime.now(TZ_COL).time()
    return hora_local >= datetime.strptime("07:00", "%H:%M").time() and hora_local <= datetime.strptime("16:00", "%H:%M").time()

# ===================================
# 🔹 FUNCIÓN DE VELAS BINANCE
# ===================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=100):
    """Obtiene velas del mercado desde Binance Vision (sin API key)."""
    try:
        from binance.spot import Spot as Client
        client = Client()
        data = client.klines(symbol=simbolo, interval=intervalo, limit=limite)
        return data
    except Exception as e:
        print(f"[⚠️ Kline Error {intervalo}]: {e}")
        return []

# ===================================
# 🔹 FUNCIÓN PDH / PDL
# ===================================

def _pdh_pdl(simbolo="BTCUSDT"):
    """Calcula el máximo (PDH) y mínimo (PDL) de las últimas 24h."""
    try:
        klines = obtener_klines_binance(simbolo, "1h", 24)
        if klines:
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
            return {"PDH": max(highs), "PDL": min(lows)}
    except Exception as e:
        print(f"[⚠️ PDH/PDL Error]: {e}")
    return {"PDH": None, "PDL": None}
