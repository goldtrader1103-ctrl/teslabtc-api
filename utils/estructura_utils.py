# ============================================================
# 🧠 ESTRUCTURA MULTITEMPORAL TESLABTC.KG
# ============================================================

from statistics import mean

def evaluar_estructura(velas_h4, velas_h1, velas_m15):
    """Analiza estructura macro (H4), intradía (H1) y reacción (M15)."""
    def tendencia(velas):
        if not velas: return "sin_datos"
        closes = [v["close"] for v in velas[-40:]]
        return "alcista" if closes[-1] > closes[0] else "bajista"

    estructura = {
        "H4 (macro)": tendencia(velas_h4),
        "H1 (intradía)": tendencia(velas_h1),
        "M15 (reacción)": tendencia(velas_m15),
    }

    def zona(velas):
        if not velas: return {"High": None, "Low": None}
        highs = [v["high"] for v in velas[-10:]]
        lows = [v["low"] for v in velas[-10:]]
        return {"High": round(max(highs), 2), "Low": round(min(lows), 2)}

    zonas = {
        "ZONA H4 (macro)": zona(velas_h4),
        "ZONA H1 (intradía)": zona(velas_h1),
        "ZONA M15 (reacción)": zona(velas_m15),
    }

    contexto = "flujo alcista dominante — continuación probable" if estructura["H4 (macro)"] == "alcista" else \
                "flujo bajista dominante — continuación probable"

    return {"estructura": estructura, "zonas": zonas, "contexto": contexto}

def definir_escenarios(estructura, zonas, sesion_activa):
    """Define escenarios según contexto estructural."""
    h4 = estructura.get("H4 (macro)")
    h1 = estructura.get("H1 (intradía)")
    m15 = estructura.get("M15 (reacción)")

    escenarios = []

    if h4 == h1 == "alcista":
        escenarios.append({
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razon": "H4 y H1 alineados alcistas.",
            "accion": "Operar BUY A+ con confirmación BOS M5 dentro del POI M15.\nObjetivo: 1:3 o más.\n💡 Gestión de riesgo estricta.",
            "tipo": "principal"
        })
    elif h4 == h1 == "bajista":
        escenarios.append({
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razon": "H4 y H1 alineados bajistas.",
            "accion": "Operar SELL A+ con confirmación BOS M5 dentro del POI M15.\nObjetivo: 1:3 o más.\n💡 Gestión de riesgo estricta.",
            "tipo": "principal"
        })
    else:
        escenarios.append({
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Avanzado",
            "razon": "Microestructura M15 opuesta a H1.",
            "accion": "Buscar retroceso M15 y confirmar con BOS M5.\nRRR máximo: 1:2.\nSolo para traders avanzados.",
            "tipo": "scalping"
        })

    return escenarios
