# ============================================================
# 📊 ESTRUCTURA DE MERCADO – TESLABTC.KG (versión avanzada)
# ============================================================

from datetime import datetime, timezone, timedelta

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🧠 EVALUAR ESTRUCTURA MACRO / INTRADÍA / MICRO
# ============================================================

def evaluar_estructura(velas_h4, velas_h1, velas_m15):
    """
    Evalúa la estructura del mercado con base en velas de distintas temporalidades.
    Devuelve estados y zonas de reacción (High-Low) por timeframe.
    """

    def detectar_estado(velas):
        if not velas or len(velas) < 5:
            return "sin_datos", None, None

        ultimos = velas[-40:]
        highs = [v["high"] for v in ultimos]
        lows = [v["low"] for v in ultimos]
        closes = [v["close"] for v in ultimos]

        tendencia = "alcista" if closes[-1] > closes[0] else "bajista"
        zona_high = max(highs)
        zona_low = min(lows)
        return tendencia, zona_high, zona_low

    h4_estado, h4_high, h4_low = detectar_estado(velas_h4)
    h1_estado, h1_high, h1_low = detectar_estado(velas_h1)
    m15_estado, m15_high, m15_low = detectar_estado(velas_m15)

    # ============================================================
    # 🧩 CONTEXTO ESTRUCTURAL
    # ============================================================
    if h4_estado == "alcista" and h1_estado == "alcista":
        contexto = "flujo alcista dominante — continuación probable"
    elif h4_estado == "bajista" and h1_estado == "bajista":
        contexto = "flujo bajista dominante — continuación probable"
    elif h4_estado != h1_estado:
        contexto = "fase de transición — posible retroceso o mitigación"
    else:
        contexto = "rango o compresión — sin dirección clara"

    estructura = {
        "H4 (macro)": h4_estado,
        "H1 (intradía)": h1_estado,
        "M15 (reacción)": m15_estado,
    }

    zonas = {
        "ZONA H4 (macro)": {"High": h4_high, "Low": h4_low},
        "ZONA H1 (intradía)": {"High": h1_high, "Low": h1_low},
        "ZONA M15 (reacción)": {"High": m15_high, "Low": m15_low},
    }

    return {
        "estructura": estructura,
        "zonas": zonas,
        "contexto": contexto,
    }

# ============================================================
# 🔍 DETECTAR BOS / CHoCH SIMPLE (Price Action Puro)
# ============================================================

def detectar_bos(velas, tipo="alcista"):
    """
    Detecta ruptura de estructura (Break of Structure) o CHoCH simple.
    Retorna True si se confirma ruptura válida.
    """
    if not velas or len(velas) < 10:
        return False

    ultimos = velas[-15:]
    highs = [v["high"] for v in ultimos]
    lows = [v["low"] for v in ultimos]
    close = velas[-1]["close"]

    if tipo == "alcista" and close > max(highs[:-3]):
        return True
    if tipo == "bajista" and close < min(lows[:-3]):
        return True
    return False

# ============================================================
# 🧭 GENERAR ESCENARIOS ESTRUCTURALES
# ============================================================

def definir_escenarios(estructura, zonas, sesion_activa):
    """
    Devuelve el escenario operativo (conservador, reentrada o scalping).
    """

    h4 = estructura.get("H4 (macro)")
    h1 = estructura.get("H1 (intradía)")
    m15 = estructura.get("M15 (reacción)")

    escenarios = []

    # Escenario principal — Conservador 1
    if h4 == h1 and h4 in ["alcista", "bajista"]:
        escenarios.append({
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "zona_principal": zonas["ZONA H1 (intradía)"],
            "razon": f"H4 y H1 alineados ({h4}). Continuación esperada.",
            "accion": f"Operar {h4.upper()} con confirmación BOS M5 dentro del POI M15.\n"
                      "Objetivo: 1:3 o más.\n💡 Gestión de riesgo estricta.",
            "tipo": "principal"
        })

    # Reentrada si existe extensión estructural (ej. más liquidez por mitigar)
    if h4 == h1 and h1 == "bajista" and m15 == "bajista":
        escenarios.append({
            "escenario": "CONSERVADOR 2 (reentrada)",
            "nivel": "Institucional extendido",
            "zona_principal": zonas["ZONA M15 (reacción)"],
            "razon": "Reentrada en continuación estructural bajista (H4–H1–M15).",
            "accion": "Esperar nuevo impulso bajista con confirmación BOS M3.\n"
                      "Posible cobertura SL ampliada.\n🎯 Reentrada controlada.",
            "tipo": "reentrada"
        })

    # Escenario scalping — Contra tendencia
    if h1 != m15:
        escenarios.append({
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Agresivo / bajo confirmación rápida",
            "zona_principal": zonas["ZONA M15 (reacción)"],
            "razon": f"Retroceso M15 contra tendencia intradía ({h1}).",
            "accion": "Buscar oportunidad rápida en retroceso M15.\n"
                      "Confirmar BOS micro M5–M3 antes de ejecutar.\n"
                      "RRR máximo 1:1 o 1:2.\n⚠️ Solo apto para traders avanzados.",
            "tipo": "scalping"
        })

    # Si sesión cerrada
    if not sesion_activa:
        for e in escenarios:
            e["nota"] = "Sesión NY cerrada — solo modo observación / backtesting."

    return escenarios
