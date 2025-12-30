# ============================================================
# 🧭 TESLABTC.KG — utils/estructura_utils.py (v3.7.0)
# ============================================================
# Compatible con klines en formato dict o lista.
# Devuelve:
#   - evaluar_estructura: estado + high/low de zona operativa
#   - detectar_estructura_simple: HH/HL vs LH/LL con pivots
#   - definir_escenarios: usa estados H4/H1/M15
#   - detectar_bos / detectar_ob: soporte básico estructural
# ============================================================

from statistics import mean
from typing import List, Dict, Optional
import random


# ============================================================
# 🔹 Helpers base
# ============================================================

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


def _swing_zone(klines, lookback: int = 30):
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


def _extraer_hl(klines):
    """
    Devuelve listas de highs y lows a partir de klines.
    """
    if not klines:
        return [], []
    if isinstance(klines[0], dict):
        highs = [float(k["high"]) for k in klines]
        lows = [float(k["low"]) for k in klines]
    else:
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
    return highs, lows


def _pivot_extremos(highs: List[float], lows: List[float]):
    """
    Detecta pivots simples (máximos y mínimos locales).
    Devuelve listas de índices de pivots high y low.
    """
    pivots_high = []
    pivots_low = []
    n = len(highs)
    if n < 3:
        return pivots_high, pivots_low

    for i in range(1, n - 1):
        if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
            pivots_high.append(i)
        if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
            pivots_low.append(i)
    return pivots_high, pivots_low


# ============================================================
# 🧩 ESTRUCTURA HH/HL vs LH/LL (modo "swing")
# ============================================================

def detectar_estructura_simple(klines, lookback: int = 80):
    """
    Lee la estructura reciente con pivots HH/HL vs LH/LL.
    Retorna:
      {
        "estado": "alcista|bajista|rango|sin_datos",
        "ultimo_high": float | None,
        "ultimo_low": float | None,
        "high_anterior": float | None,
        "low_anterior": float | None,
      }
    """
    try:
        if not klines or len(klines) < 10:
            return {
                "estado": "sin_datos",
                "ultimo_high": None,
                "ultimo_low": None,
                "high_anterior": None,
                "low_anterior": None,
            }

        data = klines[-lookback:] if len(klines) >= lookback else klines
        highs, lows = _extraer_hl(data)
        if len(highs) < 3:
            return {
                "estado": "sin_datos",
                "ultimo_high": None,
                "ultimo_low": None,
                "high_anterior": None,
                "low_anterior": None,
            }

        pivots_high, pivots_low = _pivot_extremos(highs, lows)

        # Si no hay suficientes pivots, tratamos como rango suave
        if len(pivots_high) < 2 or len(pivots_low) < 2:
            ultimo_high = max(highs)
            ultimo_low = min(lows)
            return {
                "estado": "rango",
                "ultimo_high": round(ultimo_high, 2),
                "ultimo_low": round(ultimo_low, 2),
                "high_anterior": None,
                "low_anterior": None,
            }

        # Tomamos los dos últimos pivots de cada tipo
        ph1, ph2 = pivots_high[-2], pivots_high[-1]
        pl1, pl2 = pivots_low[-2], pivots_low[-1]

        h1, h2 = highs[ph1], highs[ph2]
        l1, l2 = lows[pl1], lows[pl2]

        if h2 > h1 and l2 > l1:
            estado = "alcista"
        elif h2 < h1 and l2 < l1:
            estado = "bajista"
        else:
            estado = "rango"

        ultimo_high = max(highs)
        ultimo_low = min(lows)

        return {
            "estado": estado,
            "ultimo_high": round(ultimo_high, 2),
            "ultimo_low": round(ultimo_low, 2),
            "high_anterior": round(h1, 2),
            "low_anterior": round(l1, 2),
        }
    except Exception:
        return {
            "estado": "sin_datos",
            "ultimo_high": None,
            "ultimo_low": None,
            "high_anterior": None,
            "low_anterior": None,
        }


# ============================================================
# 🧩 ESTRUCTURA "MA" (respaldo) + RANGO
# ============================================================

def evaluar_estructura(klines):
    """
    Heurística estructural TESLABTC:
      1) Usa pivots HH/HL vs LH/LL para definir tendencia principal.
      2) Si no hay pivots claros, cae a MA(10) vs MA(30) como respaldo.
      3) Devuelve también el rango operativo (high/low últimos 40 candles).

    Retorna:
      {
        "estado": "alcista|bajista|rango|sin_datos",
        "high": float | None,
        "low": float | None,
        "estado_operativo": str (opcional),
        "comentario": str (opcional)
      }
    """
    if not klines or len(klines) < 25:
        return {"estado": "sin_datos", "high": None, "low": None}

    closes = _closes(klines)
    if len(closes) < 25:
        return {"estado": "sin_datos", "high": None, "low": None}

    # Rango operativo real
    hi, lo = _swing_zone(klines, 40)

    # 1) Intentamos leer estructura por swings (pivots)
    simple = detectar_estructura_simple(klines, lookback=80)
    estado = simple.get("estado", "sin_datos")

    # 2) Si no hay estructura clara por swings, usamos MA(10) vs MA(30)
    if estado in ("sin_datos", "rango"):
        ma_fast = mean(closes[-10:])
        ma_slow = mean(closes[-30:]) if len(closes) >= 30 else mean(closes[:-5] or closes)
        last = closes[-1]

        if hi and lo and hi > lo:
            width_pct = (hi - lo) / ((hi + lo) / 2)
            if width_pct < 0.003:  # rango muy estrecho < 0.3 %
                estado = "rango"
            else:
                if ma_fast > ma_slow and last > ma_slow:
                    estado = "alcista"
                elif ma_fast < ma_slow and last < ma_slow:
                    estado = "bajista"
                else:
                    if estado == "sin_datos":
                        estado = "rango"
        else:
            if estado == "sin_datos":
                estado = "rango"

    resultado = {"estado": estado, "high": hi, "low": lo}

    # Marcamos estado PRE-BOS cuando hay dirección clara
    if estado in ("alcista", "bajista") and hi and lo:
        resultado["estado_operativo"] = "🕐 PRE-BOS (esperando confirmación M5)"
        resultado["comentario"] = (
            "Estructura direccional detectada. "
            "Esperar BOS en la temporalidad de ejecución para validar entrada."
        )

    return resultado


# ============================================================
# 🧩 DEFINICIÓN DE ESCENARIOS (texto)
# ============================================================

def definir_escenarios(estados: Dict[str, str]) -> Dict[str, str]:
    """
    estados = {"H4": "alcista|bajista|rango|sin_datos", "H1": ..., "M15": ...}
    Devuelve un bloque descriptivo del escenario conservador / scalping / rango.
    """
    h4 = estados.get("H4", "sin_datos")
    h1 = estados.get("H1", "sin_datos")
    m15 = estados.get("M15", "sin_datos")

    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR (BUY A+)",
            "nivel": "Direccional principal",
            "acción": "Esperar retroceso a zona H1/M15 y gatillo BOS M5 para ejecución.",
            "gestión": "SL en invalidación; TP piscinas de liquidez (RRR ≥ 1:3).",
            "mensaje": "Estructura macro e intradía alineadas al alza.",
        }

    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR (SELL A+)",
            "nivel": "Direccional principal",
            "acción": "Esperar retroceso a zona H1/M15 y gatillo BOS M5 para ejecución.",
            "gestión": "SL en invalidación; TP piscinas de liquidez (RRR ≥ 1:3).",
            "mensaje": "Estructura macro e intradía alineadas a la baja.",
        }

    if (h1 in ("alcista", "bajista")) and h4 != h1:
        sentido = "BUY (contra macro)" if h1 == "alcista" else "SELL (contra macro)"
        return {
            "escenario": f"SCALPING {sentido}",
            "nivel": "Agresivo / riesgo controlado",
            "acción": "Solo si hay reacción clara M15 y micro-BOS M5 dentro de la zona.",
            "gestión": "Objetivo corto (1:1 – 1:2). Reducir tamaño y confirmar.",
            "mensaje": "Operación contra la macro; prioridad siempre a la dirección H4.",
        }

    return {
        "escenario": "SIN CONFIRMACIÓN",
        "nivel": "Neutro / Observación",
        "acción": "Esperar ruptura limpia (BOS/CHOCH) en H1/M15 antes de ejecutar.",
        "gestión": "Evitar operar sin gatillo validado.",
        "mensaje": "Estructuras no alineadas o datos insuficientes.",
    }


# ============================================================
# 🔍 DETECCIÓN DE BOS
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

        chunk = klines[-20:]
        if isinstance(chunk[0], dict):
            closes = [float(k["close"]) for k in chunk]
            highs = [float(k["high"]) for k in chunk]
            lows = [float(k["low"]) for k in chunk]
        else:
            closes = [float(k[4]) for k in chunk]
            highs = [float(k[2]) for k in chunk]
            lows = [float(k[3]) for k in chunk]

        last_close = closes[-1]
        prev_high = max(highs[:-1])
        prev_low = min(lows[:-1])

        if last_close > prev_high:
            return {"bos": True, "tipo": "alcista"}
        if last_close < prev_low:
            return {"bos": True, "tipo": "bajista"}
        return {"bos": False, "tipo": None}
    except Exception:
        return {"bos": False, "tipo": None}


# ============================================================
# 🔍 DETECCIÓN SIMPLE DE ORDER BLOCK
# ============================================================

def detectar_ob(klines):
    """
    Detecta un Order Block simple:
    - Busca la última vela con cuerpo grande y dirección opuesta al impulso actual.
    Retorna: {"ob": True/False, "tipo": "oferta"/"demanda"/None}
    """
    try:
        if not klines or len(klines) < 10:
            return {"ob": False, "tipo": None}

        data = klines[-30:]
        if isinstance(data[0], dict):
            bodies = [abs(float(k["close"]) - float(k["open"])) for k in data]
        else:
            bodies = [abs(float(k[4]) - float(k[1])) for k in data]

        avg_body = sum(bodies) / len(bodies)
        threshold = avg_body * 1.5

        for k in reversed(data[-15:]):
            if isinstance(k, dict):
                o, c = float(k["open"]), float(k["close"])
            else:
                o, c = float(k[1]), float(k[4])
            body_size = abs(c - o)
            if body_size > threshold:
                tipo = "demanda" if c > o else "oferta"
                return {"ob": True, "tipo": tipo}

        return {"ob": False, "tipo": None}
    except Exception:
        return {"ob": False, "tipo": None}


# ============================================================
# 💬 CONTEXTO AUTO (no crítico, pero útil si lo usas)
# ============================================================

def generar_contexto_auto(
    tendencia: str,
    bos_tipo: Optional[str] = None,
    ob_tipo: Optional[str] = None,
    sesion_activa: bool = True,
) -> str:
    """
    Genera un contexto narrativo según estado estructural.
    """
    frases = []

    if tendencia == "bajista":
        frases += [
            "El precio mantiene una estructura bajista clara con presión de venta institucional.",
            "Mercado dominado por vendedores; posible continuidad hacia mínimos anteriores.",
            "La estructura sigue siendo bajista, con liquidez limpia pendiente por debajo del PDL.",
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
    elif tendencia == "alcista":
        frases += [
            "El mercado mantiene estructura alcista y los compradores controlan el impulso.",
            "Se consolida una tendencia alcista estable con mínimos ascendentes.",
            "Presión alcista sostenida tras mitigación de zona de demanda clave.",
        ]
        if bos_tipo == "alcista":
            frases += [
                "BOS alcista reciente; los compradores recuperan el control del movimiento.",
                "Confirmación de ruptura al alza que valida continuidad hacia niveles superiores.",
            ]
        if ob_tipo == "demanda":
            frases += [
                "Reacción positiva en OB de demanda, validando absorción de liquidez bajista.",
                "Zona de demanda respetada con buen volumen; continuidad esperada.",
            ]
    else:
        frases += [
            "Mercado lateral; sin claridad direccional hasta ruptura limpia.",
            "Estructura neutral entre oferta y demanda; preferible esperar confirmaciones.",
            "Consolidación sin dirección definida; se sugiere paciencia operativa.",
        ]

    if sesion_activa:
        frases += [
            "La sesión de Nueva York está activa, incrementando la volatilidad esperada.",
            "Sesión NY abierta; posibles manipulaciones antes del movimiento real.",
        ]
    else:
        frases += [
            "Fuera de la sesión NY, el volumen institucional se mantiene reducido.",
            "El mercado opera con menor impulso fuera de la sesión de Nueva York.",
        ]

    try:
        return random.choice(frases)
    except Exception:
        return "Contexto general no disponible."
