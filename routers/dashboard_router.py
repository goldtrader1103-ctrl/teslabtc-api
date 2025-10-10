from fastapi import APIRouter
from datetime import datetime, time
from typing import Dict, Any

from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    detectar_estructura,
    _pdh_pdl,
    _asia_range,
    TZ_COL,
)

router = APIRouter()


def sesion_ny_activa(ahora_col: datetime) -> bool:
    """
    Sesión NY TESLABTC (COL): 07:00–13:30
    """
    start = time(7, 0)
    end = time(13, 30)
    t = ahora_col.time()
    return (t >= start) and (t <= end)


@router.get("/estado_general", tags=["TESLABTC"])
def estado_general_teslabtc() -> Dict[str, Any]:
    """
    Dashboard TESLABTC A.P (PA puro): estructura, liquidez, setups.
    """
    ahora_col = datetime.now(TZ_COL)

    # 1) Datos base
    precio = obtener_precio()
    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)
    velas_m5 = obtener_klines_binance("5m", 150)

    # 2) Estructura por TF
    estr_h1 = detectar_estructura(velas_h1, lookback=20) if velas_h1 else {"rango": True}
    estr_m15 = detectar_estructura(velas_m15, lookback=20) if velas_m15 else {"BOS": False}
    estr_m5 = detectar_estructura(velas_m5, lookback=20) if velas_m5 else {"BOS": False}

    # 3) Liquidez (PDH/PDL y Asia)
    pdh, pdl = _pdh_pdl(velas_h1) if velas_h1 else (None, None)
    asia_high, asia_low = _asia_range(velas_m15) if velas_m15 else (None, None)

    # 4) Sesión NY
    en_ny = sesion_ny_activa(ahora_col)
    sesion_txt = f"{'✅ Activa' if en_ny else '❌ Fuera'} (07:00–13:30 COL)"

    # 5) Lógica TESLABTC A.P de escenarios
    escenario = "⏸️ Esperar BOS en M15 dentro de POI"  # fallback
    alta_prob = False
    motivo = []

    # A+ : BOS H1 + barrida contraria + BOS M5 (direccional)
    if estr_h1.get("tipo_BOS") == "alcista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "alcista" and estr_m5.get("barrida_bajista"):
        escenario = "BUY A+ 🔥 — BOS H1 + barrida bajista + BOS M5"
        alta_prob = True
        motivo.append("Flujo mayor y micro alineados")

    elif estr_h1.get("tipo_BOS") == "bajista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "bajista" and estr_m5.get("barrida_alcista"):
        escenario = "SELL A+ 🔥 — BOS H1 + barrida alcista + BOS M5"
        alta_prob = True
        motivo.append("Flujo mayor y micro alineados")

    # Setup BASE: BOS M15
    elif estr_m15.get("BOS"):
        if estr_m15.get("tipo_BOS") == "alcista":
            escenario = "SETUP BASE ✅ — BUY si BOS M15 + retroceso M5"
        else:
            escenario = "SETUP BASE ✅ — SELL si BOS M15 + retroceso M5"
        motivo.append("Confirmación (gatillo) M15")

    # Si no hay nada confirmado
    else:
        if estr_h1.get("rango", False):
            escenario = "⏸️ RANGO — Esperar intención (BOS M15) o barrida de PDH/PDL"
        else:
            # Flujo H1 sin gatillos aún
            dir_h1 = estr_h1.get("tipo_BOS")
            if dir_h1 == "alcista":
                escenario = "📈 Tendencia H1 — Esperar BOS M15 alcista para BUY"
            elif dir_h1 == "bajista":
                escenario = "📉 Tendencia H1 — Esperar BOS M15 bajista para SELL"

    # 6) Reglas de ejecución TESLABTC A.P
    ejecucion = {
        "gatillo_obligatorio": "BOS M15 (salvo setup A+: BOS H1 + barrida + BOS M5)",
        "m5_level_entry": "Tras el gatillo, entrar en OB/FVG o micro-bos de M5 (inicio o 50%)",
        "sl": "En invalidación estructural",
        "tp": "Piscinas de liquidez; RRR mínimo 1:3",
        "gestion": "BE 1:1; 50% en 1:2; dejar correr hacia 1:3 o siguiente liquidez limpia"
    }

    # 7) Confirmaciones actuales (solo PA)
    confirmaciones = {
        "BOS H4/H1": "✅" if estr_h1.get("BOS") else ("⏸️ Rango" if estr_h1.get("rango") else "⚠️"),
        "BOS M15 (gatillo)": "✅" if estr_m15.get("BOS") else "❌",
        "BOS M5": "✅" if estr_m5.get("BOS") else "❌",
        "Barrida PDH/PDL": "⚠️" if (pdh and precio and (precio > pdh or precio < pdl)) else "—",
        "Barrida Asia": "⚠️" if (asia_high and precio and precio > asia_high) or (asia_low and precio and precio < asia_low) else "—",
        "Sesión NY": "✅" if en_ny else "❌",
    }

    # 8) Conclusión breve
    conclusion = "PA puro (Estructura + Liquidez). "
    if alta_prob:
        conclusion += "Escenario de ALTA PROBABILIDAD activo."
    else:
        conclusion += "Esperar confirmación clara (BOS M15 o Setup A+)."

    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "par": "BTCUSDT",
        "precio_referencia": precio,
        "sesion_NY": sesion_txt,
        "pdh_pdl": {"PDH": pdh, "PDL": pdl},
        "asia": {"high": asia_high, "low": asia_low},
        "estructura": {
            "H1": estr_h1,
            "M15": estr_m15,
            "M5": estr_m5,
        },
        "escenario_sugerido": escenario,
        "alta_probabilidad": alta_prob,
        "motivo": motivo,
        "confirmaciones": confirmaciones,
        "ejecucion_TESLABTC_AP": ejecucion,
        "conclusion": conclusion,
    }
