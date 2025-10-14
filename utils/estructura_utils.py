# ============================================================
# 🧠 ESTRUCTURA Y ESCENARIOS – TESLABTC.KG (v3.6.0)
# ============================================================

def evaluar_estructura(velas: list[dict]) -> dict:
    """
    Evalúa si la estructura es alcista o bajista según máximos/mínimos recientes.
    """
    if not velas or len(velas) < 10:
        return {"estado": "sin_datos"}

    highs = [v["high"] for v in velas[-20:]]
    lows = [v["low"] for v in velas[-20:]]
    last_close = velas[-1]["close"]

    maximo = max(highs)
    minimo = min(lows)

    if last_close > highs[-1] and highs[-1] > highs[-5]:
        estado = "alcista"
    elif last_close < lows[-1] and lows[-1] < lows[-5]:
        estado = "bajista"
    else:
        estado = "rango"

    return {
        "estado": estado,
        "high": round(maximo, 2),
        "low": round(minimo, 2)
    }

# ============================================================
# 📈 DEFINIR ESCENARIOS TESLABTC A.P.
# ============================================================

def definir_escenarios(estructura: dict) -> dict:
    h4 = estructura.get("H4 (macro)", "sin_datos")
    h1 = estructura.get("H1 (intradía)", "sin_datos")
    m15 = estructura.get("M15 (reacción)", "sin_datos")

    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "acción": "Buscar entradas long (BOS M15 dentro de POI M15 o retroceso 61.8%)",
            "gestión": "Objetivo 1:3 | BE en 1:1 + 50%",
            "mensaje": "📈 Estructura alineada a favor del impulso principal"
        }

    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional bajista",
            "acción": "Buscar shorts en reacción M15–M5 a favor de H1",
            "gestión": "Objetivo 1:3 | BE en 1:1 + 50%",
            "mensaje": "📉 Estructura macro e intradía alineadas a la baja"
        }

    if h1 != h4 and m15 != h1:
        return {
            "escenario": "SCALPING CONTRA TENDENCIA",
            "nivel": "Retroceso",
            "acción": "Operar M15 con confirmación M5–M3 dentro de retroceso controlado",
            "gestión": "Objetivo 1:1 o 1:2 | Riesgo reducido",
            "mensaje": "⚡ Escenario arriesgado (contra estructura H1)"
        }

    return {
        "escenario": "CONSERVADOR 2",
        "nivel": "Reentrada",
        "acción": "Esperar mitigación de segunda zona o reentrada tras BOS fallido",
        "gestión": "Mantener riesgo bajo",
        "mensaje": "🟡 Posible continuación si se confirma BOS limpio"
    }
