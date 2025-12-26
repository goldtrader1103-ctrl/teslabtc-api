# ============================================================
# 🚀 TESLABTC.KG — main.py (v5.3.1 PRO REAL MARKET)
# ============================================================
# Integración total con utils/analisis_premium v5.3.1
# Compatible con intelligent_formatter v5.8 PRO FINAL
# ============================================================

VERSION_TESLA = "v5.3.1 PRO REAL MARKET"

print(f"🧠 TESLABTC.KG — {VERSION_TESLA}")

import asyncio
import random
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware

# ============================================================
# 🧩 Imports Core
# ============================================================
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    sesion_ny_activa,
    BINANCE_STATUS,
)
from utils.estructura_utils import evaluar_estructura
from utils.live_monitor import live_monitor_loop, stop_monitor, get_alerts
from utils.token_utils import (
    generar_token,
    validar_token,
    liberar_token,
    listar_tokens,
)

# Nuevo analizador premium (v5.3.1)
from utils.analisis_premium import generar_analisis_premium

# Formatter unificado
from utils.intelligent_formatter import (
    construir_mensaje_operativo,
    construir_mensaje_free,
    construir_contexto_detallado,
)


# ============================================================
# ⚙️ CONFIGURACIÓN FASTAPI
# ============================================================
app = FastAPI(title="TESLABTC.KG", description="API TESLABTC.KG", version="5.3.1")
app.add_middleware(GZipMiddleware, minimum_size=600)
TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# ✨ FRASES MOTIVACIONALES (REFLEXIONES)
# ============================================================
REFLEXIONES = [
    "La gestión del riesgo es la columna vertebral del éxito en trading.",
    "La paciencia en la zona convierte el caos en oportunidad.",
    "El mercado premia la confirmación, no la anticipación.",
    "Tu disciplina define tu rentabilidad.",
    "Ser constante supera al talento. Siempre.",
    "El trader exitoso no predice, se adapta.",
]

# ============================================================
# 🧠 ENDPOINT PRINCIPAL — /analyze
# ============================================================
@app.get("/analyze", tags=["TESLABTC Premium"])
async def analizar(simbolo: str = "BTCUSDT", token: str | None = Query(None)):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 🔐 Validar token
    auth = validar_token(token) if token else None
    nivel_usuario = (
        auth.get("nivel", "Free") if auth and auth.get("estado") == "✅" else "Free"
    )

    # 💰 Obtener precio
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio", 0)
    fuente = precio_data.get("fuente", "Desconocida")
    precio_str = f"{precio:,.2f} USD" if precio else "⚙️ No disponible"
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # ============================================================
    # 🧩 FREE VERSION — estructura resumida
    # ============================================================
    if nivel_usuario.lower() == "free":
        try:
            h4 = obtener_klines_binance(simbolo, "4h", 120)
            h1 = obtener_klines_binance(simbolo, "1h", 120)
            m15 = obtener_klines_binance(simbolo, "15m", 120)

            estructura = {
                "H4 (macro)": evaluar_estructura(h4),
                "H1 (intradía)": evaluar_estructura(h1),
                "M15 (reacción)": evaluar_estructura(m15),
            }

            body_free = {
                "fecha": fecha,
                "nivel_usuario": "Free",
                "sesión": sesion,
                "activo": simbolo,
                "precio_actual": precio_str,
                "fuente_precio": fuente,
                "estructura_detectada": estructura,
                "conexion_binance": BINANCE_STATUS,
            }

            body_free["mensaje_formateado"] = construir_mensaje_free(body_free)
            return {"🧠 TESLABTC.KG": body_free}

        except Exception as e:
            return {"error": f"❌ Error Free: {e}"}

    # ============================================================
    # 🧩 PREMIUM VERSION — análisis completo
    # ============================================================
    try:
        analisis_premium = generar_analisis_premium(simbolo)
        data = analisis_premium.get("🧠 TESLABTC.KG", analisis_premium)

        # Si no devuelve nada útil
        if not data or "estructura_detectada" not in data:
            raise ValueError("Análisis vacío o incompleto.")

        # 🧠 Mensaje formateado (según versión Premium)
        if not data.get("mensaje_formateado"):
            data["mensaje_formateado"] = construir_mensaje_operativo(data)

        return {"🧠 TESLABTC.KG": data}

    except Exception as e:
        # 🔧 fallback si falla la estructura premium
        fallback_body = {
            "fecha": fecha,
            "nivel_usuario": "Premium",
            "sesión": sesion,
            "activo": simbolo,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "mensaje": f"⚙️ No se pudo generar análisis premium: {e}",
            "estructura_detectada": {},
            "estado_operativo": "🕐 PRE-BOS (esperando confirmación M5)",
            "comentario": "Esperar ruptura estructural M5 para validar entrada.",
        }

        fallback_body["mensaje_formateado"] = construir_mensaje_operativo(fallback_body)
        return {"🧠 TESLABTC.KG": fallback_body}
# ============================================================
# 🧠 ENDPOINT CONTEXTO — /contexto
# ============================================================

@app.get("/contexto", tags=["TESLABTC Premium"])
async def obtener_contexto(
    simbolo: str = "BTCUSDT",
    tipo: str = Query(
        "scalping_continuacion",
        description="scalping_continuacion | scalping_correccion | swing",
    ),
    token: str | None = Query(None),
):
    """
    Devuelve sólo el texto de contexto para el escenario elegido.
    Pensado para el botón del bot de Telegram.
    """
    # 🔐 Validar token (igual que en /analyze)
    auth = validar_token(token) if token else None
    if not auth or auth.get("estado") != "✅":
        return {
            "estado": "⛔",
            "mensaje": "Token inválido o sin acceso Premium para ver el contexto.",
        }

    # Reutilizamos el mismo análisis premium
    analisis_premium = generar_analisis_premium(simbolo)
    data = analisis_premium.get("🧠 TESLABTC.KG", analisis_premium)

    # Aseguramos que tenga estructura básica
    if not data or "estructura_detectada" not in data:
        return {
            "estado": "⚙️",
            "mensaje": "No se pudo generar el análisis estructural para este símbolo.",
        }

    contexto = construir_contexto_detallado(data, tipo)

    return {
        "estado": "✅",
        "simbolo": simbolo,
        "tipo_escenario": tipo,
        "contexto": contexto,
    }

# ============================================================
# 🧩 OTROS ENDPOINTS (tokens, health, monitor)
# ============================================================

@app.post("/validate", tags=["Bot"])
async def validate_token_route(request: Request):
    data = await request.json()
    token = data.get("token")
    if not token:
        return {"estado": "❌", "mensaje": "Falta token"}
    return validar_token(token)


@app.post("/admin/create_token", tags=["Admin"])
async def admin_create_token(data: dict):
    token_admin = data.get("token_admin")
    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}

    nivel = data.get("nivel", "Premium")
    usuario = str(data.get("telegram_id", "usuario_desconocido"))
    res = generar_token(usuario, dias_premium=30, dias_free=10)
    return res


@app.post("/admin/liberar_token", tags=["Admin"])
async def admin_liberar_token(data: dict):
    token_admin = data.get("token_admin")
    token = data.get("token")
    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}
    return liberar_token(token)


@app.get("/health", tags=["Estado"])
async def health_check():
    return {
        "status": "✅ OK",
        "servicio": "TESLABTC.KG",
        "conexion_binance": BINANCE_STATUS,
        "timestamp": datetime.now(TZ_COL).strftime("%Y-%m-%d %H:%M:%S"),
    }


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


@app.get("/", tags=["Home"])
async def home():
    return {"status": "✅ Servicio operativo", "version": VERSION_TESLA}


# ============================================================
# 🔁 ALIAS COMPATIBILIDAD (para BOT antiguo)
# ============================================================
@app.get("/analisis/premium", tags=["Compatibilidad"])
async def analisis_premium_alias():
    try:
        analisis = generar_analisis_premium("BTCUSDT")
        return {"🧠 TESLABTC.KG": analisis}
    except Exception as e:
        return {"error": f"❌ Error en alias /analisis/premium: {e}"}


# ============================================================
# 🚀 ENTRYPOINT LOCAL
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
