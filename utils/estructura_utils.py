# ============================================================
# 🧠 ESTRUCTURA Y ESCENARIOS – TESLABTC.KG (v3.6.0)
# ============================================================

def evaluar_estructura(velas: list[dict]) -> dict:
    """
    Devuelve:
      {
        "estado": "alcista" | "bajista" | "rango" | "sin_datos",
        "high": float | None,
        "low": float | None
      }
    Regla simple y robusta basada en HH/LL recientes (20 velas).
    """
    if not velas or len(velas) < 10:
        return {"estado": "sin_datos", "high": None, "low": None}

    highs = [v["high"] for v in velas[-20:]]
    lows =  [v["low"]  for v in velas[-20:]]
    last_close = velas[-1]["close"]

    maximo = max(highs) if highs else None
    minimo = min(lows) if lows else None

    # Ruptura de rango reciente como proxy de BOS
    up_break = last_close > highs[-1]
    dn_break = last_close < lows[-1]

    if up_break:
        estado = "alcista"
    elif dn_break:
        estado = "bajista"
    else:
        estado = "rango"

    return {
        "estado": estado,
        "high": round(maximo, 2) if maximo is not None else None,
        "low": round(minimo, 2) if minimo is not None else None
    }

# ============================================================
# 📈 DEFINIR ESCENARIOS TESLABTC A.P.
# ============================================================

def definir_escenarios(estructura_estados: dict) -> dict:
    """
    estructura_estados = {
      "H4 (macro)": "alcista|bajista|rango|sin_datos",
      "H1 (intradía)": "...",
      "M15 (reacción)": "..."
    }
    """
    h4 = estructura_estados.get("H4 (macro)", "sin_datos")
    h1 = estructura_estados.get("H1 (intradía)", "sin_datos")
    m15 = estructura_estados.get("M15 (reacción)", "sin_datos")

    # CONSERVADOR 1 — alineación macro + intradía
    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "acción": "Buscar long: BOS M5 dentro de POI M15 a favor de H1.",
            "gestión": "Objetivo ≥ 1:3 | BE 1:1 | 50% en 1:2.",
            "mensaje": "📈 Flujo alcista alineado."
        }
    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "acción": "Buscar short: BOS M5 dentro de POI M15 a favor de H1.",
            "gestión": "Objetivo ≥ 1:3 | BE 1:1 | 50% en 1:2.",
            "mensaje": "📉 Flujo bajista alineado."
        }

    # SCALPING — contra H1 pero con M15
    if (h1 == "alcista" and m15 == "bajista") or (h1 == "bajista" and m15 == "alcista"):
        return {
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Agresivo",
            "acción": "Operar retroceso M15 con confirmación BOS M5–M3.",
            "gestión": "Objetivo 1:1 o 1:2. Riesgo reducido.",
            "mensaje": "⚡ Solo si dominas la gestión de riesgo."
        }

    # CONSERVADOR 2 — reentrada (H1 en rango con H4 direccional)
    if (h4 in ("alcista", "bajista")) and (h1 == "rango"):
        return {
            "escenario": "CONSERVADOR 2 (reentrada)",
            "nivel": "Institucional",
            "acción": "Esperar CHOCH/BOS M15 a favor de H4. Reentrar tras mitigación.",
            "gestión": "SL cubriendo ambas zonas si hay liquidez extendida.",
            "mensaje": "🟡 Posible continuación tras consolidar."
        }

    # Sin confirmación clara
    return {
        "escenario": "SIN CONFIRMACIÓN",
        "nivel": "Neutro / observación",
        "acción": "Esperar ruptura limpia en H1/M15 antes de ejecutar.",
        "gestión": "Evitar operar sin gatillo validado.",
        "mensaje": "⏸️ Estructuras no alineadas o datos insuficientes."
    }
