# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.7 ESTABLE FINAL)
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
# 📊 DETALLE DE ESCENARIO
# ============================================================

def _detalle_escenario(esc, zonas, titulo_base, emoji):
    if not esc or not isinstance(esc, dict):
        return ""

    tipo = esc.get("tipo", "Neutro")
    prob = esc.get("probabilidad", "Media")
    riesgo = esc.get("riesgo", "Medio")
    texto = esc.get("texto", "")
    contexto = esc.get("contexto", "")

    if tipo == "Compra":
        dir_txt = "Alcista"
    elif tipo == "Venta":
        dir_txt = "Bajista"
    else:
        dir_txt = "Neutro"

    lineas = [
        f"{emoji} {titulo_base} {dir_txt}",
        f"Tipo: {tipo} | Riesgo: {riesgo} | Probabilidad: {prob}"
    ]

    if texto:
        lineas.append(texto)

    if contexto:
        lineas.append(f"📌 Contexto: {contexto}")

    confs_favor = esc.get("confs_favor", [])
    confs_pend = esc.get("confs_pendientes", [])

    if confs_favor:
        lineas.append("✅ Confirmaciones a favor:")
        for c in confs_favor:
            lineas.append(f"• {c}")

    if confs_pend:
        lineas.append("⚠️ Confirmaciones pendientes:")
        for c in confs_pend:
            lineas.append(f"• {c}")

    return "\n".join(lineas)

# ============================================================
# 🧩 MENSAJE PREMIUM
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

    setup_txt = ""
    if setup.get("activo"):
        setup_txt = (
            f"\n⚙️ SETUP TESLABTC\n"
            f"Zona: {setup.get('zona_entrada','—')}\n"
            f"SL: {setup.get('sl','—')}\n"
            f"TP1: {setup.get('tp1','—')} | TP2: {setup.get('tp2','—')}"
        )

    msg = f"""
📋 REPORTE TESLABTC — Sesión NY
────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio: {precio}
🕒 Sesión: {sesion}

🧭 DIRECCIÓN GENERAL
{direccion}

💎 ZONAS
{zonas_final}

📊 ESCENARIOS
{esc1_txt}

{esc2_txt}

{setup_txt}

🧠 CONCLUSIÓN
{conclusion}

💭 Reflexión
{reflexion}

{slogan}
"""

    return safe_markdown(msg.strip())

# ============================================================
# 🆓 MENSAJE FREE (ESTE ERA EL QUE FALTABA Y ROMPÍA TODO)
# ============================================================

def construir_mensaje_free(data: dict) -> str:
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    precio = data.get("precio_actual", "—")
    sesion = data.get("sesión", "—")
    estructura = data.get("estructura_detectada", {}) or {}

    d = estructura.get("D", {})
    h4 = estructura.get("H4", {})
    h1 = estructura.get("H1", {})

    reflex = frase_motivacional()

    msg = f"""
📋 TESLABTC — ANÁLISIS GRATUITO
────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio: {precio}
🕒 Sesión: {sesion}

🧭 D: {d.get('estado','—')} | H4: {h4.get('estado','—')} | H1: {h1.get('estado','—')}

💭 {reflex}

⚠️ Activa el modo Premium para ver:
• POI estructurales
• Zonas de liquidez
• Escenarios reales
• Setup TESLABTC
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
    text = text.replace("[", "〔").replace("]", "〕")
    text = text.replace("(", "（").replace(")", "）")
    return text
