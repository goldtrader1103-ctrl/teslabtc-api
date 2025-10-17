# ============================================================
# 🚀 TESLABTC.KG — API Principal (v3.6.0 PRO STABLE)
# ============================================================

import asyncio
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
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

# 🔧 Forzar codificación UTF-8 global (evita símbolos raros)
JSONResponse.media_type = "application/json; charset=utf-8"

# Compresión GZIP para optimizar respuestas grandes
app.add_middleware(GZipMiddleware, minimum_size=600)

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 ENDPOINT PRINCIPAL
# ============================================================

@app.get("/analyze", tags=["Análisis"])
async def analizar(simbolo: str = "BTCUSDT", token: str | None = None):
    """
    Endpoint principal: análisis operativo TESLABTC.KG
    Retorna estructura, zonas, escenario y conexión Binance.
    """
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # Precio actual
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio")
    fuente = precio_data.get("fuente")
    precio_str = f"{precio:,.2f} USD" if precio not in [None, 0] else "⚙️ No disponible"

    # Sesión
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # Velas
    h4 = obtener_klines_binance(simbolo, "4h", 120)
    h1 = obtener_klines_binance(simbolo, "1h", 120)
    m15 = obtener_klines_binance(simbolo, "15m", 120)

    # Estructura (estado + zonas high/low)
    e_h4 = evaluar_estructura(h4)
    e_h1 = evaluar_estructura(h1)
    e_m15 = evaluar_estructura(m15)

    estructura = {
        "H4 (macro)": e_h4,
        "H1 (intradía)": e_h1,
        "M15 (reacción)": e_m15,
    }

    # Zonas PDH/PDL (24h)
    zonas = _pdh_pdl(simbolo)

    # Escenario operativo (conservador / scalping / rango)
    escenario = definir_escenarios({
        "H4": e_h4.get("estado", "sin_datos"),
        "H1": e_h1.get("estado", "sin_datos"),
        "M15": e_m15.get("estado", "sin_datos"),
    })

    # Paquete final de respuesta
    payload = {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "nivel_usuario": "Premium" if token and "PREMIUM" in token else "Free",
            "sesión": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }

    return JSONResponse(content=payload)

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
        "descripcion": "TESLABTC.KG conectado a Binance (data mirror) y CoinGecko (fallback).",
        "version": "3.6.0",
        "autor": "GoldTraderBTC"
    }
