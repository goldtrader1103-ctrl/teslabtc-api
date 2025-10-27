# ============================================================
# utils/bos_choch.py — BOS / CHoCH a partir de swings
# ============================================================
from typing import List, Dict, Optional

def _last_of(swings: List[Dict], t: str) -> Optional[Dict]:
    for s in reversed(swings):
        if s["type"] == t:
            return s
    return None

def tendencia_por_estructura(swings: List[Dict]) -> str:
    """
    Regla simple pero PA real:
      - Si los últimos 3-4 swings muestran HH/HL -> alcista
      - Si muestran LH/LL -> bajista
      - Si alternan -> rango
    """
    if len(swings) < 4: return "sin_datos"
    # Usa últimos 6 swings
    w = swings[-6:]
    # Extrae secuencia de precios con tipo
    seq = [(s["type"], s["price"]) for s in w]
    highs = [p for t,p in seq if t == "H"]
    lows  = [p for t,p in seq if t == "L"]
    if len(highs) >= 2 and len(lows) >= 2:
        # Comparar últimos dos de cada tipo
        HH = highs[-1] > highs[-2]
        HL = lows[-1]  > lows[-2]
        LH = highs[-1] < highs[-2]
        LL = lows[-1]  < lows[-2]
        if HH and HL: return "alcista"
        if LH and LL: return "bajista"
    return "rango"

def detectar_bos_choch(swings: List[Dict], tendencia_actual: str) -> Dict:
    """
    BOS: ruptura del último swing opuesto en dirección de la tendencia propuesta.
    CHoCH: ruptura de swing en contra de la tendencia vigente.
    """
    if len(swings) < 4:
        return {"BOS": None, "CHoCH": None}

    last_H = _last_of(swings, "H")
    last_L = _last_of(swings, "L")
    if not last_H or not last_L:
        return {"BOS": None, "CHoCH": None}

    # Punto de referencia (swing opuesto más reciente antes del último del mismo tipo)
    # Simplificación: comparamos últimos H y L entre sí
    BOS = None
    CHOCH = None

    if tendencia_actual == "alcista":
        # BOS alcista si precio rompió el último H previo
        BOS = {"tipo": "alcista", "nivel": last_H["price"]}
        # CHoCH si rompió el último L (cambio de carácter)
        CHOCH = {"tipo": "bajista", "nivel": last_L["price"]}

    elif tendencia_actual == "bajista":
        BOS = {"tipo": "bajista", "nivel": last_L["price"]}
        CHOCH = {"tipo": "alcista", "nivel": last_H["price"]}

    return {"BOS": BOS, "CHoCH": CHOCH}
