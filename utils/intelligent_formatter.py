# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.5 PRO)
# ============================================================
# - No modifica la lógica de la API, sólo el mensaje final.
# - Dirección D muestra RANGO en vez de HH/LL teóricos.
# - Zonas: PDH/PDL + Asia + OB/POI.
# - Confirmaciones con contexto.
# - Escenarios SIEMPRE: Continuación y Corrección (fallback).
# - Protección Markdown para Telegram.
# ============================================================

import random
import re
from datetime import datetime


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
    "El éxito llega cuando la disciplina se vuelve natural."
]


def frase_motivacional():
    return random.choice(FRASES_TESLA)


# ============================================================
# 🧩 FORMATEADOR PREMIUM
# ============================================================

def construir_mensaje_operativo(data):

    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")

    estructura = data.get("estructura_detectada", {})
    zonas = data.get("zonas_detectadas", {})
    confs = data.get("confirmaciones", {})

    esc1 = data.get("escenario_1", {}) or {}
    esc2 = data.get("escenario_2", {}) or {}
    setup = data.get("setup_tesla", {}) or {}

    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    )

    # --------------------------------------------------------
    # 🧭 DIRECCIÓN GENERAL — RANGO REAL
    # --------------------------------------------------------

    d = estructura.get("D", {}) or {}
    h4 = estructura.get("H4", {}) or {}
    h1 = estructura.get("H1", {}) or {}

    d_estado = str(d.get("estado", "—")).upper()
    h4_estado = str(h4.get("estado", "—")).upper()
    h1_estado = str(h1.get("estado", "—")).upper()

    d_bos = d.get("BOS", "—")
    h4_bos = h4.get("BOS", "—")
    h1_bos = h1.get("BOS", "—")

    d_hi = d.get("RANGO_HIGH", zonas.get("D_HIGH"))
    d_lo = d.get("RANGO_LOW", zonas.get("D_LOW"))
    h4_hi = h4.get("RANGO_HIGH", zonas.get("H4_HIGH"))
    h4_lo = h4.get("RANGO_LOW", zonas.get("H4_LOW"))
    h1_hi = h1.get("RANGO_HIGH", zonas.get("H1_HIGH"))
    h1_lo = h1.get("RANGO_LOW", zonas.get("H1_LOW"))

    d_line = (
        f"📈 D: {d_estado} ({d_bos}) | RANGO: {d_hi}–{d_lo}"
        if d_hi is not None and d_lo is not None else
        f"📈 D: {d_estado} ({d_bos})"
    )

    h4_line = (
        f"⚙️ H4: {h4_estado} ({h4_bos}) | RANGO: {h4_hi}–{h4_lo}"
        if h4_hi is not None and h4_lo is not None else
        f"⚙️ H4: {h4_estado} ({h4_bos})"
    )

    h1_line = (
        f"🔹 H1: {h1_estado} ({h1_bos}) | RANGO: {h1_hi}–{h1_lo}"
        if h1_hi is not None and h1_lo is not None else
        f"🔹 H1: {h1_estado} ({h1_bos})"
    )

    direccion = f"{d_line}\n{h4_line}\n{h1_line}"

    # --------------------------------------------------------
    # 💎 ZONAS DE LIQUIDEZ
    # --------------------------------------------------------

    zonas_txt = []

    pdh = zonas.get("PDH")
    pdl = zonas.get("PDL")

    if pdh or pdl:
        zonas_txt.append(f"• PDH: {pdh or '—'} | • PDL: {pdl or '—'}")

    asia_high = zonas.get("ASIAN_HIGH")
    asia_low = zonas.get("ASIAN_LOW")

    if asia_high and asia_low:
        zonas_txt.append(f"• ASIAN HIGH: {asia_high} | • ASIAN LOW: {asia_low}")
    elif asia_high or asia_low:
        zonas_txt.append(f"• ASIAN HIGH: {asia_high or '—'} | • ASIAN LOW: {asia_low or '—'}")
    else:
        zonas_txt.append("• Rango Asiático: — (sin datos)")

    if zonas.get("OB_H4"):
        zonas_txt.append(f"• OB H4: {zonas['OB_H4']}")
    if zonas.get("POI_H4"):
        zonas_txt.append(f"• POI H4: {zonas['POI_H4']}")
    if zonas.get("OB_H1"):
        zonas_txt.append(f"• OB H1: {zonas['OB_H1']}")
    if zonas.get("POI_H1"):
        zonas_txt.append(f"• POI H1: {zonas['POI_H1']}")

    zonas_final = "\n".join(zonas_txt) if zonas_txt else "—"

    # --------------------------------------------------------
    # ⚙️ SETUP TESLABTC
    # --------------------------------------------------------

    if setup.get("activo"):
        setup_txt = (
            f"{setup.get('nivel', 'SETUP ACTIVO')}\n"
            f"{setup.get('contexto', '')}\n"
            f"Zona de entrada: {setup.get('zona_entrada', '—')}\n"
            f"SL: {setup.get('sl', '—')}\n"
            f"TP1: {setup.get('tp1', '—')} | TP2: {setup.get('tp2', '—')}\n"
            f"Comentario: {setup.get('comentario', '')}"
        )
    else:
        setup_txt = (
            "⏳ Sin setup activo — esperando confirmaciones estructurales "
            "(BOS + POI + Sesión NY)."
        )
    # --------------------------------------------------------
    # 🕐 ETIQUETA PRE-BOS (si aplica)
    # --------------------------------------------------------
    pre_bos_txt = ""
    estado_operativo = str(data.get("estado_operativo", "")).strip()
    if estado_operativo.startswith("🕐"):
        pre_bos_txt = f"""
🔵 **{estado_operativo}**
──────────────────────────────
El precio se encuentra dentro del rango operativo, pero aún **sin confirmación BOS M5**.
Esperar ruptura o confirmación de gatillo antes de ejecutar setup.
"""

    # --------------------------------------------------------
    # 🧩 MENSAJE FINAL
    # --------------------------------------------------------

    msg = f"""
📋 **REPORTE TESLABTC A.P. — Sesión NY**
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio actual: {precio}
🕒 Sesión: {sesion}

{pre_bos_txt}
🧭 **DIRECCIÓN GENERAL**
──────────────────────────────
{direccion}

💎 **ZONAS DE LIQUIDEZ**
──────────────────────────────
{zonas_final}

⚙️ **SETUP TESLABTC**
──────────────────────────────
{setup_txt}

🧠 **CONCLUSIÓN OPERATIVA**
──────────────────────────────
{data.get("conclusion_general", "Sin conclusión registrada.")}

📓 **Reflexión TESLABTC A.P.**
──────────────────────────────
💭 {reflexion}

⚠️ Análisis exclusivo para la sesión NY.
{slogan}
"""

    return safe_markdown(msg.strip())


# ============================================================
# 🛡️ SAFE MARKDOWN
# ============================================================

def safe_markdown(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'(?<!\*)\*(?!\*)', '✱', text)
    text = re.sub(r'(?<!_)_(?!_)', '‗', text)
    text = text.replace("[", "〔").replace("]", "〕").replace("(", "（").replace(")", "）")

    return text


# ============================================================
# 🧹 ALIAS COMPATIBILIDAD
# ============================================================

def limpiar_texto(text: str) -> str:
    if not isinstance(text, str):
        return ""

    return text.replace("  ", " ").strip()
# ============================================================
# 🧩 FORMATEADOR FREE (para usuarios sin token Premium)
# ============================================================

def construir_mensaje_free(data):
    """
    Formateador básico para usuarios Free.
    Muestra estructura, precio y sesión sin detalles Premium.
    """
    fecha = data.get("fecha", "—")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    fuente = data.get("fuente_precio", "—")
    estructura = data.get("estructura_detectada", {})

    h4 = estructura.get("H4 (macro)", {}).get("estado", "—")
    h1 = estructura.get("H1 (intradía)", {}).get("estado", "—")
    m15 = estructura.get("M15 (reacción)", {}).get("estado", "—")

    msg = f"""
📋 **TESLABTC Free — Vista General**
──────────────────────────────
📅 Fecha: {fecha}
💵 Precio actual: {precio}
🕒 Sesión: {sesion}

🧭 **Estructura Detectada**
──────────────────────────────
H4 (macro): {h4}
H1 (intradía): {h1}
M15 (reacción): {m15}

⚙️ Fuente de datos: {fuente}
──────────────────────────────
💭 Accede al modo *Premium* para ver zonas, confirmaciones y setups activos.
"""
    return safe_markdown(msg.strip())
