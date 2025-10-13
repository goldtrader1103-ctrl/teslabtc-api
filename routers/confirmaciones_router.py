from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import (
    TZ_COL, obtener_precio, obtener_klines_binance, detectar_estructura, sesion_ny_activa
)

router = APIRouter()

@router.get("/", tags=["TESLABTC"])  # ← ruta raíz
def confirmaciones_teslabtc():
    """Validaciones PA pura TESLABTC.KG"""
    ahora_col = datetime.now(TZ_COL)
    precio = obtener_precio("BTCUSDT")
    velas_h1 = obtener_klines_binance("BTCUSDT", "1h", 120)
    velas_m15 = obtener_klines_binance("BTCUSDT", "15m", 120)

    estructura = detectar_estructura(velas_h1 or [])
    sesion = "✅ Activa" if sesion_ny_activa() else "❌ Fuera de sesión"

    return {
        "fecha": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "precio": precio,
        "sesion": sesion,
        "estructura": estructura,
        "nota": "Confirmaciones simplificadas"
    }
