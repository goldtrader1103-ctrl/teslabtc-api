# ============================================================
# 🧭 TESLABTC.KG — utils/estructura_utils.py (v3.6.1)
# ============================================================
# Compatible con klines en formato dict o lista.
# Lee velas Binance / CoinGecko y devuelve:
#  - estado: alcista / bajista / rango / sin_datos
#  - high / low de zona operativa (swing recent)
#  - Mensajes de escenario (conservador / scalping / rango)
# ============================================================

from statistics import mean

def _closes(klines):
    """
    Extrae cierres de cualquier formato (lista o dict).
    """
    try:
        if not klines:
            return []
        if isinstance(klines[0], dict):
            return [float(k["close"]) for k in klines]
        return [float(k[4]) for k in klines]
    except Exception:
        return []

def _swing_zone(klines, lookback=30):
    """
    Calcula zona operativa simple: max/min de los últimos 'lookback' candles.
    Acepta klines dict o lista.
    """
    if not klines:
        return None, None

    data = klines[-lookback:] if len(klines) >= lookback else klines

    try:
        if isinstance(data[0], dict):
            highs = [float(k["high"]) for k in data]
            lows = [float(k["low"]) for k in data]
        else:
            highs = [float(k[2]) for k in data]
            lows = [float(k[3]) for k in data]
    except Exception:
        return None, None

    return (max(highs) if highs else None, min(lows) if lows else None)


def evaluar_estructura(klines):
    """
    Heurística robusta y compatible con formato dict o lista.
      - si no hay 25+ velas → sin_datos
      - calcula MA(10) vs MA(30) y cierre relativo
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
# ============================================================
# 🔍 DETECCIÓN DE BOS Y OB (Soporte para analisis_estructura.py)
# ============================================================

def detectar_bos(klines):
    """
    Detecta un BOS (Break of Structure) simple:
    - Si el cierre actual supera el último máximo → BOS alcista
    - Si el cierre actual rompe el último mínimo → BOS bajista
    Retorna: {"bos": True/False, "tipo": "alcista"/"bajista"/None}
    """
    try:
        if not klines or len(klines) < 10:
            return {"bos": False, "tipo": None}

        closes = [float(k["close"]) for k in klines[-20:]] if isinstance(klines[0], dict) else [float(k[4]) for k in klines[-20:]]
        highs = [float(k["high"]) for k in klines[-20:]] if isinstance(klines[0], dict) else [float(k[2]) for k in klines[-20:]]
        lows = [float(k["low"]) for k in klines[-20:]] if isinstance(klines[0], dict) else [float(k[3]) for k in klines[-20:]]

        last_close = closes[-1]
        prev_high = max(highs[:-1])
        prev_low = min(lows[:-1])

        if last_close > prev_high:
            return {"bos": True, "tipo": "alcista"}
        elif last_close < prev_low:
            return {"bos": True, "tipo": "bajista"}
        else:
            return {"bos": False, "tipo": None}
    except Exception:
        return {"bos": False, "tipo": None}


def detectar_ob(klines):
    """
    Detecta un Order Block simple:
    - Busca la última vela con cuerpo grande y dirección opuesta al impulso actual.
    Retorna: {"ob": True/False, "tipo": "oferta"/"demanda"/None}
    """
    try:
        if not klines or len(klines) < 10:
            return {"ob": False, "tipo": None}

        # Detectar cuerpo promedio
        if isinstance(klines[0], dict):
            bodies = [abs(float(k["close"]) - float(k["open"])) for k in klines[-30:]]
        else:
            bodies = [abs(float(k[4]) - float(k[1])) for k in klines[-30:]]

        avg_body = sum(bodies) / len(bodies)
        threshold = avg_body * 1.5

        for k in reversed(klines[-15:]):
            if isinstance(k, dict):
                o, c = float(k["open"]), float(k["close"])
            else:
                o, c = float(k[1]), float(k[4])
            body_size = abs(c - o)

            # Si el cuerpo es grande, consideramos OB
            if body_size > threshold:
                tipo = "demanda" if c > o else "oferta"
                return {"ob": True, "tipo": tipo}

        return {"ob": False, "tipo": None}
    except Exception:
        return {"ob": False, "tipo": None}
# ============================================================
# 💬 CONTEXTO AUTOMÁTICO TESLABTC — frases dinámicas (v3.6.2)
# ============================================================
import random

def generar_contexto_auto(tendencia: str, bos_tipo: str | None, ob_tipo: str | None, sesion_activa: bool) -> str:
    """
    Genera un contexto narrativo aleatorio según el estado estructural.
    Retorna una frase coherente y diferente en cada análisis.
    """
    try:
        frases = []

        # 🔻 Contextos bajistas
        if tendencia == "bajista":
            frases += [
                "El precio mantiene una estructura bajista clara con presión de venta institucional.",
                "Se observa continuidad bajista tras reacción en zona de oferta activa.",
                "Mercado dominado por vendedores; posible continuación hacia mínimos anteriores.",
                "La estructura sigue siendo bajista, con liquidez limpia pendiente por debajo del PDL.",
                "Presión bajista sólida; el precio se encuentra bajo la media clave y respeta la estructura macro."
            ]

            if bos_tipo == "bajista":
                frases += [
                    "BOS bajista confirmado, reforzando la intención de continuidad descendente.",
                    "Nueva ruptura de estructura a la baja, alineada con la macro dirección.",
                ]

            if ob_tipo == "oferta":
                frases += [
                    "Reacción técnica en OB de oferta; el impulso vendedor domina la sesión.",
                    "El precio rechazó con fuerza el OB de oferta más reciente.",
                ]

        # 🔺 Contextos alcistas
        elif tendencia == "alcista":
            frases += [
                "El mercado mantiene estructura alcista y los compradores controlan el impulso.",
                "Se consolida una tendencia alcista estable con mínimos ascendentes.",
                "El precio muestra fuerza compradora y sostiene la estructura positiva.",
                "Presión alcista sostenida tras mitigación de zona de demanda clave.",
                "Estructura saludable con BOS alcista confirmado y demanda respetada."
            ]

            if bos_tipo == "alcista":
                frases += [
                    "BOS alcista reciente; los compradores recuperan el control del movimiento.",
                    "Confirmación de ruptura al alza que valida continuidad hacia niveles superiores.",
                ]

            if ob_tipo == "demanda":
                frases += [
                    "Reacción positiva en OB de demanda, validando absorción de liquidez bajista.",
                    "Zona de demanda respetada con alto volumen; continuidad esperada.",
                ]

        # 🔸 Contextos neutros / rango
        else:
            frases += [
                "Mercado lateral; sin claridad direccional hasta ruptura limpia.",
                "Estructura neutral entre oferta y demanda; preferible esperar confirmaciones.",
                "Consolidación sin dirección definida; se sugiere paciencia operativa.",
                "Movimiento rango con baja volatilidad; posible expansión próxima.",
            ]

        # ⏰ Añadir contexto de sesión
        if sesion_activa:
            frases += [
                "La sesión de Nueva York está activa, incrementando la volatilidad esperada.",
                "Sesión NY abierta; posibles manipulaciones antes del movimiento real.",
                "Con la apertura de NY, se esperan movimientos institucionales direccionales.",
            ]
        else:
            frases += [
                "Fuera de la sesión NY, el volumen institucional se mantiene reducido.",
                "El mercado opera con bajo impulso fuera de la sesión de Nueva York.",
            ]

        # 🎲 Devolver una frase aleatoria
        return random.choice(frases)
    except Exception:
        return "Contexto general no disponible."
