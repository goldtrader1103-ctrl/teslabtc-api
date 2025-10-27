# ============================================================
# utils/ob_detector.py — Detección básica de OB válidos
# ============================================================
from typing import List, Dict, Optional

def detectar_ob_valido(klines: List[Dict], direccion: str) -> Optional[Dict]:
    """
    Heurística limpia:
      - Busca vela origen del impulso que rompió el último swing (cuerpo dominante)
      - Debe dejar desplazamiento claro (cierre lejos) y preferible FVG posterior
      - Filtra OB ya mitigados (precio volvió y cerró dentro)
    """
    if not klines or len(klines) < 20:
        return None

    # Tomamos últimos 50 candles
    data = klines[-50:]
    # Busca vela con cuerpo grande previa a un tramo tendencial
    idx = None
    for i in range(len(data)-6, 3, -1):  # hacia atrás
        o = float(data[i]["open"]); c = float(data[i]["close"])
        h = float(data[i]["high"]); l = float(data[i]["low"])
        rango = abs(h - l)
        cuerpo = abs(c - o)
        if rango <= 0: 
            continue
        if cuerpo / rango < 0.55:  # cuerpo dominante (simplificación)
            continue
        # Confirmar desplazamiento posterior:
        closes_fut = [float(k["close"]) for k in data[i+1:i+6]]
        if not closes_fut: 
            continue
        if direccion == "bajista" and all(cf < min(o,c) for cf in closes_fut):
            idx = i; break
        if direccion == "alcista" and all(cf > max(o,c) for cf in closes_fut):
            idx = i; break

    if idx is None: 
        return None

    o = float(data[idx]["open"]); c = float(data[idx]["close"])
    h = float(data[idx]["high"]); l = float(data[idx]["low"])

    ob = {"tipo": "oferta" if direccion=="bajista" else "demanda",
          "rango": (min(o, c), max(o, c)),
          "vela_idx": idx}

    # Mitigación simple: si cierres recientes están dentro del rango -> mitigado
    closes_recent = [float(k["close"]) for k in data[idx+1:]]
    if any(ob["rango"][0] <= cr <= ob["rango"][1] for cr in closes_recent):
        ob["mitigado"] = True
    else:
        ob["mitigado"] = False

    return ob
