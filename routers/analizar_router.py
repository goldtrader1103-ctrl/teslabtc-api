# ============================================================
# 🧠 analizar_router.py — Enrutador principal TESLABTC
# ============================================================

from fastapi import APIRouter, Request
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio
from utils.analisis_free import generar_analisis_free
from utils.analisis_premium import generar_analisis_premium
from utils.token_utils import validar_token

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))


@router.get("/", tags=["TESLABTC"])
async def analizar(request: Request):
    """
    Endpoint principal del análisis TESLABTC.
    Determina si el usuario es Free o Premium según su token.
    """
    ahora = datetime.now(TZ_COL)

    # Verificar token en encabezado
    token = request.headers.get("Authorization")
    nivel_usuario = "Free"
    token_valido = False
print("🔍 TOKEN RECIBIDO:", request.headers.get("Authorization"))

    if token:
        verif = validar_token(token)
        if verif.get("valido"):
            nivel_usuario = verif.get("nivel", "Free")
            token_valido = True

    # Obtener precio actual
    p = obtener_precio("BTCUSDT")
    precio, fuente = p.get("precio"), p.get("fuente")
    precio_float = precio if isinstance(precio, (int, float)) else 0.0

    # Generar análisis según nivel
    if nivel_usuario.lower() == "premium":
        analisis = generar_analisis_premium(precio_float)
    else:
        analisis = generar_analisis_free(precio_float)

    # Añadir información de sesión
    hora_local = ahora.hour + (ahora.minute / 60)
    analisis["sesion"] = "✅ Activa (Sesión NY)" if 7 <= hora_local < 13.5 else "❌ Cerrada (Fuera de NY)"
    analisis["fuente_precio"] = fuente

    # Cuerpo final
    body = {
        "🧠 TESLABTC.KG": analisis,
        "conexion_binance": "🦎 Fallback CoinGecko activo" if fuente != "Binance (REST)" else "✅ Conectado a Binance"
    }

    return body
