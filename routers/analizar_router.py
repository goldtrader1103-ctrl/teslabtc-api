# ============================================================
# 🧠 analizar_router.py — TESLABTC Análisis estructurado
# ============================================================

from fastapi import APIRouter, Request
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio
from utils.analisis_free import generar_analisis_free
from utils.analisis_premium import generar_analisis_premium
from utils.userdb import validar_token_api

router = APIRouter(prefix="/analizar", tags=["TESLABTC"])
TZ_COL = timezone(timedelta(hours=-5))

@router.get("/", summary="Analiza el mercado BTCUSDT y retorna el resultado TESLABTC.KG")
async def analizar(request: Request):
    """
    Endpoint principal del análisis TESLABTC.
    Determina si el usuario es Free o Premium según su token.
    Devuelve JSON válido siempre.
    """
    ahora = datetime.now(TZ_COL)

    # 1️⃣ Validar token
    token = request.headers.get("Authorization") or request.query_params.get("token")
    verif = validar_token_api(token)
    nivel_usuario = verif.get("nivel", "Free")
    token_valido = verif.get("valido", False)

    # 2️⃣ Obtener precio actual
    p = obtener_precio("BTCUSDT")
    precio, fuente = p.get("precio"), p.get("fuente")
    precio_float = float(precio) if isinstance(precio, (int, float)) else 0.0

    # 3️⃣ Generar análisis según nivel
    analisis = (
        generar_analisis_premium(precio_float)
        if token_valido
        else generar_analisis_free(precio_float)
    )

    # 4️⃣ Datos de sesión
    hora_local = ahora.hour + (ahora.minute / 60)
    analisis["sesion"] = (
        "✅ Activa (Sesión NY)" if 7 <= hora_local < 13.5 else "❌ Cerrada (Fuera de NY)"
    )
    analisis["fuente_precio"] = fuente
    analisis["nivel_usuario"] = nivel_usuario

    # 5️⃣ Cuerpo final (JSON válido)
    body = {
        "🧠 TESLABTC.KG": analisis,
        "conexion_binance": (
            "🦎 Fallback CoinGecko activo" if fuente != "Binance (REST)" else "✅ Conectado a Binance"
        ),
    }

    return body
