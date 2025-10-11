from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import (
    TZ_COL, obtener_precio, obtener_klines_binance, detectar_estructura, sesion_ny_activa
)

router = APIRouter()

@router.get("/confirmaciones", tags=["TESLABTC"])
def confirmaciones_teslabtc():
    """Validaciones PA pura TESLABTC A.P."""
    ahora_col = datetime.now(TZ_COL)
    precio = obtener_precio()

    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)

    estr_h1 = detectar_estructura(velas_h1)
    estr_m15 = detectar_estructura(velas_m15)
    en_ny = sesion_ny_activa(ahora_col)

    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "precio": precio,
        "confirmaciones": {
            "BOS H1": estr_h1["BOS"],
            "Tipo BOS H1": estr_h1["tipo_BOS"],
            "Tendencia H1": estr_h1["tendencia"],
            "BOS M15": estr_m15["BOS"],
            "Tipo BOS M15": estr_m15["tipo_BOS"],
            "Tendencia M15": estr_m15["tendencia"],
            "Sesión NY": "Activa ✅" if en_ny else "Fuera ❌"
        }
    }
