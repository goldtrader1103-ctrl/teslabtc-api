# ============================================================
# 🧠 TESLABTC.KG — Análisis Estructural Real (Multi-TF)
# ============================================================

from utils.price_utils import obtener_klines_binance
from utils.estructura_utils import detectar_bos, detectar_ob
from datetime import datetime

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def analizar_estructura_general(simbolo="BTCUSDT"):
    """
    Analiza estructura D / H4 / H1 + confirma zonas, liquidez y contexto macro.
    Devuelve dict con:
    - estructura_detectada
    - zonas
    - confirmaciones
    - contexto_general
    """

    # ===============================
    # 📊 DATOS MULTITF
    # ===============================
    kl_d = obtener_klines_binance(simbolo, "1d", 300)
    kl_h4 = obtener_klines_binance(simbolo, "4h", 300)
    kl_h1 = obtener_klines_binance(simbolo, "1h", 300)
    kl_m5 = obtener_klines_binance(simbolo, "5m", 300)

    # ===============================
    # 🧭 ESTRUCTURA BÁSICA
    # ===============================
    def estructura_tf(kl):
        if not kl:
            return {"estado": "sin_datos"}

        highs = [float(k["high"]) for k in kl]
        lows = [float(k["low"]) for k in kl]
        close = float(kl[-1]["close"])

        avg_high = sum(highs[-10:]) / 10
        avg_low = sum(lows[-10:]) / 10

        if close > avg_high:
            estado = "alcista"
        elif close < avg_low:
            estado = "bajista"
        else:
            estado = "lateral"

        bos = "✔️" if detectar_bos(kl) else "—"
        return {
            "estado": estado,
            "BOS": bos,
            "HH": max(highs[-60:]),
            "LH": sorted(highs[-60:])[-2],
            "LL": min(lows[-60:]),
            "HL": sorted(lows[-60:])[1],
        }

    e_d = estructura_tf(kl_d)
    e_h4 = estructura_tf(kl_h4)
    e_h1 = estructura_tf(kl_h1)
    estructura = {"D": e_d, "H4": e_h4, "H1": e_h1}

    # ===============================
    # 📍 ZONAS
    # ===============================
    zonas = {
        "PDH": max([float(x["high"]) for x in kl_h1[-96:]]),
        "PDL": min([float(x["low"]) for x in kl_h1[-96:]]),
        "DHIGH": e_d.get("HH"),
        "DLOW": e_d.get("LL"),
        "H4HIGH": e_h4.get("HH"),
        "H4LOW": e_h4.get("LL"),
        "H1HIGH": e_h1.get("HH"),
        "H1LOW": e_h1.get("LL"),
    }

    # ===============================
    # ✅ CONFIRMACIONES
    # ===============================
    precio_actual = float(kl_h1[-1]["close"])
    ob_valido = detectar_ob(kl_h1)
    barrida_pdh = precio_actual > zonas["PDH"]
    barrida_pdl = precio_actual < zonas["PDL"]

    confs = {
        "macro": "✅" if e_d["estado"] in ["alcista", "bajista"] else "❌",
        "intradía": "✅" if e_h1["estado"] in ["alcista", "bajista"] else "❌",
        "ob_valido": "✅" if ob_valido else "❌",
        "barrida_pdh": "✅" if barrida_pdh else "❌",
        "bajo_asia": "✅" if barrida_pdl else "❌",
    }

    # ===============================
    # 🧠 CONTEXTO MACRO REAL
    # ===============================
    contexto = "—"

    if e_d["estado"] == "bajista" and e_h1["estado"] == "bajista":
        if ob_valido and barrida_pdh:
            contexto = (
                "El precio mantiene estructura bajista multitemporal (D–H1) y "
                "acaba de reaccionar a un OB de H1 tras barrer el alto de Asia. "
                "Alta probabilidad de continuación bajista hacia PDL."
            )
        elif ob_valido:
            contexto = (
                "Estructura bajista confirmada; el precio reacciona dentro de una zona de oferta activa en H1."
            )
        else:
            contexto = (
                "Estructura bajista general, pero sin confirmación clara de reacción institucional aún."
            )

    elif e_d["estado"] == "alcista" and e_h1["estado"] == "alcista":
        if ob_valido and barrida_pdl:
            contexto = (
                "El precio mantiene estructura alcista (D–H1) y acaba de barrer liquidez del bajo de Asia, "
                "reaccionando desde demanda en H1. Posible continuación al alza hacia PDH."
            )
        else:
            contexto = (
                "Estructura alcista sostenida, corrección intradía esperada antes de reanudación."
            )

    elif e_d["estado"] == "lateral" or e_h1["estado"] == "lateral":
        contexto = (
            "El mercado se encuentra en fase de acumulación/distribución; "
            "esperar ruptura clara de estructura antes de entrar."
        )

    return {
        "estructura_detectada": estructura,
        "zonas": zonas,
        "confirmaciones": confs,
        "contexto_general": contexto,
    }
