# ============================================================
# 📊 TESLABTC A.P. — DASHBOARD PRINCIPAL
# ============================================================

from fastapi import APIRouter
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    _pdh_pdl,  # ✅ ahora sí existe en price_utils.py
    TZ_COL,
)
from datetime import datetime

router = APIRouter()


@router.get("/dashboard", tags=["Dashboard TESLABTC"])
def dashboard_teslabtc():
    """Panel analítico general TESLABTC A.P."""

    ahora = datetime.now(TZ_COL)
    fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

    # --- Precio actual BTCUSDT ---
    precio_actual = obtener_precio("BTCUSDT")

    # --- Obtener Klines (últimas velas) ---
    klines = obtener_klines_binance("BTCUSDT", "15m", 20)
    ult_cierre = klines[-1]["close"] if klines else None

    # --- Calcular PDH / PDL ---
    niveles = _pdh_pdl("BTCUSDT")

    return {
        "sistema": "TESLABTC A.P. Dashboard",
        "timestamp": fecha,
        "precio_actual": precio_actual,
        "ultimo_cierre": ult_cierre,
        "niveles_previos": niveles,
        "ventana_analisis": "15m",
        "sesion": "NY (07:00–13:30 COL)",
        "mensaje": "✅ Datos actualizados correctamente" if precio_actual else "⚠️ Error al obtener datos",
    }
