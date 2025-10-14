# ============================================================
# 📈 DETECCIÓN DE ESTRUCTURA DE MERCADO – TESLABTC.KG
# ============================================================

from datetime import datetime, timezone, timedelta

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔹 FUNCIÓN PRINCIPAL
# ============================================================

def detectar_estructura(velas: list[dict]) -> dict:
    """
    Detecta estructura de mercado (alcista, bajista o rango)
    usando máximos/mínimos y rupturas significativas.
    """
    if not velas or len(velas) < 20:
        return {"estado": "sin_datos"}

    highs = [v["high"] for v in velas[-50:]]
    lows = [v["low"] for v in velas[-50:]]
    closes = [v["close"] for v in velas[-50:]]

    hh = hl = lh = ll = None
    tendencia = None

    # --- Identificar últimos puntos estructurales ---
    for i in range(2, len(highs)-2):
        if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            hh = highs[i]
        if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
            ll = lows[i]

    if hh and ll:
        rango = hh - ll
        mid = ll + rango / 2
        precio_actual = closes[-1]

        # --- Determinar sesgo estructural ---
        if precio_actual > mid and closes[-1] > closes[-2]:
            tendencia = "alcista"
        elif precio_actual < mid and closes[-1] < closes[-2]:
            tendencia = "bajista"
        else:
            tendencia = "rango"

        # --- Detectar posible BOS / CHoCH ---
        cambio = None
        if closes[-1] > hh:
            cambio = "BOS alcista"
            tendencia = "alcista"
        elif closes[-1] < ll:
            cambio = "BOS bajista"
            tendencia = "bajista"
        elif (closes[-3] > closes[-2] and closes[-1] < closes[-2]):
            cambio = "CHoCH bajista"
            tendencia = "bajista"
        elif (closes[-3] < closes[-2] and closes[-1] > closes[-2]):
            cambio = "CHoCH alcista"
            tendencia = "alcista"

        return {
            "estado": tendencia,
            "HH": round(hh, 2),
            "LL": round(ll, 2),
            "BOS_CHoCH": cambio or "sin_confirmar"
        }

    return {"estado": "rango"}

# ============================================================
# 🔸 FUNCIÓN EXTENDIDA (ANÁLISIS MULTITEMPORAL)
# ============================================================

def evaluar_estructura_multitemporal(velas_H4, velas_H1, velas_M15):
    """
    Analiza estructura macro (H4), intradía (H1) y reacción (M15)
    devolviendo direccionalidad y zonas de reacción.
    """
    E_H4 = detectar_estructura(velas_H4)
    E_H1 = detectar_estructura(velas_H1)
    E_M15 = detectar_estructura(velas_M15)

    estructura = {
        "H4": E_H4.get("estado", "sin_datos"),
        "H1": E_H1.get("estado", "sin_datos"),
        "M15": E_M15.get("estado", "sin_datos")
    }

    zonas = {
        "ZONA H4": {"High": E_H4.get("HH"), "Low": E_H4.get("LL")},
        "ZONA H1": {"High": E_H1.get("HH"), "Low": E_H1.get("LL")},
        "ZONA M15": {"High": E_M15.get("HH"), "Low": E_M15.get("LL")}
    }

    # --- Evaluación global ---
    if estructura["H4"] == estructura["H1"]:
        sesgo = f"Principal {estructura['H1']}"
    elif estructura["H1"] == estructura["M15"]:
        sesgo = f"Intradía {estructura['H1']}"
    else:
        sesgo = "Rango / Transición"

    return {
        "estructura": estructura,
        "zonas": zonas,
        "sesgo_general": sesgo
    }

# ============================================================
# 🧪 TEST LOCAL
# ============================================================

if __name__ == "__main__":
    # Solo para depuración local
    import json
    ejemplo = [{"high": i+1, "low": i, "close": i+0.5} for i in range(60)]
    print(json.dumps(detectar_estructura(ejemplo), indent=2))
