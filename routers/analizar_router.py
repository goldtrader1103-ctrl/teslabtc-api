# ============================================================
# 🧠 routers/analizar_router.py — TESLABTC Análisis
# ============================================================
from __future__ import annotations
from fastapi import APIRouter, Request
from datetime import datetime, timezone, timedelta
from utils.analisis_premium import generar_analisis_premium
from utils.intelligent_formatter import construir_mensaje_free

router = APIRouter(prefix="/analizar", tags=["TESLABTC"])
TZ_COL = timezone(timedelta(hours=-5))

def _analisis_free_stub() -> dict:
    now = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "fecha": now,
        "sesión": "❌ Cerrada (Fuera de NY)",
        "precio_actual": "—",
        "conexion_binance": "—",
    }
    data["mensaje_formateado"] = construir_mensaje_free(data)
    return data

@router.get("/", summary="Análisis TESLABTC (Free/Premium)")
async def analizar(request: Request):
    token = request.headers.get("Authorization") or request.query_params.get("token")
    # Si tienes userdb/validación real, úsala; aquí asumo Premium si token llega.
    is_premium = bool(token)

    if is_premium:
        payload = generar_analisis_premium("BTCUSDT")
        return {"🧠 TESLABTC.KG": payload}
    else:
        free = _analisis_free_stub()
        return {"🧠 TESLABTC.KG": free}
