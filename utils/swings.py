# ============================================================
# utils/swings.py — Detección de swings (fractal) HH/HL/LH/LL
# ============================================================
from typing import List, Dict

def _is_pivot_high(kl, i: int, depth: int) -> bool:
    h = kl[i]["high"]
    for j in range(1, depth + 1):
        if i-j < 0 or i+j >= len(kl): return False
        if kl[i-j]["high"] >= h or kl[i+j]["high"] > h: return False
    return True

def _is_pivot_low(kl, i: int, depth: int) -> bool:
    l = kl[i]["low"]
    for j in range(1, depth + 1):
        if i-j < 0 or i+j >= len(kl): return False
        if kl[i-j]["low"] <= l or kl[i+j]["low"] < l: return False
    return True

def detectar_swings(klines: List[Dict], depth: int = 3, max_points: int = 30) -> List[Dict]:
    """
    Devuelve lista de swings: [{"i": idx, "type": "H|L", "price": float}]
    depth=3 suele ir bien para H1/M15; usa 4-5 para H4 si deseas.
    """
    if not klines or len(klines) < depth * 2 + 1:
        return []
    out = []
    for i in range(depth, len(klines) - depth):
        if _is_pivot_high(klines, i, depth):
            out.append({"i": i, "type": "H", "price": float(klines[i]["high"])})
        elif _is_pivot_low(klines, i, depth):
            out.append({"i": i, "type": "L", "price": float(klines[i]["low"])})
    # Mantener últimos puntos relevantes
    return out[-max_points:]
