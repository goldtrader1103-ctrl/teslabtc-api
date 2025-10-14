# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal (v4.0)
# ============================================================

from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    detectar_estructura,
    _pdh_pdl,
)
from utils.estructura_utils import evaluar_estructura

app = FastAPI(
    title="TESLABTC.KG API",
    description="Análisis operativo real BTCUSDT basado en Price Action puro — estructura, POI, BOS, zonas de reacción y escenarios.",
    version="4.0.0"
)

TZ_COL = timezone(timedelta(hours=-5))


@app.get("/")
def estado_general():
    """Verifica que la API esté operativa."""
    return {"estado": "✅ TESLABTC.KG API activa y operativa."}


@app.get("/analizar")
def analizar(tipo_operacion: str = "institucional"):
    """
    Análisis operativo TESLABTC.KG
    - Detecta estructura real (H4, H1, M15)
    - Define escenarios conservadores y scalping
    - Indica zonas de reacción (PDH/PDL)
    """

    ahora = datetime.now(TZ_COL)
    hora = ahora.hour + ahora.minute / 60
    sesion = "✅ Activa (Sesión New York)" if 7 <= hora < 13.5 else "❌ Cerrada (Fuera de NY)"

    # ============================================================
    # 💰 PRECIO ACTUAL
    # ============================================================
    try:
        precio_data = obtener_precio("BTCUSDT")
        precio_btc = precio_data["precio"]
        fuente = precio_data["fuente"]
        error_msg = None
    except Exception as e:
        precio_btc, fuente, error_msg = None, "Ninguna", str(e)

    # ============================================================
    # 📊 ESTRUCTURA REAL DESDE BINANCE
    # ============================================================
    try:
        h4_klines = obtener_klines_binance("BTCUSDT", "4h", 200)
        h1_klines = obtener_klines_binance("BTCUSDT", "1h", 200)
        m15_klines = obtener_klines_binance("BTCUSDT", "15m", 200)

        H4_dir = detectar_estructura(h4_klines)["estado"]
        H1_dir = detectar_estructura(h1_klines)["estado"]
        M15_dir = detectar_estructura(m15_klines)["estado"]
    except Exception as e:
        H4_dir, H1_dir, M15_dir = "sin_datos", "sin_datos", "sin_datos"
        error_msg = str(e)

    # ============================================================
    # 🟣 PDH/PDL (últimas 24h)
    # ============================================================
    zonas = _pdh_pdl("BTCUSDT")

    # ============================================================
    # 🧭 ESCENARIO DETECTADO
    # ============================================================
    estructura = evaluar_estructura(H4_dir, H1_dir, M15_dir, tipo_operacion)

    # ============================================================
    # 📦 RESPUESTA FINAL TESLABTC.KG
    # ============================================================
    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:,.2f} USD" if precio_btc else "⚙️ No disponible",
            "fuente_precio": fuente,
            "estructura_detectada": {
                "H4 (macro)": H4_dir,
                "H1 (intradía)": H1_dir,
                "M15 (reacción)": M15_dir,
            },
            "zonas": {
                "PDH (alto 24h)": zonas["PDH"],
                "PDL (bajo 24h)": zonas["PDL"],
            },
            "escenario": estructura,
            "mensaje": "✨ Análisis completado correctamente" if not error_msg else "⚠️ Error parcial",
            "error": error_msg or "Ninguno"
        }
    }
