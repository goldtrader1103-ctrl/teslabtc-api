from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import (
    TZ_COL, obtener_precio, obtener_klines_binance,
    _pdh_pdl, _asia_range, sesion_ny_activa, detectar_estructura
)

router = APIRouter()

@router.get("/estado_general", tags=["TESLABTC"])
def estado_general_teslabtc():
    """Dashboard TESLABTC A.P — Estructura, Liquidez y Escenarios"""
    ahora_col = datetime.now(TZ_COL)
    precio = obtener_precio()
    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)
    velas_m5 = obtener_klines_binance("5m", 120)

    estr_h1 = detectar_estructura(velas_h1)
    estr_m15 = detectar_estructura(velas_m15)
    estr_m5 = detectar_estructura(velas_m5)

    pdh, pdl = _pdh_pdl(velas_h1)
    asia_high, asia_low = _asia_range(velas_m15)
    en_ny = sesion_ny_activa(ahora_col)

    # Escenario A+
    escenario = "⏸️ Esperar confirmación clara"
    alta_prob = False
    if estr_h1["tipo_BOS"] == "alcista" and estr_m5["tipo_BOS"] == "alcista":
        escenario = "BUY A+ 🔥 — BOS H1 + BOS M5"
        alta_prob = True
    elif estr_h1["tipo_BOS"] == "bajista" and estr_m5["tipo_BOS"] == "bajista":
        escenario = "SELL A+ 🔥 — BOS H1 + BOS M5"
        alta_prob = True

    confirmaciones = {
        "BOS H1": "✅" if estr_h1["BOS"] else "❌",
        "BOS M15": "✅" if estr_m15["BOS"] else "❌",
        "BOS M5": "✅" if estr_m5["BOS"] else "❌",
        "Sesión NY": "✅" if en_ny else "❌",
    }

    conclusion = "PA Puro — estructura y liquidez. "
    conclusion += "Alta probabilidad" if alta_prob else "Esperar BOS M15 o A+."

    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "par": "BTCUSDT",
        "precio": precio,
        "sesión_NY": "Activa ✅" if en_ny else "Fuera ❌",
        "estructura": {"H1": estr_h1, "M15": estr_m15, "M5": estr_m5},
        "escenario": escenario,
        "confirmaciones": confirmaciones,
        "conclusión": conclusion
    }
