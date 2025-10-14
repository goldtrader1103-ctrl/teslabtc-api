# ============================================================
# 🚀 TESLABTC.KG — API Principal de Análisis Operativo
# ============================================================

import asyncio
from fastapi import FastAPI
from datetime import datetime, timedelta, timezone

# === Importar utilidades actualizadas ===
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
    version="3.5.0",
)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 FUNCIÓN PRINCIPAL — /analizar
# ============================================================

@app.get("/analizar")
async def analizar_mercado():
    try:
        # === 1️⃣ PRECIO ACTUAL ===
        precio_data = obtener_precio()
        precio_actual = precio_data.get("precio")
        fuente = precio_data.get("fuente")

        # === 2️⃣ SESIÓN NY ===
        sesion_activa = sesion_ny_activa()
        sesion_estado = "✅ Activa (Sesión New York)" if sesion_activa else "❌ Cerrada (Fuera de NY)"

        # === 3️⃣ ESTRUCTURA MULTINIVEL (H4 / H1 / M15) ===
        velas_h4 = obtener_klines_binance(intervalo="4h", limite=200)
        velas_h1 = obtener_klines_binance(intervalo="1h", limite=200)
        velas_m15 = obtener_klines_binance(intervalo="15m", limite=200)

        estructura = {
            "H4 (macro)": evaluar_estructura(velas_h4, "H4"),
            "H1 (intradía)": evaluar_estructura(velas_h1, "H1"),
            "M15 (reacción)": evaluar_estructura(velas_m15, "M15"),
        }

        # === 4️⃣ ZONAS DE REACCIÓN (PDH / PDL) ===
        zonas = _pdh_pdl()
        zona_h4 = _rango_precio(velas_h4)
        zona_h1 = _rango_precio(velas_h1)
        zona_m15 = _rango_precio(velas_m15)

        # === 5️⃣ ESCENARIO OPERATIVO ===
        escenario = definir_escenarios(estructura, sesion_activa)

        # === 6️⃣ RESPUESTA FINAL ===
        return {
            "🧠 TESLABTC.KG": {
                "fecha": datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S"),
                "sesion": sesion_estado,
                "precio_actual": f"{precio_actual:,.2f} USD" if precio_actual else "⚪ No disponible",
                "fuente_precio": fuente,
                "estructura_detectada": estructura,
                "contexto_estructural": _contexto(estructura),
                "zonas": {
                    "ZONA H4 (macro)": zona_h4,
                    "ZONA H1 (intradía)": zona_h1,
                    "ZONA M15 (reacción)": zona_m15,
                    "PDH": zonas.get("PDH"),
                    "PDL": zonas.get("PDL"),
                },
                "escenario": escenario,
                "conexion_binance": BINANCE_STATUS,
                "mensaje": "✨ Análisis completado correctamente",
                "error": "Ninguno"
            }
        }

    except Exception as e:
        return {
            "🧠 TESLABTC.KG": {
                "fecha": datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S"),
                "mensaje": "❌ Error interno del servidor TESLABTC.KG",
                "error": str(e),
            }
        }

# ============================================================
# 📍 FUNCIÓN AUXILIAR — RANGO DE ZONA (High / Low)
# ============================================================

def _rango_precio(velas):
    try:
        highs = [v["high"] for v in velas[-20:]]
        lows = [v["low"] for v in velas[-20:]]
        return {
            "High": round(max(highs), 2),
            "Low": round(min(lows), 2),
        }
    except Exception:
        return {"High": None, "Low": None}

# ============================================================
# 📊 CONTEXTO GENERAL ESTRUCTURAL
# ============================================================

def _contexto(estructura: dict) -> str:
    try:
        h4 = estructura.get("H4 (macro)", "sin_datos")
        h1 = estructura.get("H1 (intradía)", "sin_datos")

        if h4 == "bajista" and h1 == "bajista":
            return "flujo bajista dominante — continuación probable"
        elif h4 == "alcista" and h1 == "alcista":
            return "flujo alcista alineado — tendencia fuerte"
        elif h4 != h1 and h4 != "sin_datos":
            return "desalineación temporal — posible retroceso o rango"
        else:
            return "sin confirmación clara, mercado en transición"
    except:
        return "sin contexto definido"

# ============================================================
# 🟢 MONITOR EN VIVO (alertas periódicas)
# ============================================================

@app.get("/monitor/start")
async def start_monitor():
    asyncio.create_task(live_monitor_loop())
    return {"status": "🟢 Monitor en ejecución cada 5 minutos"}

@app.get("/monitor/stop")
async def stop_monitor_api():
    stop_monitor()
    return {"status": "🔴 Monitor detenido"}

@app.get("/monitor/status")
async def monitor_status():
    return get_alerts()

# ============================================================
# 📡 ESTADO GENERAL DE LA API
# ============================================================

@app.get("/")
async def estado_general():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "API TESLABTC.KG conectada correctamente. Fuente: Binance público. Monitor en background activo.",
        "version": "3.5.0",
        "autor": "GoldTraderBTC",
    }

