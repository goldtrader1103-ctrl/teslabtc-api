from fastapi import APIRouter
from utils.price_utils import (
    obtener_precio, obtener_klines_binance, detectar_bos,
    detectar_fvg_m15, detectar_ob_h1_h4, sesion_ny_activa, ahora_col
)

router = APIRouter()

@router.get("/confirmaciones")
def confirmaciones():
    precio = obtener_precio()
    h4 = obtener_klines_binance(interval="4h", limit=60)
    h1 = obtener_klines_binance(interval="1h", limit=60)
    m15 = obtener_klines_binance(interval="15m", limit=60)

    bos_h4 = detectar_bos(h4, bullish=True) or detectar_bos(h4, bullish=False)
    bos_h1 = detectar_bos(h1, bullish=True) or detectar_bos(h1, bullish=False)
    bos_m15_up  = detectar_bos(m15, bullish=True)
    bos_m15_dn  = detectar_bos(m15, bullish=False)

    obz = detectar_ob_h1_h4()
    fvg = detectar_fvg_m15()
    sesion_ok = sesion_ny_activa()

    conf = {
        "BOS H4": "✅" if bos_h4 else "⚠️",
        "BOS H1 (dirección del día)": "✅" if bos_h1 else "⚠️",
        "BOS M15 (gatillo)": "✅" if (bos_m15_up or bos_m15_dn) else "❌",
        "POI/OB/FVG identificados": "✅" if (obz["H1"] != (None,None) or obz["H4"] != (None,None) or fvg["bullish"] or fvg["bearish"]) else "⚠️",
        "Sesión NY (07:00–13:30)": "✅" if sesion_ok else "❌"
    }

    veredicto = "Setup potencial — ejecutar en M5 (Level Entry) si M15 imprime BOS dentro de POI."
    if conf["BOS M15 (gatillo)"] == "❌":
        veredicto = "Esperar gatillo: BOS M15 dentro del POI."

    return {
        "timestamp": ahora_col().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio,
        "confirmaciones": conf,
        "veredicto": veredicto,
        "gestion": "BE 1:1, parcial 50% 1:2, dejar correr 1:3 o liquidez limpia. Sin volumen ni fibo."
    }
