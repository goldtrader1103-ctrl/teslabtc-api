# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal
# ============================================================

from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, obtener_klines_binance
from utils.estructura_utils import evaluar_estructura

app = FastAPI(
    title="TESLABTC.KG API",
    description="Análisis estructural y operativo BTCUSDT — Price Action Puro (macro, intradía, reacción y scalping).",
    version="3.5.0"
)

TZ_COL = timezone(timedelta(hours=-5))  # Zona horaria Colombia


@app.get("/")
def estado_general():
    """Verifica que la API esté activa."""
    return {"estado": "✅ TESLABTC.KG API activa y operativa."}


@app.get("/analizar")
def analizar(tipo_operacion: str = "institucional"):
    """
    Endpoint principal TESLABTC.KG
    - tipo_operacion: 'institucional' o 'scalping'
    - Devuelve estructura y escenarios:
        1️⃣ Escenario Conservador (principal)
        2️⃣ Escenario Conservador 2 (reentrada)
        3️⃣ Escenario Scalping (contra tendencia)
    """

    ahora = datetime.now(TZ_COL)
    hora = ahora.hour + ahora.minute / 60
    sesion = "✅ Activa (Sesión New York)" if 7 <= hora < 13.5 else "❌ Cerrada (Fuera de NY)"

    # ===========================
    # 🔹 Precio actual BTCUSDT
    # ===========================
    try:
        precio_data = obtener_precio("BTCUSDT")
        precio_btc = precio_data["precio"]
        fuente = precio_data["fuente"]
        error_msg = None
    except Exception as e:
        precio_btc = None
        fuente = "Ninguna"
        error_msg = str(e)

    # ===========================
    # 🔹 Estructura simulada (por ahora usa detección general)
    # ===========================
    try:
        h4_klines = obtener_klines_binance("BTCUSDT", "4h", 200) or []
        h1_klines = obtener_klines_binance("BTCUSDT", "1h", 200) or []
        m15_klines = obtener_klines_binance("BTCUSDT", "15m", 200) or []
    except Exception as e:
        h4_klines, h1_klines, m15_klines = [], [], []

    # Estos valores pueden reemplazarse por detección real según tu estructura
    H4_dir = "bajista"   # Estructura macro
    H1_dir = "bajista"   # Estructura intradía
    M15_dir = "alcista"  # Retroceso o mitigación

    estructura = evaluar_estructura(H4_dir, H1_dir, M15_dir, tipo_operacion)

    # ===========================
    # 🔹 Respuesta final TESLABTC.KG
    # ===========================
    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:,.2f} USD" if precio_btc else "⚙️ No disponible",
            "fuente": fuente,
            "estructura": estructura,
            "mensaje": "✨ Análisis completado correctamente" if not error_msg else "⚠️ Error parcial",
            "error": error_msg or "Ninguno"
        }
    }
