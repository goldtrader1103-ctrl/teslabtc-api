from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from utils.price_utils import (
    obtener_klines_binance,
    detectar_estructura,
    _pdh_pdl,
    _asia_range,
    TZ_COL,
)

router = APIRouter()


@router.get("/confirmaciones", tags=["TESLABTC"])
def confirmaciones_teslabtc() -> Dict[str, Any]:
    """
    Analiza las confirmaciones TESLABTC A.P. (PA puro):
    - BOS por temporalidad (H1, M15, M5)
    - Barridas de PDH/PDL o rango asiático
    - Identifica Setup Base (BOS M15) o Setup A+ (BOS H1 + barrida + BOS M5)
    """
    ahora_col = datetime.now(TZ_COL)

    # 1️⃣ Velas recientes
    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)
    velas_m5 = obtener_klines_binance("5m", 150)

    if not velas_h1 or not velas_m15 or not velas_m5:
        return {"error": "No se pudieron obtener velas reales desde Binance."}

    # 2️⃣ Estructura
    estr_h1 = detectar_estructura(velas_h1, lookback=20)
    estr_m15 = detectar_estructura(velas_m15, lookback=20)
    estr_m5 = detectar_estructura(velas_m5, lookback=20)

    # 3️⃣ Liquidez
    pdh, pdl = _pdh_pdl(velas_h1)
    asia_high, asia_low = _asia_range(velas_m15)

    # 4️⃣ Confirmaciones base
    confirmaciones = {
        "BOS H1": "✅" if estr_h1.get("BOS") else ("⏸️ Rango" if estr_h1.get("rango") else "❌"),
        "BOS M15": "✅" if estr_m15.get("BOS") else "❌",
        "BOS M5": "✅" if estr_m5.get("BOS") else "❌",
        "Barrida PDH": "⚠️" if estr_h1.get("barrida_alcista") else "—",
        "Barrida PDL": "⚠️" if estr_h1.get("barrida_bajista") else "—",
        "Barrida Asia": "⚠️" if (estr_m15.get("barrida_alcista") or estr_m15.get("barrida_bajista")) else "—",
    }

    # 5️⃣ Detección de setups
    setup = "⏸️ Sin setup activo"
    alta_prob = False

    # Setup A+ → BOS H1 + barrida contraria + BOS M5 alineado
    if estr_h1.get("tipo_BOS") == "alcista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "alcista" and estr_m5.get("barrida_bajista"):
        setup = "🔥 Setup A+ BUY — BOS H1 + barrida bajista + BOS M5 alcista"
        alta_prob = True

    elif estr_h1.get("tipo_BOS") == "bajista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "bajista" and estr_m5.get("barrida_alcista"):
        setup = "🔥 Setup A+ SELL — BOS H1 + barrida alcista + BOS M5 bajista"
        alta_prob = True

    # Setup Base → BOS M15 válido
    elif estr_m15.get("BOS"):
        if estr_m15.get("tipo_BOS") == "alcista":
            setup = "✅ Setup BASE BUY — BOS M15 alcista"
        elif estr_m15.get("tipo_BOS") == "bajista":
            setup = "✅ Setup BASE SELL — BOS M15 bajista"

    # 6️⃣ Observaciones
    observacion = "Esperar confirmación adicional."
    if alta_prob:
        observacion = "Escenario de ALTA PROBABILIDAD activo."
    elif estr_m15.get("BOS"):
        observacion = "Gatillo M15 confirmado — buscar entrada M5 (Level Entry)."
    elif estr_h1.get("rango"):
        observacion = "Mercado en rango — esperar BOS o barrida de liquidez."

    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "estructura": {
            "H1": estr_h1,
            "M15": estr_m15,
            "M5": estr_m5,
        },
        "confirmaciones": confirmaciones,
        "setup_actual": setup,
        "alta_probabilidad": alta_prob,
        "observacion": observacion,
        "pdh_pdl": {"PDH": pdh, "PDL": pdl},
        "rango_asia": {"High": asia_high, "Low": asia_low},
        "estrategia": "TESLABTC A.P. — Acción del Precio pura: Estructura, Liquidez y Precisión (sin volumen, sin Fibo).",
    }
