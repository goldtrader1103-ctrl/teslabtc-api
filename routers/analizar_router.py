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

    # ==============================
    # 1) Validar token
    # ==============================
    token = request.headers.get("Authorization")

    if not token:
        token = request.query_params.get("token")

    nivel_usuario = "Free"
    token_valido = False

    if token:
        verif = validar_token(token)
        if verif.get("valido"):
            nivel_usuario = verif.get("nivel", "Free")
            token_valido = True

    # ==============================
    # 2) Obtener precio actual
    # ==============================
    p = obtener_precio("BTCUSDT")
    precio, fuente = p.get("precio"), p.get("fuente")
    precio_float = precio if isinstance(precio, (int, float)) else 0.0

    # ==============================
    # 3) Decidir análisis
    # ==============================
    if token_valido:
        analisis = generar_analisis_premium(precio_float)
    else:
        analisis = generar_analisis_free(precio_float)

    # ==============================
    # 4) Datos de sesión
    # ==============================
    hora_local = ahora.hour + (ahora.minute / 60)
    analisis["sesion"] = "✅ Activa (Sesión NY)" if 7 <= hora_local < 13.5 else "❌ Cerrada (Fuera de NY)"
    analisis["fuente_precio"] = fuente
    analisis["nivel_usuario"] = nivel_usuario

    # ==============================
    # 5) Cuerpo final
    # ==============================
    body = {
        "🧠 TESLABTC.KG": analisis,
        "conexion_binance": "🦎 Fallback CoinGecko activo" if fuente != "Binance (REST)" else "✅ Conectado a Binance"
    }

    return body
