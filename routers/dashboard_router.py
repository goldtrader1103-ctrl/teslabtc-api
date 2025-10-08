from fastapi import APIRouter
from utils.price_utils import (
    obtener_precio, obtener_klines_binance, detectar_bos,
    detectar_fvg_m15, detectar_ob_h1_h4, high_low_anterior_dia, sesion_ny_activa, ahora_col
)

router = APIRouter()

@router.get("/estado_general")
def estado_general():
    precio = obtener_precio()
    h1 = obtener_klines_binance(interval="1h", limit=60)
    h4 = obtener_klines_binance(interval="4h", limit=60)

    bos_h1_up  = detectar_bos(h1, bullish=True)
    bos_h1_dn  = detectar_bos(h1, bullish=False)
    direccion  = "Alcista 📈" if bos_h1_up and not bos_h1_dn else "Bajista 📉" if bos_h1_dn and not bos_h1_up else "Rango ⏸️"

    pdh, pdl = high_low_anterior_dia()
    fvg = detectar_fvg_m15()
    obz = detectar_ob_h1_h4()
    sesion = "✅ Activa (07:00–13:30 COL)" if sesion_ny_activa() else "❌ Fuera de sesión NY"

    # Escenario PA puro
    if direccion.startswith("Alcista"):
        escenario = "Esperar retroceso a POI (OB/FVG) para BUY en M15 (BOS obligatorio)"
    elif direccion.startswith("Bajista"):
        escenario = "Esperar retroceso a POI (OB/FVG) para SELL en M15 (BOS obligatorio)"
    else:
        escenario = "Esperar BOS en H1 que defina el flujo; operar solo con confirmación M15"

    return {
        "timestamp": ahora_col().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio,
        "direccion_macro": direccion,
        "sesion_NY": sesion,
        "pdh_pdl": {"PDH": pdh, "PDL": pdl},
        "ob": obz,
        "fvg_m15": fvg,
        "escenario_sugerido": escenario,
        "conclusion": "TESLABTC A.P. = PA pura: Estructura (BOS), Liquidez y POI (OB/FVG). Sin volumen ni Fibonacci."
    }
