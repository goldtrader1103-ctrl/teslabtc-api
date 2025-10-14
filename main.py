# ============================================================
# 🚀 TESLABTC.KG — API Principal de Análisis Operativo
# ============================================================

import asyncio
from fastapi import FastAPI
from datetime import datetime, timedelta, timezone

from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    sesion_ny_activa,
    _pdh_pdl,
    BINANCE_STATUS,
)
from utils.estructura_utils import evaluar_estructura, definir_escenarios
from utils.live_monitor import live_monitor_loop, stop_monitor, get_alerts

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

app = FastAPI(
    title="TESLABTC.KG",
    description="Análisis operativo BTCUSDT basado en Price Action puro (TESLABTC A.P.)",
    version="3.4.0",
)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔁 ARRANQUE DEL MONITOR EN BACKGROUND
# ============================================================

_monitor_task = None

@app.on_event("startup")
async def _start_monitor():
    global _monitor_task
    # Inicia el loop de alertas cada 5 minutos (ajustable)
    _monitor_task = asyncio.create_task(live_monitor_loop(interval_min=5))

@app.on_event("shutdown")
async def _stop_monitor():
    stop_monitor()
    if _monitor_task:
        try:
            _monitor_task.cancel()
        except Exception:
            pass

# ============================================================
# 🔍 ENDPOINT PRINCIPAL: /analizar
# ============================================================

@app.get("/analizar", tags=["TESLABTC"])
def analizar():
    ahora = datetime.now(TZ_COL)
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # 💰 Precio actual
    data_precio = obtener_precio("BTCUSDT")
    precio = data_precio.get("precio")
    fuente = data_precio.get("fuente")

    # 📊 Estructura multitemporal
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
        print(f"[estructura] Error: {e}")

    # 🟣 PDH/PDL
    try:
        zonas.update(_pdh_pdl("BTCUSDT"))
    except Exception as e:
        zonas["PDH"] = None
        zonas["PDL"] = None
        print(f"[pdh_pdl] Error: {e}")

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "contexto_estructural": contexto,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis completado correctamente",
        }
    }

# ============================================================
# 🔔 ENDPOINT: /alertas (estado y últimas señales del monitor)
# ============================================================

@app.get("/alertas", tags=["TESLABTC"])
def alertas():
    """
    Devuelve:
      - Estado del monitor (corriendo, último tick, intervalo)
      - Últimas alertas detectadas (A+, SCALPING, CHOCH_H1, INFO_M15, etc.)
    """
    return get_alerts()

# ============================================================
# 🌐 ENDPOINT BASE
# ============================================================

@app.get("/", tags=["Estado"])
def home():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "API TESLABTC.KG conectada correctamente a Binance. Monitor en background activo.",
        "version": "3.4.0",
        "autor": "GoldTraderBTC",
    }
