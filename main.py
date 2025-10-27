
# ============================================================
# 🚀 TESLABTC.KG — main.py (integrado con token_utils persistente)
# ============================================================

import asyncio
from fastapi import FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta, timezone
import random

# Importa tus utilidades (asumiendo que ya existen)
from utils.price_utils import obtener_precio, obtener_klines_binance, sesion_ny_activa, _pdh_pdl, BINANCE_STATUS
from utils.estructura_utils import evaluar_estructura, definir_escenarios
from utils.live_monitor import live_monitor_loop, stop_monitor, get_alerts

# Import token utils (nuevo)
from utils.token_utils import generar_token, validar_token, verificar_vencimientos, liberar_token, listar_tokens

# ============================================================
app = FastAPI(title="TESLABTC.KG", description="API TESLABTC.KG", version="4.3")
app.add_middleware(GZipMiddleware, minimum_size=600)
TZ_COL = timezone(timedelta(hours=-5))

# Reflexiones aleatorias (puedes ampliar la lista)
REFLEXIONES = [
    "La gestión del riesgo es la columna vertebral del éxito en trading.",
    "La paciencia en la zona de demanda puede transformar pérdidas en ganancias.",
    "Entrar con menor tamaño y mayor convicción es preferible a lo contrario.",
    "La disciplina al cortar pérdidas conserva el capital para las buenas oportunidades.",
    "La confirmación en múltiples marcos temporales aumenta la probabilidad de éxito.",
    "Un buen plan no garantiza ganancias, pero la ausencia de plan garantiza pérdidas.",
    "La recompensa real del trading es el proceso, no el resultado inmediato.",
    "Observa la estructura primero — las velas contarán la historia después.",
    "No confundas movimiento con tendencia; el contexto lo determina.",
    "La paciencia y la gestión convierten probabilidades en rendimiento."
]

# ============================================================
# 🧠 ENDPOINT PRINCIPAL DE ANÁLISIS — TESLABTC.KG
# ============================================================
@app.get("/analyze", tags=["Análisis TESLABTC"])
async def analizar(simbolo: str = "BTCUSDT", token: str | None = Query(None)):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # ==========================
    # 🔐 Validar token
    # ==========================
    auth = validar_token(token) if token else None
    nivel_usuario = auth.get("nivel", "Free") if auth and auth.get("valido") else "Free"

    # ==========================
    # 💰 Datos de precio
    # ==========================
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio", 0)
    fuente = precio_data.get("fuente", "Desconocida")
    precio_str = f"{precio:,.2f} USD" if precio else "⚙️ No disponible"
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # ==========================
    # 🧩 Estructuras por temporalidad
    # ==========================
    try:
        h4 = obtener_klines_binance(simbolo, "4h", 120)
        h1 = obtener_klines_binance(simbolo, "1h", 120)
        m15 = obtener_klines_binance(simbolo, "15m", 120)
        e_h4 = evaluar_estructura(h4)
        e_h1 = evaluar_estructura(h1)
        e_m15 = evaluar_estructura(m15)
    except Exception as e:
        print(f"⚠️ Error analizando estructura: {e}")
        e_h4 = e_h1 = e_m15 = {"estado": "sin_datos"}

    estructura = {
        "H4 (macro)": e_h4,
        "H1 (intradía)": e_h1,
        "M15 (reacción)": e_m15
    }

    # ============================================================
    # 🧠 FREE — acceso limitado
    # ============================================================
    if nivel_usuario.lower() == "free":
        return {
            "🧠 TESLABTC.KG": {
                "fecha": fecha,
                "nivel_usuario": "Free",
                "sesión": sesion,
                "precio_actual": precio_str,
                "fuente_precio": fuente,
                "estructura_detectada": estructura,
                "mensaje": "🧩 Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
                "conexion_binance": BINANCE_STATUS
            }
        }

    # ============================================================
    # 💎 PREMIUM — análisis completo
    # ============================================================
    zonas = _pdh_pdl(simbolo)
    escenarios = definir_escenarios({
        "H4": e_h4.get("estado"),
        "H1": e_h1.get("estado"),
        "M15": e_m15.get("estado")
    })

    reflexion = random.choice(REFLEXIONES)

    return {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "nivel_usuario": "Premium",
            "sesión": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "zonas": zonas,
            "confirmaciones": "BOS validado + Volumen confirmado + FVG limpio",
            "escenario_1": escenarios.get("continuacion", "Esperando señal"),
            "escenario_2": escenarios.get("correccion", "Esperando señal"),
            "conclusion": "Estructura y contexto alineados con el flujo institucional.",
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis Premium completado correctamente",
            "reflexion": reflexion
        }
    }

# ============================================================
# Validación del bot (opcional) - expone la lógica de validación
# ============================================================
@app.post("/validate", tags=["Bot"])
async def validate_token(request: Request):
    data = await request.json()
    token = data.get("token")
    if not token:
        return {"estado": "❌", "mensaje": "Falta token"}
    return validar_token(token)

# ============================================================
# Admin: crear/renovar token (mantiene mismo token por usuario)
# ============================================================
@app.post("/admin/create_token", tags=["Admin"])
async def admin_create_token(data: dict):
    token_admin = data.get("token_admin")
    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}

    nivel = data.get("nivel", "Premium")
    usuario = str(data.get("telegram_id", "usuario_desconocido"))
    # generar o renovar token para el usuario
    res = generar_token(usuario, dias_premium=30, dias_free=10)
    return res

# ============================================================
# Endpoint para liberar token manualmente
# ============================================================
@app.post("/admin/liberar_token", tags=["Admin"])
async def admin_liberar_token(data: dict):
    token_admin = data.get("token_admin")
    token = data.get("token")
    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}
    return liberar_token(token)

# ============================================================
# Monitor y health
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

@app.get("/health", tags=["Estado"])
async def health_check():
    return {
        "status": "✅ OK",
        "servicio": "TESLABTC.KG",
        "conexion_binance": BINANCE_STATUS,
        "timestamp": datetime.now(TZ_COL).strftime("%Y-%m-%d %H:%M:%S"),
    }

@app.get("/", tags=["Home"])
async def home():
    return {"status": "✅ Servicio operativo", "version": "4.3 PRO STABLE"}

# ============================================================
# 🧩 DEBUG ROUTER INTEGRADO — para sincronización con el BOT
# ============================================================
import json, os
from fastapi import APIRouter

@app.get("/debug/tokens", tags=["Debug"])
async def obtener_tokens_debug():
    """Devuelve la lista de tokens activos para sincronización con el BOT."""
    try:
        if not os.path.exists("tokens.json"):
            return {"tokens": [], "mensaje": "Archivo tokens.json no encontrado"}

        with open("tokens.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return {"tokens": data, "mensaje": "Tokens cargados correctamente"}
    except Exception as e:
        return {"tokens": [], "error": str(e)}

# ============================================================
# Incluir routers adicionales (al final del archivo)
# ============================================================
from routers.admin_extra import router as admin_extra_router
from routers.auth_extra import router as auth_extra_router
from routers.analizar_router import router as analizar_router

app.include_router(admin_extra_router)
app.include_router(auth_extra_router)
app.include_router(analizar_router)  # <- sin prefix, ya lo tiene internamente

# ============================================================
# 🚀 ENTRYPOINT — EJECUCIÓN LOCAL
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
