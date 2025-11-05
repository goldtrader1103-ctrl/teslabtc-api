# ==============================================
# 📦 TESLABTC.KG — utils/price_utils.py (v3.6.3)
# ==============================================
# 1️⃣ Precio actual (Binance REST -> CoinGecko fallback)
# 2️⃣ Klines multi-timeframe (Binance Global -> Binance Vision -> CoinGecko)
# 3️⃣ Sesión NY
# 4️⃣ PDH/PDL últimas 24h
# ==============================================

import requests
import time
from datetime import datetime, timezone, timedelta

BINANCE_STATUS = "🦎 Fallback CoinGecko activo"
TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.6"}

# ==============================================
# 🌐 Endpoints base
# ==============================================
BINANCE_REST_BASE = "https://api.binance.com"
BINANCE_VISION_BASE = "https://data-api.binance.vision"

# ==============================================
# 💰 FUNCIÓN PRINCIPAL DE PRECIO
# ==============================================

def obtener_precio(simbolo="BTCUSDT"):
    """
    Obtiene el precio actual desde Binance REST y cae a CoinGecko si hay bloqueo.
    No requiere API Keys.
    """
    global BINANCE_STATUS

    # Intento 1️⃣ — Binance REST público
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/ticker/price",
            params={"symbol": simbolo},
            headers=UA,
            timeout=6,
        )
        r.raise_for_status()
        price = float(r.json()["price"])
        BINANCE_STATUS = "✅ Conectado a Binance REST"
        return {"precio": price, "fuente": "Binance (REST)"}
    except Exception as e:
        BINANCE_STATUS = f"⚠️ Binance REST: {e}"

    # Intento 2️⃣ — CoinGecko fallback
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=UA,
            timeout=6,
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

# ==============================================
# 🕒 SESIÓN NEW YORK (07:00–13:30 COL)
# ==============================================

def sesion_ny_activa():
    """
    Verifica si la sesión de Nueva York está activa.
    NY: 07:00–13:30 hora Colombia.
    """
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    return 7 <= h < 13.5  # 13:30

# ==============================================
# 📊 FUNCIÓN DE VELAS (KLINES)
# ==============================================

def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=120):
    """
    🔁 Sistema híbrido:
        1️⃣ Binance Global
        2️⃣ Binance Vision (si Global bloquea)
        3️⃣ CoinGecko (fallback)
    Devuelve lista de velas en formato dict y actualiza BINANCE_STATUS.
    """
    global BINANCE_STATUS
    simbolo = str(simbolo).upper()  # ✅ Asegura formato correcto

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Connection": "keep-alive",
    }

    urls = [
        ("Binance Global", f"{BINANCE_REST_BASE}/api/v3/klines"),
        ("Binance Vision", f"{BINANCE_VISION_BASE}/api/v3/klines"),
    ]

    last_err = None

    for src, url in urls:
        try:
            for intento in range(3):
                r = requests.get(
                    url,
                    params={"symbol": simbolo, "interval": intervalo, "limit": limite},
                    headers=headers,
                    timeout=10,
                )

                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        BINANCE_STATUS = f"✅ Klines desde {src}"
                        klines = []
                        for k in data:
                            klines.append({
                                "open_time": k[0],
                                "open": float(k[1]),
                                "high": float(k[2]),
                                "low": float(k[3]),
                                "close": float(k[4]),
                                "volume": float(k[5])
                            })
                        return klines

                elif r.status_code == 451:
                    print(f"⚠️ {src} bloqueado ({r.status_code}), probando mirror Vision...")
                    break

                elif r.status_code in (403, 429):
                    print(f"⚠️ Límite o bloqueo temporal ({r.status_code}) desde {src}, reintentando...")
                    time.sleep(2)
                    continue

                else:
                    last_err = f"HTTP {r.status_code} desde {src}"
                    break

        except Exception as e:
            last_err = f"{src}: {type(e).__name__} {e}"

    # ==========================================
    # 🦎 Fallback CoinGecko si Binance falla
    # ==========================================
    try:
        cg_interval = "hourly" if "m" in intervalo or "h" in intervalo else "daily"
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": 7, "interval": cg_interval},
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        prices = r.json().get("prices", [])
        if prices:
            BINANCE_STATUS = "🦎 Fallback CoinGecko (simulación de velas)"
            klines = []
            for ts, price in prices[-limite:]:
                k = {
                    "open_time": ts,
                    "open": float(price),
                    "high": float(price),
                    "low": float(price),
                    "close": float(price),
                    "volume": 0.0
                }
                klines.append(k)
            return klines
    except Exception as e:
        last_err = f"CoinGecko: {e}"

    BINANCE_STATUS = f"⛔ Sin datos válidos ({last_err})"
    print(BINANCE_STATUS)
    return []

# ==============================================
# 📈 FUNCIÓN PDH / PDL (ÚLTIMAS 24H)
# ==============================================

def _pdh_pdl(simbolo="BTCUSDT"):
    """
    Calcula el máximo (PDH) y mínimo (PDL) de las últimas 24h usando velas 1h.
    """
    try:
        klines = obtener_klines_binance(simbolo, "1h", 24)
        highs = [float(k["high"]) for k in klines] if klines else []
        lows = [float(k["low"]) for k in klines] if klines else []
        return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}
    except Exception as e:
        print(f"⚠️ Error PDH/PDL: {e}")
        return {"PDH": None, "PDL": None}

# ==============================================
# 📊 ESTADO BINANCE
# ==============================================

def estado_binance():
    """
    Devuelve el estado actual de conexión de Binance o CoinGecko.
    """
    return BINANCE_STATUS
