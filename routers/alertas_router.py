from fastapi import APIRouter
from utils.price_utils import (
    obtener_precio, detectar_fvg_m15, detectar_ob_h1_h4, high_low_anterior_dia, ahora_col
)

router = APIRouter()

def _en_rango(p, rango, tol=30.0):
    if not p or not rango or rango[0] is None or rango[1] is None:
        return False
    lo, hi = sorted(rango)
    # Considera “toque” si el precio entra en el rango con una tolerancia
    return (lo - tol) <= p <= (hi + tol)

@router.get("/alertas")
def alertas():
    p = obtener_precio()
    pdh, pdl = high_low_anterior_dia()
    fvg = detectar_fvg_m15()
    obz = detectar_ob_h1_h4()

    mensaje = "🟢 Sin alertas activas"
    nivel = None

    if p and pdh and abs(p - pdh) <= 30:
        mensaje = f"⚠️ BTCUSDT tocó PDH ({pdh})"
        nivel = "Liquidez alta (PDH)"
    elif p and pdl and abs(p - pdl) <= 30:
        mensaje = f"⚠️ BTCUSDT tocó PDL ({pdl})"
        nivel = "Liquidez alta (PDL)"
    elif p and obz["H1"] != (None,None) and _en_rango(p, obz["H1"], tol=25):
        mensaje = "⚠️ BTCUSDT tocó OB H1"
        nivel = "POI H1"
    elif p and obz["H4"] != (None,None) and _en_rango(p, obz["H4"], tol=25):
        mensaje = "⚠️ BTCUSDT tocó OB H4"
        nivel = "POI H4"
    elif p and fvg["bullish"]:
        for r in fvg["bullish"]:
            if _en_rango(p, r, tol=20):
                mensaje = "⚠️ BTCUSDT tocó FVG alcista M15"
                nivel = f"FVG M15 {r}"
                break
    elif p and fvg["bearish"]:
        for r in fvg["bearish"]:
            if _en_rango(p, r, tol=20):
                mensaje = "⚠️ BTCUSDT tocó FVG bajista M15"
                nivel = f"FVG M15 {r}"
                break

    return {
        "timestamp": ahora_col().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": p,
        "alerta": mensaje,
        "nivel": nivel or "—",
        "accion_recomendada": "Solo ejecutar si hay BOS M15 dentro del POI (ejecución en M5 - Level Entry)."
    }
