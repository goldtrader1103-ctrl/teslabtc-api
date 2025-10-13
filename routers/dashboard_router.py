# ============================================================
# 📊 TESLABTC.KG — DASHBOARD PRINCIPAL
# ============================================================

from fastapi import APIRouter
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    _pdh_pdl,
    TZ_COL,
)
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Dashboard TESLABTC"])  # ← ruta raíz
def dashboard_teslabtc():
    """Panel analítico general TESLABTC.KG"""
    ahora = datetime.now(TZ_COL)
    fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

    precio = obtener_precio("BTCUSDT")
    pd = _pdh_pdl("BTCUSDT")

    return {
        "dashboard": {
            "fecha": fecha,
            "precio": precio,
            "PDH": pd.get("PDH"),
            "PDL": pd.get("PDL"),
        }
    }
