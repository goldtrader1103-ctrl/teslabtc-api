# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG (versión final)
# ============================================================

import time
import requests
import os
from datetime import datetime, timedelta, timezone
from utils.estructura_utils import analizar_estructura_multinivel, determinar_escenario

TZ_COL = timezone(timedelta(hours=-5))
UA = {"User-Agent": "teslabtc-kg/3.0"}

# ============================================================
# 🔐 CLAVES API BINANCE (Render Env + Secret File)
# ============================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = None

try:
    with open("/etc/secrets/BINANCE_API_SECRET", "r") as f:
        BINANCE_API_SECRET = f.read().strip()
except Exception:
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# ============================================================
# 💰 FUNCIONES BASE DE CONEXIÓN
# ============================================================

def _get_binance(symbol="BTCUSDT"):
    headers = {"User-Agent": "teslabtc-kg/3.0"}
    if BINANCE_API_KEY:
        headers["X-MBX-APIKEY"] = BINANCE_API_KEY
    r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=5, headers=headers)
    r.raise_for_status()
    return float(r.json()["price"]), "Binance"

def obtener_klines(symbol="BTCUSDT", interval="5m", limit=200):
    headers = {"User-Agent": "teslabtc-kg/3.0"}
    if BINANCE_API_KEY:
        headers["X-MBX-APIKEY"] = BINANCE_API_KEY
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url, timeout=10, headers=headers)
    r.raise_for_status()
    data = r.json()
    return [
        {
            "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
            "open": float(k[1]), "high": float(k[2]),
            "low": float(k[3]), "close": float(k[4]),
            "volume": float(k[5]),
        }
        for k in data
    ]

# ============================================================
# 📊 ANÁLISIS COMPLETO DEL MERCADO TESLABTC
# ============================================================

def analizar_mercado(symbol="BTCUSDT"):
    precio, fuente = _get_binance(symbol)
    velas_h4 = obtener_klines(symbol, "4h", 300)
    velas_h1 = obtener_klines(symbol, "1h", 300)
    velas_m15 = obtener_klines(symbol, "15m", 200)

    estructura = analizar_estructura_multinivel(velas_h4, velas_h1, velas_m15)
    escenario = determinar_escenario(estructura)

    # PDH/PDL
    highs = [v["high"] for v in velas_h1[-96:]]
    lows = [v["low"] for v in velas_h1[-96:]]
    pdh = max(highs)
    pdl = min(lows)

    return {
        "🧠 TESLABTC.KG": {
            "fecha": datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": "✅ Activa (Sesión New York)" if sesion_ny_activa() else "🕐 Cerrada (Fuera de NY)",
            "precio_actual": f"{precio:,.2f} USD",
            "fuente_precio": fuente,
            "estructura_detectada": {
                "H4 (macro)": estructura["H4"],
                "H1 (intradía)": estructura["H1"],
                "M15 (reacción)": estructura["M15"]
            },
            "zonas": {
                "PDH (alto 24h)": pdh,
                "PDL (bajo 24h)": pdl,
                "ZONA H4": estructura["zonas"]["H4"],
                "ZONA H1": estructura["zonas"]["H1"],
                "ZONA M15": estructura["zonas"]["M15"]
            },
            "escenario": escenario,
            "mensaje": "✨ Análisis completado correctamente",
            "error": "Ninguno"
        }
    }

# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA
# ============================================================

def sesion_ny_activa() -> bool:
    now = datetime.now(TZ_COL)
    h = now.hour + now.minute / 60
    weekday = now.weekday()
    return weekday < 5 and 7 <= h < 13.5

# ============================================================
# 🧠 VERIFICACIÓN DE CARGA DE FUNCIONES (DEBUG TESLABTC)
# ============================================================

if __name__ == "__main__":
    try:
        resultado = obtener_precio()
        print(f"[TESLABTC.KG] 🔍 Prueba de obtener_precio OK → {resultado}")
    except Exception as e:
        print(f"[TESLABTC.KG] ❌ Error al probar obtener_precio: {e}")
