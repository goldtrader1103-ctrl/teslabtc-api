# ============================================================
# 🧭 TESLABTC.KG — utils/estructura_utils.py (v3.6.0)
# ============================================================
# Lee velas Binance (lista klines) y devuelve:
#  - estado: alcista / bajista / rango / sin_datos
#  - high / low de zona operativa (swing recent)
#  - Mensajes de escenario (conservador / scalping / rango)
# ============================================================

from statistics import mean

def _closes(klines):
    try:
        return [float(k[4]) for k in klines]
    except Exception:
        return []

def _swing_zone(klines, lookback=30):
    """
    Calcula zona operativa simple: max/min de los últimos 'lookback' candles.
    """
    if not klines:
        return None, None
    data = klines[-lookback:] if len(klines) >= lookback else klines
    highs = [float(k[2]) for k in data]
    lows  = [float(k[3]) for k in data]
    return (max(highs) if highs else None, min(lows) if lows else None)

def evaluar_estructura(klines):
    """
    Heurística robusta:
      - si no hay 25+ velas → sin_datos
      - calcula MA(10) vs MA(30) y cierre relativo para decidir alcista/bajista
      - si el rango es estrecho → rango
    """
    if not klines or len(klines) < 25:
        return {"estado": "sin_datos", "high": None, "low": None}

    closes = _closes(klines)
    if len(closes) < 25:
        return {"estado": "sin_datos", "high": None, "low": None}

    ma_fast = mean(closes[-10:])
    ma_slow = mean(closes[-30:]) if len(closes) >= 30 else mean(closes[:-5] or closes)

    last = closes[-1]
    hi, lo = _swing_zone(klines, 40)

    # Rango si el ancho relativo es muy pequeño
    if hi and lo and hi > lo:
        width_pct = (hi - lo) / ((hi + lo) / 2)
        if width_pct < 0.005:  # <0.5%
            estado = "rango"
        else:
            if ma_fast > ma_slow and last > ma_slow:
                estado = "alcista"
            elif ma_fast < ma_slow and last < ma_slow:
                estado = "bajista"
            else:
                estado = "rango"
    else:
        estado = "sin_datos"

    return {"estado": estado, "high": hi, "low": lo}

def definir_escenarios(estados):
    """
    estados = {"H4": "alcista|bajista|rango|sin_datos", "H1": ..., "M15": ...}
    Devuelve bloque de escenario textual coherente con PA Puro.
    """
    h4 = estados.get("H4", "sin_datos")
    h1 = estados.get("H1", "sin_datos")
    m15 = estados.get("M15", "sin_datos")

    # Conservador (dirección institucional)
    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR (BUY A+)",
            "nivel": "Direccional principal",
            "acción": "Esperar retroceso a zona H1/M15 y gatillo BOS M5 para ejecución.",
            "gestión": "SL en invalidación; TP piscinas de liquidez (RRR ≥ 1:3).",
            "mensaje": "Estructura macro e intradía alineadas al alza."
        }
    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR (SELL A+)",
            "nivel": "Direccional principal",
            "acción": "Esperar retroceso a zona H1/M15 y gatillo BOS M5 para ejecución.",
            "gestión": "SL en invalidación; TP piscinas de liquidez (RRR ≥ 1:3).",
            "mensaje": "Estructura macro e intradía alineadas a la baja."
        }

    # Scalping contra tendencia
    if (h1 in ("alcista", "bajista")) and h4 != h1:
        sentido = "BUY (contra macro)" if h1 == "alcista" else "SELL (contra macro)"
        return {
            "escenario": f"SCALPING {sentido}",
            "nivel": "Agresivo / riesgo controlado",
            "acción": "Solo si hay reacción clara M15 y micro-BOS M5 dentro de la zona.",
            "gestión": "Objetivo corto (1:1 – 1:2). Reducir tamaño y confirmar.",
            "mensaje": "Operación contra la macro; prioridad siempre a la dirección H4."
        }

    # Rango / sin confirmación
    return {
        "escenario": "SIN CONFIRMACIÓN",
        "nivel": "Neutro / Observación",
        "acción": "Esperar ruptura limpia (BOS/CHOCH) en H1/M15 antes de ejecutar.",
        "gestión": "Evitar operar sin gatillo validado.",
        "mensaje": "Estructuras no alineadas o datos insuficientes."
    }
