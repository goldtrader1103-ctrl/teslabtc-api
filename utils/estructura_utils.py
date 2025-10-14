# ============================================================
# 🧠 TESLABTC.KG — Estructura y Zonas (H4/H1/M15)
# Acción del Precio Pura (sin volumen / sin fibo)
# ============================================================

from typing import List, Dict, Optional

# velas = [{"open": float, "high": float, "low": float, "close": float, "open_time": datetime, ...}, ...]

# ---------- Utilidades de pivotes (swing high/low) ----------

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

# ---------- BOS / Dirección estructural ----------

def _last_bos(velas: List[Dict]) -> Dict:
    """
    Busca el último rompimiento de estructura (BOS) comparando swing highs/lows.
    Devuelve: {"dir": "up"|"down"|"range", "idx_break": int|None, "idx_ref": int|None}
    """
    highs, lows = _collect_swings(velas, lb=2, take_last=120)
    if len(highs) < 2 and len(lows) < 2:
        return {"dir": "range", "idx_break": None, "idx_ref": None}

    # último swing high/low confirmado
    hs = highs[-3:] if len(highs) >= 3 else highs
    ls = lows[-3:] if len(lows) >= 3 else lows

    # ¿rompió el último high?
    if len(hs) >= 2:
        last_high_val = velas[hs[-1]]["high"]
        prev_high_val = velas[hs[-2]]["high"]
        # mirar si alguna vela posterior a prev_high rompió su high
        for j in range(hs[-2]+1, len(velas)):
            if velas[j]["high"] > prev_high_val:
                return {"dir": "up", "idx_break": j, "idx_ref": hs[-2]}

    # ¿rompió el último low?
    if len(ls) >= 2:
        last_low_val = velas[ls[-1]]["low"]
        prev_low_val = velas[ls[-2]]["low"]
        for j in range(ls[-2]+1, len(velas)):
            if velas[j]["low"] < prev_low_val:
                return {"dir": "down", "idx_break": j, "idx_ref": ls[-2]}

    return {"dir": "range", "idx_break": None, "idx_ref": None}

# ---------- Order Block simple (OB) ----------

def _ob_zone_from_candle(c: Dict, kind: str) -> Dict:
    """
    kind = 'demand' (alcista)  -> última vela bajista antes del impulso
    kind = 'supply' (bajista)  -> última vela alcista antes del impulso
    Retorna {inferior, superior}
    """
    if kind == "demand":
        # Zona conservadora: [low, open] de la vela bajista
        return {"inferior": round(c["low"], 2), "superior": round(c["open"], 2)}
    else:  # supply
        # Zona conservadora: [open, high] de la vela alcista
        return {"inferior": round(c["open"], 2), "superior": round(c["high"], 2)}

def _find_last_ob(velas: List[Dict], dir_bos: str, idx_break: int) -> Optional[Dict]:
    """
    Busca la última vela contraria previa al tramo que rompió (OB principal).
    También devuelve una segunda zona candidata (OB anterior) si existe.
    """
    if idx_break is None or idx_break <= 0:
        return None

    # retroceder desde el rompimiento para encontrar el tramo impulsivo
    j = idx_break
    ob_list = []
    # límite de retroceso para no irse muy atrás
    floor = max(0, idx_break - 60)

    if dir_bos == "up":  # demanda: última vela bajista antes del impulso
        while j > floor:
            j -= 1
            if velas[j]["close"] < velas[j]["open"]:  # vela bajista
                ob_list.append(_ob_zone_from_candle(velas[j], "demand"))
                if len(ob_list) == 2:  # principal + secundaria
                    break
    elif dir_bos == "down":  # oferta: última vela alcista antes del impulso
        while j > floor:
            j -= 1
            if velas[j]["close"] > velas[j]["open"]:  # vela alcista
                ob_list.append(_ob_zone_from_candle(velas[j], "supply"))
                if len(ob_list) == 2:
                    break

    if not ob_list:
        return None

    zonas = {"zona_1": ob_list[0]}
    if len(ob_list) > 1:
        zonas["zona_2"] = ob_list[1]
    return zonas

# ---------- API de alto nivel para H4/H1/M15 ----------

def estructura_y_zonas(velas_h4: List[Dict], velas_h1: List[Dict], velas_m15: List[Dict]) -> Dict:
    """
    Devuelve:
    {
      "macro": {"estado": "alcista|bajista|rango", "zonas": { "zona_1":{...}, "zona_2":{...}, "nota": str }},
      "intradía": {"estado": "...", "zonas": {...}},
      "reaccion": {"zona_1": {...} }  # refinamiento M15 dentro de H1.zona_1 si existe
    }
    """

    # --- H4 MACRO ---
    bos_h4 = _last_bos(velas_h4)
    estado_h4 = "alcista" if bos_h4["dir"] == "up" else ("bajista" if bos_h4["dir"] == "down" else "rango")
    zonas_h4 = _find_last_ob(velas_h4, bos_h4["dir"], bos_h4["idx_break"])
    macro = {"estado": estado_h4, "zonas": zonas_h4 or {}}
    if zonas_h4 and "zona_2" in zonas_h4:
        macro["nota"] = "Si la zona 1 no reacciona, considerar zona 2 como reentrada o SL extendido."

    # --- H1 INTRADÍA ---
    bos_h1 = _last_bos(velas_h1)
    estado_h1 = "alcista" if bos_h1["dir"] == "up" else ("bajista" if bos_h1["dir"] == "down" else "rango")
    zonas_h1 = _find_last_ob(velas_h1, bos_h1["dir"], bos_h1["idx_break"])
    intradia = {"estado": estado_h1, "zonas": zonas_h1 or {}}
    if zonas_h1 and "zona_2" in zonas_h1:
        intradia["nota"] = "Zona 2 como reentrada si la principal falla."

    # --- M15 REACCIÓN (refinamiento dentro de H1.zona_1 si existe) ---
    reaccion = {}
    if zonas_h1 and "zona_1" in zonas_h1:
        z1 = zonas_h1["zona_1"]
        # buscar en M15 la última vela contraria dentro de esa banda para refinar
        z_inf, z_sup = z1["inferior"], z1["superior"]
        cand = None
        for c in reversed(velas_m15[-120:]):
            if z_inf <= c["low"] <= z_sup or z_inf <= c["high"] <= z_sup or (c["low"] < z_inf and c["high"] > z_sup):
                # elegir vela contraria como POI refinado
                if estado_h1 == "alcista" and c["close"] < c["open"]:
                    cand = _ob_zone_from_candle(c, "demand")
                    break
                if estado_h1 == "bajista" and c["close"] > c["open"]:
                    cand = _ob_zone_from_candle(c, "supply")
                    break
        if cand:
            reaccion["zona_1"] = cand

    return {"macro": macro, "intradia": intradia, "reaccion": reaccion}
