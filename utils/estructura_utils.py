# ============================================================
# 🧠 UTILIDADES DE ESTRUCTURA — TESLABTC.KG (v3.6.3)
# ============================================================

def evaluar_estructura(velas):
    """
    Evalúa estructura simple (alcista, bajista o rango) basado en los últimos swings.
    """
    if not velas or len(velas) < 5:
        return {"estado": "sin_datos", "high": None, "low": None}

    highs = [v["high"] for v in velas]
    lows = [v["low"] for v in velas]

    high_reciente = highs[-1]
    low_reciente = lows[-1]

    prev_high = highs[-5]
    prev_low = lows[-5]

    if high_reciente > prev_high and low_reciente > prev_low:
        estado = "alcista"
    elif high_reciente < prev_high and low_reciente < prev_low:
        estado = "bajista"
    else:
        estado = "rango"

    return {"estado": estado, "high": high_reciente, "low": low_reciente}


def definir_escenarios(estructura):
    """
    Define un escenario global con base en la alineación de temporalidades.
    """
    if not estructura:
        return {
            "escenario": "SIN CONFIRMACIÓN",
            "nivel": "Neutro / observación",
            "acción": "Esperar ruptura limpia en H1/M15 antes de ejecutar.",
            "gestión": "Evitar operar sin gatillo validado.",
            "mensaje": "⏸️ Sin datos suficientes."
        }

    h4 = estructura.get("H4 (macro)")
    h1 = estructura.get("H1 (intradía)")
    m15 = estructura.get("M15 (reacción)")

    if h4 == h1 == m15 == "alcista":
        return {
            "escenario": "LONG",
            "nivel": "Alcista confirmado",
            "acción": "Buscar entradas en demanda con confirmación BOS M15.",
            "gestión": "Mantener riesgo bajo y gestión activa.",
            "mensaje": "📈 Tendencia alineada al alza."
        }

    if h4 == h1 == m15 == "bajista":
        return {
            "escenario": "SHORT",
            "nivel": "Bajista confirmado",
            "acción": "Esperar retesteos en oferta para ejecutar ventas.",
            "gestión": "Ajustar stops y parciales rápido.",
            "mensaje": "📉 Tendencia alineada a la baja."
        }

    return {
        "escenario": "SIN CONFIRMACIÓN",
        "nivel": "Neutro / observación",
        "acción": "Esperar ruptura limpia en H1/M15 antes de ejecutar.",
        "gestión": "Evitar operar sin gatillo validado.",
        "mensaje": "⏸️ Estructuras no alineadas o mixtas."
    }
