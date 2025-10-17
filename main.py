# ============================================================
# 🚀 TESLABTC.KG — API Principal (v4.3 PRO STABLE)
# ============================================================

import asyncio
from fastapi import FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta, timezone

# Utilidades internas
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    sesion_ny_activa,
    _pdh_pdl,
    BINANCE_STATUS,
)
from utils.estructura_utils import evaluar_estructura, definir_escenarios
from utils.live_monitor import live_monitor_loop, stop_monitor, get_alerts
from utils.token_utils import generar_token, validar_token, verificar_vencimientos, liberar_token
from utils.auth_utils import obtener_uso

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

app = FastAPI(
    title="TESLABTC.KG",
    description="💼 TESLABTC.KG — API profesional con monetización por token (FREE / PREMIUM)",
    version="4.3",
)
app.add_middleware(GZipMiddleware, minimum_size=600)
TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 ENDPOINT PRINCIPAL — /analyze
# ============================================================

@app.get("/analyze", tags=["Análisis"])
async def analizar(simbolo: str = "BTCUSDT", token: str | None = Query(None)):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 🔐 Validar token
    auth = validar_token(token)
    if auth["estado"] != "✅":
        return {
            "autenticación": auth,
            "mensaje": "⛔ Acceso denegado o token inválido",
            "fecha": fecha
        }

    nivel_usuario = auth["nivel"]

    # 📊 Obtener precio
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio")
    fuente = precio_data.get("fuente")
    precio_str = f"{precio:,.2f} USD" if precio not in [None, 0] else "⚙️ No disponible"

    # 🕐 Sesión New York
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    try:
        h4 = obtener_klines_binance(simbolo, "4h", 120)
        h1 = obtener_klines_binance(simbolo, "1h", 120)
        m15 = obtener_klines_binance(simbolo, "15m", 120)
        e_h4 = evaluar_estructura(h4)
        e_h1 = evaluar_estructura(h1)
        e_m15 = evaluar_estructura(m15)
    except Exception as e:
        e_h4 = e_h1 = e_m15 = {"estado": "sin_datos"}
        print(f"⚠️ Error estructura: {e}")

    estructura = {
        "H4 (macro)": e_h4,
        "H1 (intradía)": e_h1,
    }

    if nivel_usuario.lower() == "free":
        return {
            "🧠 TESLABTC.KG": {
                "fecha": fecha,
                "nivel_usuario": nivel_usuario,
                "sesión": sesion,
                "precio_actual": precio_str,
                "fuente_precio": fuente,
                "estructura_detectada": estructura,
                "mensaje": "🧩 Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
                "conexion_binance": BINANCE_STATUS
            }
        }

    zonas = _pdh_pdl(simbolo)
    estructura["M15 (reacción)"] = e_m15
    escenario = definir_escenarios({
        "H4": e_h4.get("estado", "sin_datos"),
        "H1": e_h1.get("estado", "sin_datos"),
        "M15": e_m15.get("estado", "sin_datos"),
    })

    return {
        "🧠 TESLABTC.KG": {
            "fecha": fecha,
            "nivel_usuario": nivel_usuario,
            "sesión": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "zonas": zonas,
            "escenario": escenario,
            "conexion_binance": BINANCE_STATUS,
            "mensaje": "✨ Análisis Premium completado correctamente"
        }
    }

# ============================================================
# 🔐 VALIDACIÓN DE TOKENS PARA EL BOT TELEGRAM
# ============================================================

@app.post("/validate", tags=["Bot"])
async def validate_token(request: Request):
    data = await request.json()
    token = data.get("token")
    device_id = data.get("device_id")

    if not token:
        return {"estado": "⛔", "mensaje": "Falta token"}

    return validar_token(token, device_id)

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
# 🛠️ ADMINISTRACIÓN — TOKENS
# ============================================================

@app.post("/admin/create_token", tags=["Admin"])
async def admin_create_token(data: dict):
    token_admin = data.get("token_admin")
    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}

    nivel = data.get("nivel", "Free")
    usuario = data.get("telegram_id", "usuario_desconocido")
    return generar_token(nivel, str(usuario))

@app.post("/admin/renovar_token", tags=["Admin"])
async def renovar_token(data: dict):
    from utils.token_utils import cargar_usuarios, guardar_usuarios
    token_admin = data.get("token_admin")
    telegram_id = str(data.get("telegram_id"))

    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}

    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == telegram_id and u["nivel"].lower() == "premium":
            u["fecha_vencimiento"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            u["activo"] = True
            guardar_usuarios(usuarios)
            return {
                "estado": "✅",
                "mensaje": f"Token renovado para {telegram_id}",
                "vencimiento": u["fecha_vencimiento"]
            }

    return {"estado": "⛔", "mensaje": "Usuario no encontrado o sin token Premium"}

@app.post("/admin/liberar_token", tags=["Admin"])
async def admin_liberar_token(data: dict):
    token_admin = data.get("token_admin")
    token = data.get("token")

    if token_admin != "admin-teslabtc-kg":
        return {"estado": "⛔", "mensaje": "Token administrativo inválido"}

    return liberar_token(token)

# ============================================================
# 🔍 HEALTH CHECK Y HOME
# ============================================================

@app.get("/health", tags=["Estado"])
async def health_check():
    return {
        "status": "✅ OK",
        "servicio": "TESLABTC.KG",
        "conexion_binance": BINANCE_STATUS,
        "timestamp": datetime.now(TZ_COL).strftime("%Y-%m-%d %H:%M:%S"),
    }

@app.get("/", tags=["Estado"])
async def home():
    return {
        "status": "✅ Servicio operativo",
        "descripcion": "TESLABTC.KG conectado a Binance Vision con sistema de monetización por token.",
        "version": "4.3 PRO STABLE",
        "autor": "GoldTraderBTC",
        "framework": "FastAPI + Fly.io",
    }

# ============================================================
# 🚀 ENTRYPOINT LOCAL / DOCKER
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
