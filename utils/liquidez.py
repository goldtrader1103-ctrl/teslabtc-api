# ============================================================
# utils/liquidez.py — PDH/PDL + ASIAN High/Low básicos
# ============================================================
from typing import List, Dict, Optional

def _max_min(vals):
    return (max(vals) if vals else None, min(vals) if vals else None)

def niveles_liquidez_horas(klines_1h: List[Dict]) -> Dict:
    """
    PDH/PDL últimas 24h con velas 1h.
    """
    if not klines_1h: 
        return {"PDH": None, "PDL": None}
    highs = [float(k["high"]) for k in klines_1h[-24:]]
    lows  = [float(k["low"])  for k in klines_1h[-24:]]
    return {"PDH": max(highs) if highs else None, "PDL": min(lows) if lows else None}

def asian_range(klines_15m: List[Dict]) -> Dict:
    """
    Rango asiático aproximado: tomamos últimas 32 velas de M15 (~8h).
    """
    if not klines_15m: 
        return {"ASIAN_HIGH": None, "ASIAN_LOW": None}
    highs = [float(k["high"]) for k in klines_15m[-32:]]
    lows  = [float(k["low"])  for k in klines_15m[-32:]]
    return {"ASIAN_HIGH": max(highs) if highs else None, "ASIAN_LOW": min(lows) if lows else None}
