from fastapi import APIRouter
from datetime import datetime, time
from typing import Dict, Any
from utils.price_utils import (
    obtener_precio,
    obtener_klines,
    detectar_bos,
    _pdh_pdl,
    _asia_range,
    TZ_COL,
)

router = APIRouter()

# =====================================================
# SESIÓN NY
# =====================================================

def sesion_ny_activa(ahora_col: datetime) -> bool:
    """Sesión NY TESLABTC (COL): 07:00–13:30"""
    start = time(7, 0)
    end = time(13, 30)
    t = ahora_col.time()
    return start <= t <= end


# =====================================================
# ENDPOINT PRINCIPAL
# =====================================================

@router.get("/estado_general", tags=["TESLABTC"])
def estado_general_teslabtc() -> Dict[str, Any]:
    """Dashboard TESLABTC A.P v2.1 — estructura, flujo y escenarios."""

    ahora_col = datetime.now(TZ_COL)

    # 1️⃣ Datos base
    precio = obtener_precio()
    velas_h1 = obtener_klines("1h", 120)
    velas_m15 = obtener_klines("15m", 120)
    velas_m5 = obtener_klines("5m", 150)

    # 2️⃣ Estructura y flujo direccional por temporalidad
    estr_h1 = detectar_bos(velas_h1) if velas_h1 else {"rango": True}
    estr_m15 = detectar_bos(velas_m15) if velas_m15 else {"BOS": False}
    estr_m5 = detectar_bos(velas_m5) if velas_m5 else {"BOS": False}

    # 3️⃣ Liquidez (PDH/PDL y Asia)
    pdh, pdl = _pdh_pdl(velas_h1) if velas_h1 else (None, None)
    asia_high, asia_low = _asia_range(velas_m15) if velas_m15 else (None, None)

    # 4️⃣ Sesión NY
    en_ny = sesion_ny_activa(ahora_col)
    sesion_txt = f"{'✅ Activa' if en_ny else '❌ Fuera'} (07:00–13:30 COL)"

    # 5️⃣ Interpretación de flujo macro
    flujo_macro = estr_h1.get("flujo")
    tipo_bos = estr_h1.get("tipo_BOS")
    tendencia_txt = "Rango"
    if tipo_bos == "alcista":
        tendencia_txt = "Tendencia Alcista (BOS)"
    elif tipo_bos == "bajista":
        tendencia_txt = "Tendencia Bajista (BOS)"
    elif flujo_macro == "alcista":
        tendencia_txt = "Flujo Alcista Progresivo"
    elif flujo_macro == "bajista":
        tendencia_txt = "Flujo Bajista Progresivo"

    # 6️⃣ Escenarios TESLABTC A.P.
    escenario = "⏸️ Esperar BOS M15 dentro de POI"
    alta_prob = False
    motivo = []

    # Setup A+ : BOS H1 + barrida contraria + BOS M5
    if estr_h1.get("tipo_BOS") == "alcista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "alcista" and estr_m5.get("barrida_bajista"):
        escenario = "BUY A+ 🔥 — BOS H1 + barrida bajista + BOS M5"
        alta_prob = True
        motivo.append("Flujo mayor y micro alineados")

    elif estr_h1.get("tipo_BOS") == "bajista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "bajista" and estr_m5.get("barrida_alcista"):
        escenario = "SELL A+ 🔥 — BOS H1 + barrida alcista + BOS M5"
        alta_prob = True
        motivo.append("Flujo mayor y micro alineados")

    # Setup BASE : BOS M15 o flujo direccional M15
    elif estr_m15.get("BOS") or estr_m15.get("flujo"):
        if estr_m15.get("tipo_BOS") == "alcista" or estr_m15.get("flujo") == "alcista":
            escenario = "SETUP BASE ✅ — BUY si BOS/flujo M15 + retroceso M5"
        else:
            escenario = "SETUP BASE ✅ — SELL si BOS/flujo M15 + retroceso M5"
        motivo.append("Confirmación (gatillo) M15")

    else:
        if estr_h1.get("rango", False):
            escenario = "⏸️ RANGO — Esperar intención (BOS M15) o barrida de PDH/PDL"
        else:
            dir_h1 = flujo_macro or tipo_bos
            if dir_h1 == "alcista":
                escenario = "📈 Flujo alcista — Esperar BOS/retroceso M15 para BUY"
            elif dir_h1 == "bajista":
                escenario = "📉 Flujo bajista — Esperar BOS/retroceso M15 para SELL"

    # 7️⃣ Reglas de gestión TESLABTC A.P.
    ejecucion = {
        "gatillo_obligatorio": "BOS/flujo M15 (salvo setup A+: BOS H1 + barrida + BOS M5)",
        "m5_level_entry": "Tras el gatillo, entrar en OB/FVG o micro-bos M5 (inicio o 50 %)",
        "sl": "En invalidación estructural",
        "tp": "Piscinas de liquidez; RRR mínimo 1:3",
        "gestion": "BE 1:1; 50 % en 1:2; dejar correr hacia 1:3 o siguiente liquidez limpia"
    }

    # 8️⃣ Confirmaciones actuales (Price Action Puro)
    confirmaciones = {
        "BOS H1": "✅" if estr_h1.get("BOS") else ("📈" if flujo_macro == "alcista" else "📉" if flujo_macro == "bajista" else "⏸️"),
        "BOS M15": "✅" if estr_m15.get("BOS") else ("📈" if estr_m15.get("flujo") == "alcista" else "📉" if estr_m15.get("flujo") == "bajista" else "❌"),
        "BOS M5": "✅" if estr_m5.get("BOS") else "❌",
        "Barrida PDH/PDL": "⚠️" if (pdh and precio and (precio > pdh or precio < pdl)) else "—",
        "Barrida Asia": "⚠️" if (asia_high and precio and (precio > asia_high or precio < asia_low)) else "—",
        "Sesión NY": "✅" if en_ny else "❌",
    }

    # 9️⃣ Conclusión TESLABTC A.P.
    conclusion = "Análisis PA Puro (Estructura + Flujo + Liquidez). "
    if alta_prob:
        conclusion += "Escenario de ALTA PROBABILIDAD activo."
    else:
        conclusion += "Esperar confirmación (BOS/flujo M15 o Setup A+)."

    # 🔚 Retorno JSON
    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "par": "BTCUSDT",
        "precio_referencia": precio,
        "tendencia_macro": tendencia_txt,
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
