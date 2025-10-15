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

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

app = FastAPI(
    title="TESLABTC.KG",
    description="Análisis operativo BTCUSDT (Price Action Puro) — estructura, flujo y escenarios.",
    version="3.6.0",
)

# Comprime respuestas grandes para evitar errores en Render
app.add_middleware(GZipMiddleware, minimum_size=600)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔍 ENDPOINT PRINCIPAL — /analyze
# ============================================================

@app.get("/analyze", tags=["Análisis"])
async def analizar(simbolo: str = "BTCUSDT"):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 1️⃣ PRECIO ACTUAL
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio")
    fuente = precio_data.get("fuente")

    # Fallback visual si no hay precio válido
    precio_str = f"{precio:,.2f} USD" if precio not in [None, 0] else "⚙️ No disponible"

    # 2️⃣ SESIÓN DE NUEVA YORK
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # 3️⃣ ESTRUCTURA (H4 / H1 / M15)
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
        "H4 (macro)": e_h4.get("estado", "sin_datos"),
        "H1 (intradía)": e_h1.get("estado", "sin_datos"),
        "M15 (reacción)": e_m15.get("estado", "sin_datos")
    }

    # 4️⃣ ZONAS PDH/PDL
    zonas = _pdh_pdl(simbolo)

    # 5️⃣ ESCENARIO OPERATIVO
    escenario = definir_escenarios(estructura_estados)

    # ==========================
    # 🔹 RESPUESTA PRINCIPAL
    # ==========================
    payload = {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "sesión": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura_detallada,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis completado correctamente"
        }
    }

    # Compactar si el JSON es muy grande
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(encoded) > 900_000:
        payload = {
            "🧠 TESLABTC.KG (resumen)": {
                "fecha": fecha,
                "sesión": sesion,
                "precio_actual": precio_str,
                "estructura": estructura_estados,
                "zonas": zonas,
                "escenario": escenario,
                "conexion_binance": BINANCE_STATUS,
                "nota": "Respuesta resumida automáticamente (GZIP activo)."
            }
        }

    return payload

# ============================================================
# 📡 MONITOR EN VIVO
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
# 🏠 HOME — Estado general
# ============================================================

@app.get("/", tags=["Estado"])
async def home():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "TESLABTC.KG conectado a Binance o CoinGecko. Monitor activo en background.",
        "version": "3.6.0",
        "autor": "GoldTraderBTC"
    }
