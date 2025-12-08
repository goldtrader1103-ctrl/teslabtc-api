# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.6 PATCH ESTABLE)
# ============================================================
# ✔ Compatible 100% con análisis premium v5.3
# ✔ No rompe lógica de mercado
# ✔ Evita silencios de ZONAS / ESCENARIOS / SETUP
# ✔ Siempre imprime escenarios aunque falten campos
# ============================================================

import random
import re
from typing import List

# ============================================================
# 🌟 FRASES MOTIVACIONALES TESLABTC
# ============================================================
FRASES_TESLA = [
    "Tu mentalidad define tu rentabilidad.",
    "Disciplina no es hacer lo que amas, sino hacerlo incluso cuando no quieres.",
    "El mercado premia la paciencia, no la prisa.",
    "Cada clic debe tener un propósito, no una emoción.",
    "Tu constancia es tu verdadero edge.",
    "El dinero sigue a la claridad, no a la confusión.",
    "Operar menos es ganar más.",
    "No se trata de acertar siempre, sino de perder correctamente.",
    "Ser trader es dominarse a uno mismo, no al mercado.",
    "El trading no se domina; se respeta cada día.",
    "La consistencia no se busca, se construye.",
    "La constancia vence al talento indisciplinado.",
    "No operes por aburrimiento, opera por confirmación.",
    "El trading recompensa a los que siguen reglas, no impulsos.",
    "Tu única competencia es tu versión de ayer.",
    "Sin registro no hay mejora.",
    "El éxito llega cuando la disciplina se vuelve natural.",
]


def frase_motivacional():
    return random.choice(FRASES_TESLA)


# ============================================================
# 📊 DETALLE DE ESCENARIO (FIX COMPLETO)
# ============================================================

def _detalle_escenario(esc, zonas, titulo_base, emoji):
    if not esc or not isinstance(esc, dict):
        return ""

    tipo = esc.get("tipo", "Neutro")   # Compra o Venta
    prob = esc.get("probabilidad", "Media")
    riesgo = esc.get("riesgo", "Medio")
    texto_base = esc.get("descripcion") or esc.get("texto") or ""
    contexto = esc.get("contexto") or ""

    # ---------------------------------------------------------------------
    # Dirección según tipo (NO NEUTROS AMBIGUOS)
    # ---------------------------------------------------------------------
    if tipo == "Compra":
        dir_txt = "Alcista"
        sign = +1
    elif tipo == "Venta":
        dir_txt = "Bajista"
        sign = -1
    else:
        dir_txt = "Neutro"
        sign = 0

    titulo = f"{titulo_base} {dir_txt}" if dir_txt != "Neutro" else titulo_base

    # ---------------------------------------------------------------------
    # ✅ POI SIEMPRE A FAVOR DE LA TENDENCIA (H1 MANDA LA EJECUCIÓN)
    # ---------------------------------------------------------------------
    poi_h1 = zonas.get("POI_H1")
    poi_h4 = zonas.get("POI_H4")

    # Prioridad: POI de H1, luego H4
    zona_txt = poi_h1 or poi_h4

    entry_low = entry_high = sl_price = None

    if isinstance(zona_txt, str):
        try:
            norm = zona_txt.replace("–", "-").replace("—", "-").replace("−", "-")
            nums = [float(x.strip()) for x in norm.split("-") if x.strip()]
            if len(nums) >= 2:
                entry_low, entry_high = min(nums), max(nums)

                # ✅ SL SIEMPRE EN EXTREMO ESTRUCTURAL
                if tipo == "Compra":
                    sl_price = entry_low
                elif tipo == "Venta":
                    sl_price = entry_high
        except Exception:
            pass

    # ---------------------------------------------------------------------
    # 🎯 TPs REALES DESDE EL RGO
    # ---------------------------------------------------------------------
    tp1 = tp2 = tp3 = None
    entry_price = None

    if (
        entry_low is not None
        and entry_high is not None
        and sl_price is not None
        and sign != 0
    ):
        entry_price = (entry_low + entry_high) / 2.0
        r = abs(entry_price - sl_price)

        if r > 0:
            tp1 = entry_price + sign * r        # 1:1
            tp2 = entry_price + sign * 2 * r    # 1:2

    # ---------------------------------------------------------------------
    # TP3: SIGUIENTE ZONA DE LIQUIDEZ
    # ---------------------------------------------------------------------
    pdh = zonas.get("PDH")
    pdl = zonas.get("PDL")
    ah = zonas.get("ASIAN_HIGH")
    al = zonas.get("ASIAN_LOW")

    if sign > 0:
        candidatos = [x for x in (pdh, ah) if isinstance(x, (int, float))]
        if candidatos:
            tp3 = max(candidatos)
    elif sign < 0:
        candidatos = [x for x in (pdl, al) if isinstance(x, (int, float))]
        if candidatos:
            tp3 = min(candidatos)

    # ---------------------------------------------------------------------
    # 🧾 CONSTRUCCIÓN DEL TEXTO FINAL
    # ---------------------------------------------------------------------
    lineas = [
        f"{emoji} {titulo} ({tipo} | riesgo {riesgo}, probabilidad {prob})"
    ]

    if texto_base:
        lineas.append(texto_base)

    if contexto:
        lineas.append(f"📌 Contexto: {contexto}")

    # ---------------------------------------------------------------------
    # 📥 ZONA DE ENTRADA (REAL)
    # ---------------------------------------------------------------------
    if entry_low is not None and entry_high is not None:
        lineas.append(
            f"📥 Zona de entrada (POI a favor): {entry_low:,.2f}–{entry_high:,.2f}"
        )
    else:
        lineas.append("📥 Zona de entrada: esperar POI válido.")

    # ---------------------------------------------------------------------
    # ⛔ SL REAL
    # ---------------------------------------------------------------------
    if sl_price is not None:
        lineas.append(f"⛔ Stop Loss estructural: {sl_price:,.2f}")
    else:
        lineas.append("⛔ Stop Loss: último alto/bajo estructural.")

    # ---------------------------------------------------------------------
    # 🎯 OBJETIVOS REALES
    # ---------------------------------------------------------------------
    tp_lines = []
    if tp1 is not None:
        tp_lines.append(f"TP1: {tp1:,.2f} (1:1 → mover a BE + parcial)")
    if tp2 is not None:
        tp_lines.append(f"TP2: {tp2:,.2f} (1:2 → objetivo principal)")
    if tp3 is not None:
        tp_lines.append(f"TP3: {tp3:,.2f} (zona de liquidez)")

    if tp_lines:
        lineas.append("🎯 Objetivos: " + " | ".join(tp_lines))
    else:
        lineas.append("🎯 Objetivos: definidos solo tras BOS.")

    # ---------------------------------------------------------------------
    # 💼 GESTIÓN TESLABTC REAL
    # ---------------------------------------------------------------------
    lineas.append(
        "💼 Gestión: BE en 1:1 + 50%, dejar correr solo si la estructura se mantiene."
    )

    # ---------------------------------------------------------------------
    # ✅ CONFIRMACIONES
    # ---------------------------------------------------------------------
    confs_favor = esc.get("confs_favor", []) or []
    confs_pend = esc.get("confs_pendientes", []) or []

    if confs_favor:
        lineas.append("")
        lineas.append("✅ Confirmaciones a favor:")
        for c in confs_favor:
            lineas.append(f"   • {c}")

    if confs_pend:
        lineas.append("")
        lineas.append("⚠️ Confirmaciones pendientes:")
        for c in confs_pend:
            lineas.append(f"   • {c}")
        lineas.append("")
        lineas.append(
            "📎 Recomendación: NO ejecutar hasta que todas se alineen en la zona POI."
        )

    return "\n".join(lineas)

# ============================================================
# 🧩 FORMATEADOR PREMIUM FINAL
# ============================================================

def construir_mensaje_operativo(data: dict) -> str:
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    estructura = data.get("estructura_detectada", {})
    zonas = data.get("zonas_detectadas", {})
    esc1 = data.get("escenario_1")
    esc2 = data.get("escenario_2")
    setup = data.get("setup_tesla", {})
    conclusion = data.get("conclusion_general", "Sin conclusión")
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get("slogan", "✨ Tu mentalidad define tus resultados ✨")

    d = estructura.get("D", {})
    h4 = estructura.get("H4", {})
    h1 = estructura.get("H1", {})

    direccion = (
        f"📈 D: {str(d.get('estado','—')).upper()}\n"
        f"⚙️ H4: {str(h4.get('estado','—')).upper()}\n"
        f"🔹 H1: {str(h1.get('estado','—')).upper()}"
    )

    zonas_txt = []
    for k, v in zonas.items():
        zonas_txt.append(f"• {k}: {v}")

    zonas_final = "\n".join(zonas_txt) if zonas_txt else "—"

    esc1_txt = _detalle_escenario(esc1, zonas, "Escenario de Continuación", "🟢")
    esc2_txt = _detalle_escenario(esc2, zonas, "Escenario de Corrección", "🔴")

    setup_block = ""
    if setup.get("activo"):
        setup_block = (
            f"\n⚙️ SETUP TESLABTC\n"
            f"{setup.get('nivel','—')}\n"
            f"Zona: {setup.get('zona_entrada','—')}\n"
            f"SL: {setup.get('sl','—')}\n"
            f"TP1: {setup.get('tp1','—')} | TP2: {setup.get('tp2','—')}"
        )

    msg = f"""
📋 **REPORTE TESLABTC — Sesión NY**
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio: {precio}
🕒 Sesión: {sesion}

🧭 DIRECCIÓN GENERAL
──────────────────────────────
{direccion}

💎 ZONAS
──────────────────────────────
{zonas_final}

📊 ESCENARIOS OPERATIVOS
──────────────────────────────
{esc1_txt}

{esc2_txt}
{setup_block}

🧠 CONCLUSIÓN
──────────────────────────────
{conclusion}

💭 Reflexión
──────────────────────────────
{reflexion}

{slogan}
"""

    return safe_markdown(msg.strip())


# ============================================================
# 🛡️ SAFE MARKDOWN
# ============================================================

def safe_markdown(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"(?<!\*)\*(?!\*)", "✱", text)
    text = re.sub(r"(?<!_)_(?!_)", "‗", text)
    text = text.replace("[", "〔").replace("]", "〕").replace("(", "（").replace(")", "）")
    return text
