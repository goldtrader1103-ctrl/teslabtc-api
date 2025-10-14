# ============================================================
# 🚀 TESLABTC.KG — API Principal de Análisis Operativo
# ============================================================

from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    sesion_ny_activa,
    _pdh_pdl,
    BINANCE_STATUS
)
from utils.estructura_utils import evaluar_estructura, definir_escenarios

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

app = FastAPI(
    title="TESLABTC.KG",
    description="Análisis operativo BTCUSDT basado en Price Action puro (TESLABTC A.P.)",
    version="3.2.0",
)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔍 ENDPOINT PRINCIPAL: /analizar
# ============================================================

@app.get("/analizar", tags=["TESLABTC"])
def analizar():
    """Devuelve el análisis operativo del mercado BTCUSDT en tiempo real."""
    ahora = datetime.now(TZ_COL)
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # ============================================================
    # 💰 PRECIO ACTUAL
    # ============================================================
    try:
        data_precio = obtener_precio("BTCUSDT")
        precio = data_precio.get("precio")
        fuente = data_precio.get("fuente")
        error_msg = None
    except Exception as e:
        precio = None
        fuente = "Ninguna"
        error_msg = str(e)

    # ============================================================
    # 📊 ESTRUCTURA MULTITIMEFRAME
    # ============================================================
    try:
        velas_h4 = obtener_klines_binance("BTCUSDT", "4h", 120)
        velas_h1 = obtener_klines_binance("BTCUSDT", "1h", 120)
        velas_m15 = obtener_klines_binance("BTCUSDT", "15m", 120)

        resultado = evaluar_estructura(velas_h4, velas_h1, velas_m15)
        estructura = resultado["estructura"]
        zonas = resultado["zonas"]
        contexto = resultado["contexto"]

        escenarios = definir_escenarios(estructura, zonas, sesion_ny_activa())
        escenario = escenarios[0] if escenarios else {"escenario": "SIN CONFIRMACIÓN"}
    except Exception as e:
        estructura = {
            "H4 (macro)": "sin_datos",
            "H1 (intradía)": "sin_datos",
            "M15 (reacción)": "sin_datos",
        }
        zonas = {}
        contexto = "sin_datos"
        escenario = {"escenario": "sin_confirmacion"}
        error_msg = f"Error estructura: {e}"

    # ============================================================
    # 🟣 ZONAS PDH / PDL
    # ============================================================
    try:
        zonas.update(_pdh_pdl("BTCUSDT"))
    except Exception as e:
        zonas["PDH"] = None
        zonas["PDL"] = None
        print(f"[pdh_pdl] Error: {e}")

    # ============================================================
    # 📦 RESPUESTA FINAL JSON
    # ============================================================
    mensaje = "✨ Análisis completado correctamente"
    precio_str = f"{precio:,.2f} USD" if precio else "⚙️ No disponible"

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "contexto_estructural": contexto,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": mensaje,
            "error": error_msg or "Ninguno",
        }
    }

# ============================================================
# 🌐 ENDPOINT RAÍZ
# ============================================================

@app.get("/", tags=["Estado"])
def home():
    """Página base: información del servicio TESLABTC.KG"""
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "API TESLABTC.KG conectada y lista para análisis en tiempo real.",
        "url": "https://teslabtc-api.onrender.com/analizar",
        "version": "3.2.0",
    }
