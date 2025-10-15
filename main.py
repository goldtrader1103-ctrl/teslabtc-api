# ============================================================
# 🚀 TESLABTC.KG — API Principal (v3.6.0 PRO)
# ============================================================

import asyncio
import json
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

app = FastAPI(
    title="TESLABTC.KG",
    description="Análisis operativo BTCUSDT (Price Action Puro)",
    version="3.6.0",
)

# Comprime respuestas para evitar cortes por tamaño en Render
app.add_middleware(GZipMiddleware, minimum_size=600)

TZ_COL = timezone(timedelta(hours=-5))

# ============================
# ENDPOINT PRINCIPAL: /analyze
# ============================

@app.get("/analyze", tags=["Análisis"])
async def analizar(simbolo: str = "BTCUSDT"):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 1) Precio
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio"); fuente = precio_data.get("fuente")

    # 2) Sesión
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # 3) Estructura (H4/H1/M15)
    h4 = obtener_klines_binance(simbolo, "4h", 100)
    h1 = obtener_klines_binance(simbolo, "1h", 100)
    m15 = obtener_klines_binance(simbolo, "15m", 100)

    e_h4 = evaluar_estructura(h4)
    e_h1 = evaluar_estructura(h1)
    e_m15 = evaluar_estructura(m15)

    estructura_detallada = {
        "H4 (macro)": e_h4,
        "H1 (intradía)": e_h1,
        "M15 (reacción)": e_m15
    }
    estructura_estados = {
        "H4 (macro)": e_h4["estado"],
        "H1 (intradía)": e_h1["estado"],
        "M15 (reacción)": e_m15["estado"]
    }

    # 4) Zonas PDH/PDL (24h)
    zonas = _pdh_pdl(simbolo)

    # 5) Escenario
    escenario = definir_escenarios(estructura_estados)

    payload = {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "sesión": sesion,
            "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
            "fuente_precio": fuente,
            "estructura_detectada": estructura_detallada,   # incluye estado + high/low
            "zonas": zonas,                                  # PDH/PDL
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }

    # Resumen compacto si el JSON fuera grande (backup al GZIP)
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(encoded) > 1_000_000:
        payload = {
            "🧠 TESLABTC.KG (resumen)": {
                "fecha": fecha,
                "sesión": sesion,
                "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
                "estructura": estructura_estados,
                "zonas": zonas,
                "escenario": escenario,
                "conexion_binance": BINANCE_STATUS,
                "nota": "Respuesta reducida automáticamente."
            }
        }
    return payload

# ============================
# MONITOR EN VIVO
# ============================

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

# ============================
# HOME
# ============================

@app.get("/", tags=["Estado"])
async def home():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "TESLABTC.KG conectado a Binance. GZIP activo. Monitor en background.",
        "version": "3.6.0",
        "autor": "GoldTraderBTC"
    }
