# ============================================================
# utils/setup_detector.py — Validación de setup TESLABTC
# ============================================================
from typing import Dict, List, Optional

def _near(price: float, level: Optional[float], tol: float = 0.0015) -> bool:
    """
    Proximidad porcentual a un nivel (0.15% por defecto).
    Si level es None, retorna False.
    """
    if level is None:
        return False
    if price <= 0:
        return False
    return abs(price - level) / price <= tol

def validar_setup_tesla(
    precio_actual: float,
    tend_h1: str,
    tend_m15: str,
    bos_m15: Dict,
    bos_m5: Dict,
    ob_h1: Optional[Dict],
    liq_horas: Dict,       # {"PDH": float, "PDL": float, ...}
    asia: Dict,            # {"ASIAN_HIGH": float, "ASIAN_LOW": float}
    min_confirmaciones: int = 3
) -> Dict:
    """
    Determina si hay SETUP válido TESLABTC.
    Reglas:
      - Debe existir BOS (en M15 o M5) como gatillo.
      - Debe haber >= min_confirmaciones entre: barrida de liquidez (PDH/PDL/AH/AL),
        OB/POI/fuente (oferta/demanda H1 fuerte), FVG (pendiente si lo integras),
        a favor de tendencia intradía H1, retroceso profundo (placeholder simple).
    Retorna dict con campos para imprimir en el bot.
    """

    confirmaciones: List[str] = []

    # 1) BOS gatillo
    bos15 = bos_m15.get("BOS") if bos_m15 else None
    bos5  = bos_m5.get("BOS")  if bos_m5  else None
    tiene_bos = bos15 or bos5
    if bos15:
        confirmaciones.append(f"BOS M15 ({bos15.get('tipo','?')})")
    if bos5:
        confirmaciones.append(f"BOS M5 ({bos5.get('tipo','?')})")

    # 2) Barridas de liquidez (PDH/PDL y Asia H/L) cercanas al precio
    pdh = liq_horas.get("PDH")
    pdl = liq_horas.get("PDL")
    ah  = asia.get("ASIAN_HIGH")
    al  = asia.get("ASIAN_LOW")

    if _near(precio_actual, pdh) or (pdh is not None and precio_actual > pdh):
        confirmaciones.append("Barrida/ataque PDH")
    if _near(precio_actual, pdl) or (pdl is not None and precio_actual < pdl):
        confirmaciones.append("Barrida/ataque PDL")
    if _near(precio_actual, ah) or (ah is not None and precio_actual > ah):
        confirmaciones.append("Barrida/ataque ASIAN HIGH")
    if _near(precio_actual, al) or (al is not None and precio_actual < al):
        confirmaciones.append("Barrida/ataque ASIAN LOW")

    # 3) Zona H1 (Oferta/Demanda fuerte sin mitigar de forma obvia)
    if ob_h1:
        if ob_h1.get("tipo") == "oferta" and not ob_h1.get("mitigado", False):
            confirmaciones.append("Oferta H1 fuerte (OB)")
        if ob_h1.get("tipo") == "demanda" and not ob_h1.get("mitigado", False):
            confirmaciones.append("Demanda H1 fuerte (OB)")

    # 4) A favor de tendencia intradía (H1)
    if tend_h1 == "alcista":
        confirmaciones.append("A favor de tendencia intradía H1 (alcista)")
    elif tend_h1 == "bajista":
        confirmaciones.append("A favor de tendencia intradía H1 (bajista)")

    # 5) Retroceso profundo (placeholder simple):
    #    Si existe OB y el precio está cerca del borde interno del OB
    if ob_h1 and isinstance(ob_h1.get("rango"), (list, tuple)) and len(ob_h1["rango"]) == 2:
        a, b = ob_h1["rango"]
        # borde interno = para oferta usar el límite superior; para demanda, el inferior
        borde = max(a, b) if ob_h1["tipo"] == "oferta" else min(a, b)
        if _near(precio_actual, borde):
            confirmaciones.append("Retroceso profundo en borde de OB")

    # ¿BUY o SELL?
    #   Usamos el BOS dominante: si hay M15 lo priorizamos, si no el de M5.
    bos_dominante = bos15 or bos5
    tipo = None
    if bos_dominante:
        bos_tipo = bos_dominante.get("tipo")
        tipo = "BUY" if bos_tipo == "alcista" else "SELL" if bos_tipo == "bajista" else None

    setup_valido = bool(tiene_bos and len([c for c in confirmaciones if c]) >= min_confirmaciones)

    # Niveles de ejecución (solo si setup válido y existe OB base)
    entrada = tp1 = tp2 = tp3 = sl = None
    if setup_valido and ob_h1 and isinstance(ob_h1.get("rango"), (list, tuple)) and len(ob_h1["rango"]) == 2:
        lo, hi = min(ob_h1["rango"]), max(ob_h1["rango"])
        if tipo == "SELL":
            # entrada alta del OB (oferta); SL por encima del OB
            entrada = hi
            sl = hi * 1.003  # 0.3% por encima (ajústalo a tu gestión real)
            tp1 = pdl or al
            tp2 = al or pdl
            # tp3 swing (extensión simple si hay ambos)
            if tp1 and tp2:
                tp3 = tp2 - (tp1 - tp2)
        elif tipo == "BUY":
            # entrada baja del OB (demanda); SL por debajo del OB
            entrada = lo
            sl = lo * 0.997  # 0.3% por debajo
            tp1 = pdh or ah
            tp2 = ah or pdh
            if tp1 and tp2:
                tp3 = tp2 + (tp2 - tp1)

    return {
        "setup_valido": setup_valido,
        "tipo": tipo,
        "confirmaciones": confirmaciones,
        "entrada": entrada,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "sl": sl
    }
