# ============================================================
# 🧠 DETECCIÓN DE ESTRUCTURA DE MERCADO — TESLABTC.KG
# ============================================================

from utils.price_utils import obtener_alto_bajo

def detectar_estructura(klines):
    """
    Detecta la estructura de mercado (HH, HL, LH, LL) en base a los altos y bajos de las velas.
    Devuelve un dict con el último swing alto, swing bajo y dirección estimada.
    """
    if not klines or len(klines) < 3:
        return {"direccion": "lateral", "ultimo_alto": None, "ultimo_bajo": None}

    altos = [float(k["high"]) for k in klines]
    bajos = [float(k["low"]) for k in klines]

    ultimo_alto = max(altos[-10:]) if len(altos) >= 10 else max(altos)
    ultimo_bajo = min(bajos[-10:]) if len(bajos) >= 10 else min(bajos)

    if altos[-1] > altos[-2] and bajos[-1] > bajos[-2]:
        direccion = "alcista"
    elif altos[-1] < altos[-2] and bajos[-1] < bajos[-2]:
        direccion = "bajista"
    else:
        direccion = "lateral"

    return {
        "direccion": direccion,
        "ultimo_alto": round(ultimo_alto, 2),
        "ultimo_bajo": round(ultimo_bajo, 2)
    }
# ============================================================
# 📊 DETECCIÓN DE ESTRUCTURA DE MERCADO — TESLABTC.KG
# ============================================================

from utils.price_utils import obtener_alto_bajo

def detectar_estructura(klines):
    """
    Detecta la estructura de mercado (HH, HL, LH, LL) a partir de los altos y bajos recientes.
    Retorna dirección, último alto, último bajo y una breve descripción.
    """
    if not klines or len(klines) < 3:
        return {"direccion": "lateral", "ultimo_alto": None, "ultimo_bajo": None, "descripcion": "Sin datos suficientes"}

    altos = [float(k["high"]) for k in klines]
    bajos = [float(k["low"]) for k in klines]

    ultimo_alto = max(altos[-10:]) if len(altos) >= 10 else max(altos)
    ultimo_bajo = min(bajos[-10:]) if len(bajos) >= 10 else min(bajos)

    if altos[-1] > altos[-2] and bajos[-1] > bajos[-2]:
        direccion = "alcista"
        descripcion = "Estructura con altos y bajos ascendentes (HH–HL)."
    elif altos[-1] < altos[-2] and bajos[-1] < bajos[-2]:
        direccion = "bajista"
        descripcion = "Estructura con altos y bajos descendentes (LH–LL)."
    else:
        direccion = "lateral"
        descripcion = "Rango consolidado sin dirección clara."

    return {
        "direccion": direccion,
        "ultimo_alto": round(ultimo_alto, 2),
        "ultimo_bajo": round(ultimo_bajo, 2),
        "descripcion": descripcion
    }
