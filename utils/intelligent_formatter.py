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

def _detalle_escenario(esc: dict, zonas: dict, titulo_base: str, emoji: str) -> str:
    if not isinstance(esc, dict):
        return f"{emoji} {titulo_base}: datos no disponibles."

    tipo = esc.get("tipo", "Neutro")
    prob = esc.get("probabilidad", "Media")
    riesgo = esc.get("riesgo", "Medio")
    texto_base = esc.get("descripcion") or esc.get("texto") or "Escenario generado automáticamente por el sistema."
    contexto = esc.get("contexto") or "Contexto no especificado."

    if tipo == "Compra":
        dir_txt = "Alcista"
        sign = 1
    elif tipo == "Venta":
        dir_txt = "Bajista"
        sign = -1
    else:
        dir_txt = "Neutro"
        sign = 0

    titulo = f"{titulo_base} {dir_txt}" if dir_txt != "Neutro" else titulo_base

    poi_h1 = zonas.get("POI_H1")
    poi_h4 = zonas.get("POI_H4")
    ob_h1 = zonas.get("OB_H1")
    ob_h4 = zonas.get("OB_H4")

    zona_txt = poi_h1 or poi_h4 or ob_h1 or ob_h4

    entry_low = entry_high = sl_price = None

    if isinstance(zona_txt, str) and "-" in zona_txt:
        try:
            nums = [float(x.strip()) for x in zona_txt.replace("–", "-").split("-")]
            entry_low, entry_high = min(nums), max(nums)
            sl_price = entry_low if tipo == "Compra" else entry_high
        except Exception:
            pass

    tp1 = tp2 = tp3 = None

    if entry_low and entry_high and sl_price and sign != 0:
        entry_price = (entry_low + entry_high) / 2
        r = abs(entry_price - sl_price)
        tp1 = entry_price + sign * r
        tp2 = entry_price + sign * 2 * r

    pdh = zonas.get("PDH")
    pdl = zonas.get("PDL")
    ah = zonas.get("ASIAN_HIGH")
    al = zonas.get("ASIAN_LOW")

    if sign > 0:
        tp3 = max(x for x in [pdh, ah] if isinstance(x, (int, float))) if any(isinstance(x, (int, float)) for x in [pdh, ah]) else None
    elif sign < 0:
        tp3 = min(x for x in [pdl, al] if isinstance(x, (int, float))) if any(isinstance(x, (int, float)) for x in [pdl, al]) else None

    lineas: List[str] = []

    lineas.append(f"{emoji} {titulo} ({tipo} | riesgo {riesgo}, probabilidad {prob})")
    lineas.append(texto_base)
    lineas.append(f"📌 Contexto: {contexto}")

    if entry_low and entry_high:
        lineas.append(f"📥 Zona de entrada: {entry_low:,.2f}–{entry_high:,.2f}")
    elif zona_txt:
        lineas.append(f"📥 Zona de entrada: {zona_txt}")
    else:
        lineas.append("📥 Zona de entrada: esperar estructura en POI válido.")

    if sl_price:
        lineas.append(f"⛔ SL: {sl_price:,.2f}")
    else:
        lineas.append("⛔ SL: último alto/bajo estructural.")

    tp_lines = []
    if tp1:
        tp_lines.append(f"TP1: {tp1:,.2f} (1:1)")
    if tp2:
        tp_lines.append(f"TP2: {tp2:,.2f} (1:2)")
    if tp3:
        tp_lines.append(f"TP3: {tp3:,.2f} (Liquidez)")

    if tp_lines:
        lineas.append("🎯 Objetivos: " + " | ".join(tp_lines))
    else:
        lineas.append("🎯 Objetivos: pendientes por estructura.")

    lineas.append("💼 Gestión: mover BE en TP1 y asegurar 50%.")

    confs_favor = esc.get("confs_favor", [])
    confs_pend = esc.get("confs_pendientes", [])

    if confs_favor:
        lineas.append("")
        lineas.append("✅ Confirmaciones a favor:")
        for c in confs_favor:
            lineas.append(f"   • {c}")

    if confs_pend:
        lineas.append("")
        lineas.append("⚠️ Pendientes antes de ejecutar:")
        for c in confs_pend:
            lineas.append(f"   • {c}")

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
