
# ============================================================
# 🚀 TESLABTC.KG — main.py (integrado con token_utils persistente)
# ============================================================
# ============================================================
# 🧠 Versión del sistema TESLABTC.KG
# ============================================================
VERSION_TESLA = "v5.2 REAL MARKET (última compilación activa)"

print(f"🧠 TESLABTC.KG — {VERSION_TESLA}")

import asyncio
from fastapi import FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta, timezone
import random

from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    sesion_ny_activa,
    obtener_datos_sesion_colombia,
    BINANCE_STATUS
)

from utils.estructura_utils import evaluar_estructura, definir_escenarios
from utils.live_monitor import live_monitor_loop, stop_monitor, get_alerts
from utils.analisis_premium import generar_analisis_premium
from utils.token_utils import generar_token, validar_token, verificar_vencimientos, liberar_token, listar_tokens
from utils.intelligent_formatter import (
    construir_mensaje_operativo,
    construir_mensaje_free,
    limpiar_texto
)

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
# 🧠 ENDPOINT PRINCIPAL DE ANÁLISIS — TESLABTC.KG (formato unificado)
# ============================================================
@app.get("/analyze", tags=["Análisis TESLABTC"])
async def analizar(simbolo: str = "BTCUSDT", token: str | None = Query(None)):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")

    # 🧩 Importar los formateadores
    from utils.intelligent_formatter import (
        construir_mensaje_free,
        construir_mensaje_operativo,
    )

    # 🔐 Validación de token
    auth = validar_token(token) if token else None
    nivel_usuario = auth.get("nivel", "Free") if auth and auth.get("estado") == "✅" else "Free"

    # 💰 Precio y sesión
    precio_data = obtener_precio(simbolo)
    precio = precio_data.get("precio", 0)
    fuente = precio_data.get("fuente", "Desconocida")
    precio_str = f"{precio:,.2f} USD" if precio else "⚙️ No disponible"
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # ==============================================
    # 🧩 Estructura Base (seguridad por si falla)
    # ==============================================
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
    # FREE — versión resumida
    # ============================================================
    if nivel_usuario.lower() == "free":
        body_free = {
            "fecha": fecha,
            "nivel_usuario": "Free",
            "sesión": sesion,
            "precio_actual": precio_str,
            "fuente_precio": fuente,
            "estructura_detectada": estructura,
            "conexion_binance": BINANCE_STATUS,
        }

        body_free["mensaje_formateado"] = construir_mensaje_free(body_free)
        return {"🧠 TESLABTC.KG": body_free}

    # ============================================================
    # PREMIUM — versión completa
    # ============================================================
    else:
        try:
            # ⚙️ Análisis Premium base
            ap_full = generar_analisis_premium(simbolo)
            ap = ap_full.get("🧠 TESLABTC.KG", ap_full)
            
            # 🔍 Detección de estado “PRE-BOS” si no hay setup activo ni BOS confirmado
            setup_data = ap.get("setup_tesla", {})
            estructura_detectada = ap.get("estructura_detectada", {})
            h1_state = estructura_detectada.get("H1", {}).get("estado", "—")
            m15_state = estructura_detectada.get("M15", {}).get("estado", "—")

            # Si no hay setup activo pero estructura válida → mostrar PRE-BOS
            if not setup_data.get("activo", False) and h1_state in ("alcista", "bajista"):
                pre_bos_body = {
                    "fecha": ap.get("fecha", fecha),
                    "nivel_usuario": "Premium",
                    "sesión": ap.get("sesion", sesion),
                    "activo": ap.get("activo", simbolo),
                    "precio_actual": ap.get("precio_actual", precio_str),
                    "fuente_precio": fuente,
                    "estructura_detectada": estructura_detectada,
                    "zonas_detectadas": ap.get("zonas_detectadas", {}),
                    "confirmaciones": ap.get("confirmaciones", {}),
                    "estado_operativo": "🕐 PRE-BOS (esperando confirmación M5)",
                    "escenario_principal": (
                        "continuación" if h1_state == "bajista" else "corrección"
                    ),
                    "comentario": "Estructura clara pero sin ruptura M5 confirmada. Esperar gatillo BOS.",
                    "conexion_binance": BINANCE_STATUS,
                }

                # Añadir mensaje visual coherente
                from utils.intelligent_formatter import construir_mensaje_operativo
                pre_bos_body["mensaje_formateado"] = construir_mensaje_operativo(pre_bos_body)

                return {"🧠 TESLABTC.KG": pre_bos_body}

            # 🔁 INTEGRAR ESTRUCTURA REAL MULTI-TF
            from utils.analisis_estructura import analizar_estructura_general
            estructura_real = analizar_estructura_general(simbolo)
            ap.update(estructura_real)

            # 🧩 Estructura Premium completa
            premium_body = {
                "fecha": ap.get("fecha", fecha),
                "nivel_usuario": "Premium",
                "sesión": ap.get("sesion", sesion),
                "activo": ap.get("activo", simbolo),
                "precio_actual": ap.get("precio_actual", precio_str),
                "fuente_precio": fuente,
                "estructura_detectada": ap.get("estructura_detectada", {}),
                "zonas_detectadas": ap.get("zonas_detectadas", {}),
                "confirmaciones": ap.get("confirmaciones", {}),
                "probabilidad": ap.get("probabilidad", "—"),
                "setup_tesla": ap.get("setup_tesla", {}),
                "conclusion_general": ap.get("conclusion_general", "—"),
                "contexto_general": ap.get("contexto_general", "—"),
                "conexion_binance": BINANCE_STATUS,
            }

            # 🧠 Integración con el formateador inteligente
            premium_body["mensaje_formateado"] = construir_mensaje_operativo(premium_body)
            return {"🧠 TESLABTC.KG": premium_body}

        except Exception as e:
            print(f"⚠️ Error en análisis Premium TESLABTC: {e}")

            # 🔧 Estructura fallback para evitar respuesta vacía
            default_body = {
                "fecha": fecha,
                "nivel_usuario": "Premium",
                "sesión": sesion,
                "precio_actual": precio_str,
                "fuente_precio": fuente,
                "mensaje": f"⚙️ No se pudo generar análisis completo — {str(e)}",
                "estructura_detectada": estructura,
                "conexion_binance": BINANCE_STATUS,
                "estado_operativo": "🕐 PRE-BOS (esperando confirmación M5)",
                "escenario_principal": "continuación" if e_h1.get("tendencia") == "bajista" else "corrección",
                "comentario": "Mostrar estructura base. Esperar ruptura M5 para validar entrada."
            }

            # 🧩 Añadir mensaje formateado
            from utils.intelligent_formatter import construir_mensaje_operativo
            default_body["mensaje_formateado"] = construir_mensaje_operativo(default_body)

            return {"🧠 TESLABTC.KG": default_body}

# ============================================================
# 🔍 FUNCIÓN AUXILIAR PARA BUSCAR CONCEPTOS
# ============================================================
def obtener_concepto(nombre: str):
    from utils.conceptos_tesla import CONCEPTOS
    for clave, valor in CONCEPTOS.items():
        if clave.lower() == nombre.lower():
            return valor
    return {
        "titulo": "❌ No encontrado",
        "definicion": "El concepto solicitado no está disponible en la base actual.",
        "ejemplo": ""
    }

# ============================================================
# 📘 ENDPOINT EDUCATIVO — CONCEPTOS TESLA
# ============================================================
@app.get("/concepto")
def get_concepto(nombre: str):
    """
    Devuelve la definición de un concepto individual o la lista completa.
    Ejemplo:
      /concepto?nombre=bos
      /concepto?nombre=todos
    """
    try:
        from utils.conceptos_tesla import CONCEPTOS

        # ✅ Si es una lista (como en tu JSON actual)
        if isinstance(CONCEPTOS, list):
            conceptos_lista = CONCEPTOS
        else:
            conceptos_lista = list(CONCEPTOS.values())

        # ✅ Mostrar todos
        if nombre.lower() == "todos":
            return {"TESLABTC.KG - Concepto": conceptos_lista}

        # ✅ Buscar por nombre
        for c in conceptos_lista:
            if c.get("nombre", "").lower() == nombre.lower():
                return {"TESLABTC.KG - Concepto": c}

        # ❌ No encontrado
        return {
            "TESLABTC.KG - Concepto": {
                "titulo": "No encontrado",
                "definicion": "El concepto solicitado no está registrado.",
                "ejemplo": ""
            }
        }

    except Exception as e:
        return {"error": f"❌ Error en /concepto: {str(e)}"}

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
# 🔁 ALIAS DE COMPATIBILIDAD — Endpoint antiguo del BOT
# ============================================================
@app.get("/analisis/premium", tags=["Compatibilidad"])
async def analisis_premium_alias():
    """
    Mantiene compatibilidad con el BOT TESLABTC que llama al endpoint /analisis/premium.
    Internamente redirige al mismo análisis Premium de /analyze.
    """
    try:
        from utils.analisis_premium import generar_analisis_premium

        # ✅ Ejecutar análisis premium normal usando símbolo
        analisis = generar_analisis_premium("BTCUSDT")

        return {"🧠 TESLABTC.KG": analisis}

    except Exception as e:
        return {
            "🧠 TESLABTC.KG": {
                "estado": "❌",
                "mensaje": f"Error en alias /analisis/premium: {str(e)}"
            }
        }

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