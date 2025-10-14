# ============================================================
# 🧠 DETECTOR ESTRUCTURAL TESLABTC.KG
# ============================================================

from datetime import datetime, timezone, timedelta
from statistics import mean

TZ_COL = timezone(timedelta(hours=-5))

# ------------------------------------------------------------
# 🔍 FUNCIÓN BASE PARA LEER ESTRUCTURA SIMPLE
# ------------------------------------------------------------
def _estructura_basica(velas):
    if not velas or len(velas) < 20:
        return {"estructura": "sin_datos", "zona": None}
    closes = [v["close"] for v in velas[-40:]]
    highs = [v["high"] for v in velas[-40:]]
    lows = [v["low"] for v in velas[-40:]]

    # Tendencia por máximos y mínimos
    if highs[-1] > max(highs[:-5]) and lows[-1] > mean(lows[:-5]):
        estructura = "alcista"
    elif lows[-1] < min(lows[:-5]) and highs[-1] < mean(highs[:-5]):
        estructura = "bajista"
    else:
        estructura = "rango"

    zona = {
        "High": round(max(highs[-10:]), 2),
        "Low": round(min(lows[-10:]), 2)
    }
    return {"estructura": estructura, "zona": zona}


# ------------------------------------------------------------
# 🧩 ANALIZAR ESTRUCTURA MULTINIVEL
# ------------------------------------------------------------
def analizar_estructura_multinivel(velas_h4, velas_h1, velas_m15):
    """
    Devuelve estructura macro (H4), intradía (H1) y reacción (M15)
    con sus zonas reales (rangos de precios)
    """
    h4 = _estructura_basica(velas_h4)
    h1 = _estructura_basica(velas_h1)
    m15 = _estructura_basica(velas_m15)

    return {
        "H4": h4["estructura"],
        "H1": h1["estructura"],
        "M15": m15["estructura"],
        "zonas": {
            "H4": h4["zona"],
            "H1": h1["zona"],
            "M15": m15["zona"]
        }
    }


# ------------------------------------------------------------
# 🎯 DETERMINAR ESCENARIO DE OPERACIÓN
# ------------------------------------------------------------
def determinar_escenario(estructura):
    h4 = estructura["H4"]
    h1 = estructura["H1"]
    m15 = estructura["M15"]

    # Escenario conservador 1 – alineación total
    if h4 == h1 == m15 and h1 in ["alcista", "bajista"]:
        tipo = "CONSERVADOR 1"
        nivel = "Institucional (direccional principal)"
        razon = f"H4, H1 y M15 alineados {h1.upper()}."
        accion = f"Operar BOS M5 en dirección {h1.upper()} dentro del POI M15."
        objetivo = "Objetivo: 1:3 o más, priorizando estructuras limpias."
    # Escenario conservador 2 – reentrada o continuación
    elif h4 == h1 and m15 != h1:
        tipo = "CONSERVADOR 2"
        nivel = "Reentrada / Mitigación"
        razon = f"H4 y H1 alineados {h1.upper()}, pero M15 en retroceso."
        accion = f"Esperar confirmación BOS M5 a favor de H1 para reentrada."
        objetivo = "Objetivo: 1:2 o 1:3, dependiendo de liquidez pendiente."
    # Escenario scalping – contra tendencia
    else:
        tipo = "SCALPING"
        nivel = "Contratendencia (riesgo alto)"
        razon = f"H1 y H4 opuestos ({h4.upper()} vs {h1.upper()})."
        accion = "Buscar BOS M5-M3 dentro del POI M15 con gestión estricta."
        objetivo = "Objetivo: 1:1 o 1:2 máximo, controlando exposición."

    return {
        "escenario": tipo,
        "nivel": nivel,
        "razon": razon,
        "accion": f"{accion}\n💡 {objetivo}\n⚖️ La gestión del riesgo es la clave de un trader profesional."
    }
