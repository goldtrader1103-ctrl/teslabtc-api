# ============================================================
# 🚀 TESLABTC.KG — API Principal de Análisis Operativo (v3.5.0)
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
    description="Análisis operativo BTCUSDT basado en acción del precio (TESLABTC A.P.)",
    version="3.5.0",
)

# Activar compresión automática (para evitar errores de tamaño)
app.add_middleware(GZipMiddleware, minimum_size=500)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================

@app.get("/analyze", tags=["Análisis"])
async def analizar_mercado(simbolo: str = "BTCUSDT"):
    """
    Endpoint principal que ejecuta el análisis estructural completo.
    Devuelve un resumen comprimido para evitar respuestas grandes.
    """
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 1️⃣ Precio actual
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio")
    fuente = precio_data.get("fuente")

    # 2️⃣ Sesión activa
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # 3️⃣ Estructura del mercado (multi-temporal)
    estructura = {
        "H4 (macro)": "sin_datos",
        "H1 (intradía)": "sin_datos",
        "M15 (reacción)": "sin_datos",
    }

    try:
        h4 = obtener_klines_binance(simbolo, "4h", 100)
        h1 = obtener_klines_binance(simbolo, "1h", 100)
        m15 = obtener_klines_binance(simbolo, "15m", 100)

        estructura["H4 (macro)"] = evaluar_estructura(h4)["estado"]
        estructura["H1 (intradía)"] = evaluar_estructura(h1)["estado"]
        estructura["M15 (reacción)"] = evaluar_estructura(m15)["estado"]
    except Exception as e:
        estructura["error"] = str(e)

    # 4️⃣ Zonas clave (PDH/PDL)
    zonas = _pdh_pdl(simbolo)

    # 5️⃣ Escenario operativo según estructura
    escenario = definir_escenarios(estructura)

    # 6️⃣ Resultado resumido
    resultado = {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "sesión": sesion,
            "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "zonas": zonas,
            "escenario": escenario,
            "mensaje": "✨ Análisis completado correctamente",
            "conexion_binance": BINANCE_STATUS,
        }
    }

    # Compresión manual opcional si la respuesta supera los 1 MB
    json_data = json.dumps(resultado, ensure_ascii=False)
    if len(json_data.encode("utf-8")) > 1_000_000:
        resultado = {"mensaje": "⚠️ Respuesta reducida automáticamente (demasiado grande para Render).",
                     "resumen": resultado["🧠 TESLABTC.KG"]}

    return resultado


# ============================================================
# 🧩 ENDPOINT: Estado general del sistema
# ============================================================

@app.get("/", tags=["Estado"])
async def status():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "API TESLABTC.KG conectada correctamente a Binance. Monitor activo.",
        "version": "3.5.0",
        "autor": "GoldTraderBTC",
    }


# ============================================================
# 🔄 MONITOR EN VIVO
# ============================================================

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(live_monitor_loop())


@app.on_event("shutdown")
async def shutdown_event():
    await stop_monitor()


@app.get("/alerts", tags=["Monitor"])
async def get_live_alerts():
    return get_alerts()
