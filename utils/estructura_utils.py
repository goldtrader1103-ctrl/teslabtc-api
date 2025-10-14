# ============================================================
# 🧠 TESLABTC.KG — Estructura y Zonas (H4/H1/M15)
# Acción del Precio Pura (sin volumen / sin fibo)
# ============================================================

from typing import List, Dict, Optional

def _is_swing_high(velas: List[Dict], i: int, lb: int = 2) -> bool:
    if i - lb < 0 or i + lb >= len(velas): 
        return False
    h = velas[i]["high"]
    return all(h > velas[i - k]["high"] and h > velas[i + k]["high"] for k in range(1, lb + 1))

def _is_swing_low(velas: List[Dict], i: int, lb: int = 2) -> bool:
    if i - lb < 0 or i + lb >= len(velas): 
        return False
    l = velas[i]["low"]
    return all(l < velas[i - k]["low"] and l < velas[i + k]["low"] for k in range(1, lb + 1))

def _collect_swings(velas: List[Dict], lb: int = 2, take_last: int = 80):
    highs, lows = [], []
    start = max(0, len(velas) - take_last)
    for i in range(start, len(velas)):
        if _is_swing_high(velas, i, lb): highs.append(i)
        if _is_swing_low(velas, i, lb):  lows.append(i)
    return highs, lows

def _last_bos(velas: List[Dict]) -> Dict:
    highs, lows = _collect_swings(velas, lb=2, take_last=120)
    if len(highs) < 2 and len(lows) < 2:
        return {"dir": "range", "idx_break": None, "idx_ref": None}

    if len(highs) >= 2:
        prev_high = velas[highs[-2]]["high"]
        for j in range(highs[-2]+1, len(velas)):
            if velas[j]["high"] > prev_high:
                return {"dir": "up", "idx_break": j, "idx_ref": highs[-2]}

    if len(lows) >= 2:
        prev_low = velas[lows[-2]]["low"]
        for j in range(lows[-2]+1, len(velas)):
            if velas[j]["low"] < prev_low:
                return {"dir": "down", "idx_break": j, "idx_ref": lows[-2]}

    return {"dir": "range", "idx_break": None, "idx_ref": None}

def _ob_zone_from_candle(c: Dict, kind: str) -> Dict:
    if kind == "demand":
        return {"inferior": round(c["low"], 2), "superior": round(c["open"], 2)}
    else:
        return {"inferior": round(c["open"], 2), "superior": round(c["high"], 2)}

def _find_last_ob(velas: List[Dict], dir_bos: str, idx_break: int) -> Optional[Dict]:
    if idx_break is None or idx_break <= 0:
        return None

    j = idx_break
    ob_list = []
    floor = max(0, idx_break - 60)

    if dir_bos == "up":
        while j > floor:
            j -= 1
            if velas[j]["close"] < velas[j]["open"]:
                ob_list.append(_ob_zone_from_candle(velas[j], "demand"))
                if len(ob_list) == 2:
                    break
    elif dir_bos == "down":
        while j > floor:
            j -= 1
            if velas[j]["close"] > velas[j]["open"]:
                ob_list.append(_ob_zone_from_candle(velas[j], "supply"))
                if len(ob_list) == 2:
                    break

    if not ob_list:
        return None

    zonas = {"zona_1": ob_list[0]}
    if len(ob_list) > 1:
        zonas["zona_2"] = ob_list[1]
    return zonas

def estructura_y_zonas(velas_h4: List[Dict], velas_h1: List[Dict], velas_m15: List[Dict]) -> Dict:
    bos_h4 = _last_bos(velas_h4)
    estado_h4 = "alcista" if bos_h4["dir"] == "up" else ("bajista" if bos_h4["dir"] == "down" else "rango")
    zonas_h4 = _find_last_ob(velas_h4, bos_h4["dir"], bos_h4["idx_break"])
    macro = {"estado": estado_h4, "zonas": zonas_h4 or {}}
    if zonas_h4 and "zona_2" in zonas_h4:
        macro["nota"] = "Si la zona 1 no reacciona, considerar zona 2 como reentrada o SL extendido."

    bos_h1 = _last_bos(velas_h1)
    estado_h1 = "alcista" if bos_h1["dir"] == "up" else ("bajista" if bos_h1["dir"] == "down" else "rango")
    zonas_h1 = _find_last_ob(velas_h1, bos_h1["dir"], bos_h1["idx_break"])
    intradia = {"estado": estado_h1, "zonas": zonas_h1 or {}}
    if zonas_h1 and "zona_2" in zonas_h1:
        intradia["nota"] = "Zona 2 como reentrada si la principal falla."

    reaccion = {}
    if zonas_h1 and "zona_1" in zonas_h1:
        z1 = zonas_h1["zona_1"]
        z_inf, z_sup = z1["inferior"], z1["superior"]
        cand = None
        for c in reversed(velas_m15[-120:]):
            if z_inf <= c["low"] <= z_sup or z_inf <= c["high"] <= z_sup or (c["low"] < z_inf and c["high"] > z_sup):
                if estado_h1 == "alcista" and c["close"] < c["open"]:
                    cand = _ob_zone_from_candle(c, "demand")
                    break
                if estado_h1 == "bajista" and c["close"] > c["open"]:
                    cand = _ob_zone_from_candle(c, "supply")
                    break
        if cand:
            reaccion["zona_1"] = cand

    return {"macro": macro, "intradía": intradia, "reaccion": reaccion}
