# ============================================================
# 🚀 TESLABTC.KG — API PRINCIPAL (versión 3.1 estable)
# ============================================================

from fastapi import FastAPI
from datetime import datetime, timezone, timedelta

from utils.price_utils import (
    obtener_precio,
    sesion_ny_activa,
    _pdh_pdl
)
from utils.estructura_utils import (
    evaluar_estructura,
    definir_escenario
)

# ============================================================
# 🌎 Configuración base
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))
app = FastAPI(
    title="TESLABTC.KG API",
    description="Análisis operativo del mercado BTCUSDT basado en Price Action puro, estructura, liquidez y escenarios TESLABTC.KG",
    version="3.1.0"
)

# ============================================================
# 📊 ENDPOINT PRINCIPAL /analizar
# ============================================================

@app.get("/analizar", tags=["TESLABTC.KG"])
def analizar():
    """Análisis operativo en tiempo real del mercado BTCUSDT."""
    try:
        # 1️⃣ Obtener precio actual
        precio_info = obtener_precio("BTCUSDT")
        precio = precio_info["precio"]
        fuente = precio_info["fuente"]

        # 2️⃣ Evaluar estructura (H4, H1, M15)
        estructura_info = evaluar_estructura("BTCUSDT")
        estructura = estructura_info["estructura"]
        zonas = estructura_info["zonas"]

        # 3️⃣ Definir escenario operativo
        escenario = definir_escenario(estructura)

        # 4️⃣ Obtener PDH/PDL (últimas 24h)
        pdh_pdl = _pdh_pdl("BTCUSDT")

        # 5️⃣ Estado de sesión NY
        sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de sesión NY)"

        # 6️⃣ Construir respuesta final
        ahora = datetime.now(TZ_COL)

        return {
            "🧠 TESLABTC.KG": {
                "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
                "sesion": sesion,
                "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
                "fuente_precio": fuente,
                "estructura_detectada": estructura,
                "zonas": {
                    "PDH (alto 24h)": pdh_pdl.get("PDH"),
                    "PDL (bajo 24h)": pdh_pdl.get("PDL"),
                    **zonas
                },
                "escenario": escenario,
                "mensaje": "✨ Análisis completado correctamente",
                "error": "Ninguno"
            }
        }

    except Exception as e:
        print(f"[analizar] Error: {e}")
        return {
            "🧠 TESLABTC.KG": {
                "fecha": datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S"),
                "sesion": "⚠️ No verificada",
                "precio_actual": "⚙️ No disponible",
                "fuente_precio": "N/A",
                "estructura_detectada": "sin_datos",
                "zonas": {},
                "escenario": {"escenario": "sin_datos", "razón": str(e)},
                "mensaje": "⚠️ Error al obtener datos en vivo",
                "error": str(e)
            }
        }

# ============================================================
# 🏠 ENDPOINT BASE /
# ============================================================

@app.get("/", tags=["Estado"])
def estado_general():
    """Verifica que el sistema TESLABTC.KG esté en línea."""
    return {
        "status": "✅ Activo",
        "api": "TESLABTC.KG v3.1.0",
        "mensaje": "Sistema operativo — listo para análisis BTCUSDT",
        "autora": "Katherinne Galvis"
    }

# ============================================================
# 🕓 ENDPOINT SESIÓN NY
# ============================================================

@app.get("/ny-session", tags=["Sesión"])
def ny_session_status():
    """Verifica si la sesión de Nueva York está activa."""
    estado = sesion_ny_activa()
    ahora = datetime.now(TZ_COL)
    return {
        "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
        "sesion_ny": "✅ Activa" if estado else "❌ Cerrada",
        "horario": "07:00–13:30 COL (Lun–Vie)",
        "mensaje": "Dentro del horario operativo" if estado else "Fuera del horario operativo"
        }
