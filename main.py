# ============================================================
# 🚀 TESLABTC.KG — API Principal (v3.6.0 PRO STABLE)
# ============================================================

import asyncio
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
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
    description="Análisis operativo BTCUSDT (Price Action Puro)",
    version="3.6.0",
)

# Compresión GZIP para evitar errores de respuesta grande
app.add_middleware(GZipMiddleware, minimum_size=600)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 ENDPOINT PRINCIPAL
# ============================================================

@app.get("/analyze", tags=["Análisis"])
async def analizar(simbolo: str = "BTCUSDT"):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio")
    fuente = precio_data.get("fuente")

    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    h4 = obtener_klines_binance(simbolo, "4h", 120)
    h1 = obtener_klines_binance(simbolo, "1h", 120)
    m15 = obtener_klines_binance(simbolo, "15m", 120)

    e_h4 = evaluar_estructura(h4)
    e_h1 = evaluar_estructura(h1)
    e_m15 = evaluar_estructura(m15)

    estructura = {
        "H4 (macro)": e_h4,
        "H1 (intradía)": e_h1,
        "M15 (reacción)": e_m15
    }

    zonas = _pdh_pdl(simbolo)
    escenario = definir_escenarios({
        "H4": e_h4.get("estado"),
        "H1": e_h1.get("estado"),
        "M15": e_m15.get("estado")
    })

    return {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "sesión": sesion,
            "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }

# ============================================================
# 🟣 MONITOR EN VIVO
# ============================================================

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(live_monitor_loop())

@app.on_event("shutdown")
async def shutdown_event():
    stop_monitor()

@app.get("/monitor/status", tags=["Monitor"])
async def monitor_status():
    return get_alerts()

@app.get("/monitor/stop", tags=["Monitor"])
async def monitor_stop():
    stop_monitor()
    return {"estado": "🔴 Monitor detenido"}

# ============================================================
# 🏠 HOME
# ============================================================

@app.get("/", tags=["Estado"])
async def home():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "TESLABTC.KG conectado a Binance Vision y CoinGecko (fallback).",
        "version": "3.6.0",
        "autor": "GoldTraderBTC"
    }
