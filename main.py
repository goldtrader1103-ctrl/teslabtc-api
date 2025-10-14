# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
import sys, os

# --- RUTAS Y MÓDULOS ---
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

# Intento de importación segura (evita crash si falla en Render)
try:
    from utils.price_utils import (
        obtener_precio,
        sesion_ny_activa,
        obtener_klines_binance,
        detectar_estructura,
        _pdh_pdl
    )
except ImportError as e:
    print(f"[TESLABTC.KG] ⚠️ Error al importar utils: {e}")

    # fallback básico
    def obtener_precio(simbolo="BTCUSDT"):
        return {"precio": None, "fuente": "Sin conexión"}
    def sesion_ny_activa(): return False
    def detectar_estructura(velas): return {"estado": "sin_datos"}
    def _pdh_pdl(simbolo="BTCUSDT"): return {"PDH": None, "PDL": None}
    def obtener_klines_binance(*args, **kwargs): return None

# ============================================================
# ⚙️ CONFIGURACIÓN APP FASTAPI
# ============================================================

app = FastAPI(
    title="TESLABTC.KG API",
    description="Sistema operativo de análisis BTCUSDT basado en estructura (H4–M15), liquidez y Price Action puro.",
    version="3.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧩 ENDPOINT PRINCIPAL: /analizar
# ============================================================

@app.get("/analizar", tags=["TESLABTC"])
def analizar_mercado():
    """Devuelve análisis operativo completo de TESLABTC.KG"""
    ahora = datetime.now(TZ_COL)

    # --- Precio actual ---
    precio_info = obtener_precio("BTCUSDT")
    precio_btc = precio_info.get("precio")
    fuente_precio = precio_info.get("fuente")

    # --- Velas por temporalidad ---
    velas_H4 = obtener_klines_binance("BTCUSDT", "4h", 200)
    velas_H1 = obtener_klines_binance("BTCUSDT", "1h", 200)
    velas_M15 = obtener_klines_binance("BTCUSDT", "15m", 200)

    # --- Estructuras detectadas ---
    estructura_H4 = detectar_estructura(velas_H4)
    estructura_H1 = detectar_estructura(velas_H1)
    estructura_M15 = detectar_estructura(velas_M15)

    # --- Zonas de reacción ---
    pdh_pdl = _pdh_pdl("BTCUSDT")

    # --- Determinar escenario operativo ---
    macro = estructura_H4.get("estado", "sin_datos")
    intra = estructura_H1.get("estado", "sin_datos")
    micro = estructura_M15.get("estado", "sin_datos")

    if macro == intra and macro != "sin_datos":
        escenario = {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razon": f"H4 y H1 alineados en estructura {macro.upper()}.",
            "accion": f"Operar {macro.upper()} A+ con confirmación BOS M5 dentro del POI M15.\n"
                      "Objetivo: 1:3 o más, priorizando estructuras limpias.\n"
                      "💡 La gestión del riesgo es la clave de un trader profesional.",
            "tipo": "principal"
        }
    elif macro != intra and intra != "sin_datos":
        escenario = {
            "escenario": "CONSERVADOR 2 (Reentrada)",
            "nivel": "Mitigación secundaria o continuación",
            "razon": f"H4 ({macro}) y H1 ({intra}) no alineados completamente.",
            "accion": "Esperar confirmación M15 o microestructura en favor de H1 antes de ejecutar.\n"
                      "Si el precio deja ineficiencia, considerar reentrada al siguiente POI.",
            "tipo": "reentrada"
        }
    else:
        escenario = {
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Agresivo / bajo confirmación rápida",
            "razon": "Estructura H1 aún sin BOS o mitigando zona opuesta.",
            "accion": "Buscar oportunidad rápida en retroceso M15 con confirmación BOS M5–M3.\n"
                      "RRR máximo 1:1 o 1:2.\n"
                      "💡 Recomendado solo para traders avanzados con control de riesgo.",
            "tipo": "scalping"
        }

    # --- Estado sesión NY ---
    sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    return {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "precio_actual": f"{precio_btc:,.2f} USD" if precio_btc else "⚙️ No disponible",
            "fuente_precio": fuente_precio,
            "estructura_detectada": {
                "H4 (macro)": macro,
                "H1 (intradía)": intra,
                "M15 (reacción)": micro
            },
            "zonas": {
                "PDH (alto 24h)": pdh_pdl.get("PDH"),
                "PDL (bajo 24h)": pdh_pdl.get("PDL")
            },
            "escenario": escenario,
            "mensaje": "✨ Análisis completado correctamente",
            "error": "Ninguno"
        }
    }

# ============================================================
# 🧭 ENDPOINT ESTADO GENERAL
# ============================================================

@app.get("/", tags=["Estado"])
def estado_general():
    ahora = datetime.now(TZ_COL)
    return {
        "status": "✅ TESLABTC.KG operativo",
        "version": "3.0.1",
        "hora": ahora.strftime("%d/%m/%Y %H:%M:%S"),
        "mensaje": "Servidor activo y funcional en Render."
    }

# ============================================================
# 🕐 ENDPOINT SESIÓN NY
# ============================================================

@app.get("/ny-session", tags=["TESLABTC"])
def estado_sesion_ny():
    return {"NY_session_activa": sesion_ny_activa()}
