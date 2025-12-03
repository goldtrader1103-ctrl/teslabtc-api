# ============================================================
# utils/ob_detector.py — Detección básica de OB válidos TESLABTC
# ============================================================
from typing import List, Dict, Optional

def detectar_ob_valido(klines: List[Dict], direccion: str) -> Optional[Dict]:
    """
    Heurística limpia TESLABTC:

      - Sólo usa las últimas ~50 velas (zona operativa reciente).
      - Busca la vela ORIGEN del impulso que continúa a favor de la dirección:
          • Cuerpo dominante (no doji)
          • Desplazamiento claro en las 3–5 velas siguientes
      - Construye el OB con:
          • Demanda (alcista): [LOW, max(OPEN, CLOSE)]
          • Oferta  (bajista): [min(OPEN, CLOSE), HIGH]
      - Si el rango ya fue MITIGADO (cierres dentro del OB) → se descarta.
    """
    if not klines or len(klines) < 20:
        return None

    if direccion not in ("alcista", "bajista"):
        return None

    # Trabajamos con las últimas 50 velas
    data = klines[-50:]

    idx = None
    # Recorremos hacia atrás desde la parte reciente
    for i in range(len(data) - 6, 3, -1):
        o = float(data[i]["open"])
        c = float(data[i]["close"])
        h = float(data[i]["high"])
        l = float(data[i]["low"])

        rango = abs(h - l)
        cuerpo = abs(c - o)
        if rango <= 0:
            continue

        # Cuerpo dominante (evitar dojis / velas sin intención)
        if cuerpo / rango < 0.55:
            continue

        # Desplazamiento posterior a favor de la dirección
        closes_fut = [float(k["close"]) for k in data[i+1:i+6]]
        if not closes_fut:
            continue

        if direccion == "bajista":
            # Queremos que todas las velas siguientes cierren por
            # DEBAJO del cuerpo de la vela origen
            if all(cf < min(o, c) for cf in closes_fut):
                idx = i
                break
        else:  # direccion == "alcista"
            # Todas las siguientes cierren por ENCIMA del cuerpo
            if all(cf > max(o, c) for cf in closes_fut):
                idx = i
                break

    if idx is None:
        return None

    o = float(data[idx]["open"])
    c = float(data[idx]["close"])
    h = float(data[idx]["high"])
    l = float(data[idx]["low"])

    if direccion == "bajista":
        tipo = "oferta"
        ob_low  = min(o, c)   # base del cuerpo
        ob_high = h           # extremo de la mecha
    else:
        tipo = "demanda"
        ob_low  = l           # extremo de la mecha
        ob_high = max(o, c)   # techo del cuerpo

    rango_ob = (ob_low, ob_high)

    # Mitigación: si cierres posteriores están DENTRO del OB → lo descartamos
    closes_recent = [float(k["close"]) for k in data[idx+1:]]
    mitigado = any(rango_ob[0] <= cr <= rango_ob[1] for cr in closes_recent)
    if mitigado:
        return None

    ob = {
        "tipo": tipo,
        "rango": rango_ob,
        "vela_idx": idx,
        "mitigado": False,
    }
    return ob
