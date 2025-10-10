def detectar_bos(data: List[Dict], base_lookback: int = 20) -> Dict:
    """
    TESLABTC A.P. v2.1 — Detección avanzada de BOS y flujo direccional.
    
    Combina:
      - BOS clásico (ruptura de extremos previos)
      - Flujo direccional (pendiente de swing y momentum)
      - Ajuste dinámico del lookback según volatilidad
    """

    if len(data) < base_lookback + 5:
        return {
            "BOS": False,
            "tipo_BOS": None,
            "rango": True,
            "flujo": None,
            "barrida_alcista": False,
            "barrida_bajista": False
        }

    closes = [x["close"] for x in data]
    highs = [x["high"] for x in data]
    lows = [x["low"] for x in data]

    # ====== Volatilidad dinámica ======
    avg_range = sum((h - l) for h, l in zip(highs[-base_lookback:], lows[-base_lookback:])) / base_lookback
    volatilidad_alta = avg_range > (sum(highs[-base_lookback:]) / base_lookback) * 0.004  # 0.4 %
    lookback = 10 if volatilidad_alta else base_lookback

    # ====== Estructura previa ======
    prev_max = max(highs[-(lookback + 1):-1])
    prev_min = min(lows[-(lookback + 1):-1])
    close_actual = closes[-1]
    high_actual = highs[-1]
    low_actual = lows[-1]

    bos_up = close_actual > prev_max
    bos_dn = close_actual < prev_min

    # ====== Barridas ======
    sweep_up = high_actual > prev_max and not bos_up
    sweep_dn = low_actual < prev_min and not bos_dn

    # ====== Flujo direccional (momentum) ======
    sub = closes[-5:]
    tendencia_alcista = all(sub[i] < sub[i + 1] for i in range(4))
    tendencia_bajista = all(sub[i] > sub[i + 1] for i in range(4))

    flujo = None
    if tendencia_alcista:
        flujo = "alcista"
    elif tendencia_bajista:
        flujo = "bajista"

    # ====== Swing progressivo ======
    swing_alcista = highs[-1] > highs[-2] > highs[-3] and lows[-1] > lows[-2] > lows[-3]
    swing_bajista = highs[-1] < highs[-2] < highs[-3] and lows[-1] < lows[-2] < lows[-3]

    # ====== Resultado final ======
    return {
        "BOS": bool(bos_up or bos_dn),
        "tipo_BOS": "alcista" if bos_up else "bajista" if bos_dn else None,
        "rango": not (bos_up or bos_dn or swing_alcista or swing_bajista),
        "flujo": flujo,
        "swing_alcista": swing_alcista,
        "swing_bajista": swing_bajista,
        "barrida_alcista": sweep_up,
        "barrida_bajista": sweep_dn,
        "prev_max": prev_max,
        "prev_min": prev_min,
    }
