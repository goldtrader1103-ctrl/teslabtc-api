# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.8 PRO FINAL)
# ============================================================
# - Dirección D, H4 y H1 con RANGO real (High–Low)
# - Muestra Zonas de Liquidez: PDH, PDL, Asia High/Low, POI H4, POI H1
# - Escenarios completos (Continuación y Corrección)
# - Confirmaciones detalladas tipo lista
# - Setup Activo con etiqueta superior (color dinámica)
# - Formato seguro para Telegram (Markdown protegido)
# ============================================================

import random
import re
from datetime import datetime
from typing import Dict, Any

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

def construir_mensaje_operativo(data: Dict[str, Any]) -> str:
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    estructura = data.get("estructura_detectada", {})
    zonas = data.get("zonas_detectadas", {})
    confs = data.get("confirmaciones", {})
    setup = data.get("setup_tesla", {}) or {}
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get("slogan", "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    # ============================================================
    # 💥 ETIQUETA SUPERIOR (SETUP ACTIVO con color dinámico)
    # ============================================================
    etiqueta_setup = ""
    if setup.get("activo"):
        tipo = setup.get("tipo", "").lower()
        color_emoji = "🟢" if "compra" in tipo else "🔴" if "venta" in tipo else "💥"
        etiqueta_setup = (
            f"{color_emoji} **SETUP ACTIVO ({setup.get('tipo', '—').upper()}) — PRECIO {precio}** {color_emoji}\n"
            f"──────────────────────────────\n"
            f"📍 Zona de entrada: {setup.get('zona_entrada', '—')} | "
            f"🎯 TP1: {setup.get('tp1', '—')} | 🛡️ SL: {setup.get('sl', '—')}\n"
            f"⚙️ Contexto: {setup.get('contexto', 'Ejecución institucional detectada en M5.')}\n\n"
        )

    # ============================================================
    # 🧭 DIRECCIÓN GENERAL — RANGO REAL
    # ============================================================
    d = estructura.get("D", {}) or {}
    h4 = estructura.get("H4", {}) or {}
    h1 = estructura.get("H1", {}) or {}

    def _fmt_linea(tf: Dict[str, Any], nombre: str, icono: str) -> str:
        estado = str(tf.get("estado", "—")).upper()
        bos = tf.get("BOS", "—")
        hi = tf.get("RANGO_HIGH") or zonas.get(f"{nombre}_HIGH", "—")
        lo = tf.get("RANGO_LOW") or zonas.get(f"{nombre}_LOW", "—")
        return f"{icono} {nombre}: {estado} ({bos}) | RANGO: {hi}–{lo}"

    direccion_txt = "\n".join([
        _fmt_linea(d, "D", "📈"),
        _fmt_linea(h4, "H4", "⚙️"),
        _fmt_linea(h1, "H1", "🔹"),
    ])

    # ============================================================
    # 💎 ZONAS DE LIQUIDEZ
    # ============================================================
    zonas_txt = [
        f"• PDH: {zonas.get('PDH', '—')} | PDL: {zonas.get('PDL', '—')}",
        f"• ASIA HIGH: {zonas.get('ASIAN_HIGH', '—')} | ASIA LOW: {zonas.get('ASIAN_LOW', '—')}",
        f"• POI H4: {zonas.get('POI_H4', '—')}",
        f"• POI H1: {zonas.get('POI_H1', '—')}",
    ]
    zonas_final = "\n".join(zonas_txt)

    # ============================================================
    # 📊 ESCENARIOS OPERATIVOS
    # ============================================================
    try:
        escenarios_txt = _fmt_escenarios_operativos(data)
    except Exception as e:
        escenarios_txt = f"Error al generar escenarios: {e}"

    # ============================================================
    # ⚙️ SETUP TESLABTC (solo si no está activo)
    # ============================================================
    if not setup.get("activo"):
        setup_txt = (
            "⏳ **Sin setup activo** — esperando confirmaciones estructurales "
            "(BOS + POI + Sesión NY)."
        )
    else:
        setup_txt = "✅ Setup confirmado en zona institucional (M5)."

    # ============================================================
    # 🧠 CONCLUSIÓN Y REFLEXIÓN
    # ============================================================
    conclusion_txt = (
        f"🧠 **CONCLUSIÓN OPERATIVA**\n──────────────────────────────\n{data.get('conclusion_general', 'Sin conclusión registrada.')}\n\n"
        f"📓 **Reflexión TESLABTC A.P.**\n──────────────────────────────\n💭 {reflexion}\n\n"
        f"⚠️ Análisis exclusivo para la sesión NY.\n{slogan}"
    )

    # ============================================================
    # 📋 MENSAJE FINAL COMPLETO
    # ============================================================
    msg = f"""
{etiqueta_setup}
📋 **REPORTE TESLABTC A.P. — Sesión NY**
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio actual: {precio}
🕒 Sesión: {sesion}

🧭 **DIRECCIÓN GENERAL**
──────────────────────────────
{direccion_txt}

💎 **ZONAS DE LIQUIDEZ**
──────────────────────────────
{zonas_final}

📊 **ESCENARIOS OPERATIVOS**
──────────────────────────────
{escenarios_txt}

⚙️ **SETUP TESLABTC**
──────────────────────────────
{setup_txt}

{conclusion_txt}
"""
    return safe_markdown(msg.strip())


# ============================================================
# 🔹 Escenarios Operativos TESLABTC (Continuación / Corrección)
# ============================================================

def construir_mensaje_operativo(data: Dict[str, Any]) -> str:
    """Formatea el mensaje principal del bot con la nueva lógica:

    - Muestra sólo info clave (fecha, activo, sesión, precio)
    - Escenarios SCALPING (continuación / corrección) en M5
    - Escenario SWING basado en H4 + H1
    - El detalle de contexto se delega a futuros botones/comandos
    """
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    scalping = data.get("scalping", {}) or {}
    swing = data.get("swing", {}) or {}
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get("slogan", "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    s_cont = scalping.get("continuacion", {}) or {}
    s_corr = scalping.get("correccion", {}) or {}
    s_swing = swing or {}

    def _flag(activo_flag: bool) -> str:
        return "✅ ACTIVO" if activo_flag else "⏳ En espera"

    # ============================
    # CABECERA
    # ============================
    msg = ""
    msg += "📋 SEÑALES ACTIVAS\n"
    msg += "──────────────────────────────\n"
    msg += f"📅 Fecha: {fecha}\n"
    msg += f"💰 Activo: {safe_markdown(activo)}\n"
    msg += f"💵 Precio actual: {precio}\n"
    msg += f"🕒 Sesión: {sesion}\n\n"

    # ============================
    # SCALPING
    # ============================
    msg += "📊 ESCENARIOS OPERATIVOS SCALPING\n"
    msg += "──────────────────────────────\n"

    # Continuación
    msg += "🟢 Escenario de Continuación (Tendencia Principal)\n"
    msg += "──────────────────────────────\n"
    msg += f"📌 Estado: {_flag(s_cont.get('activo', False))}\n"
    msg += f"📈 Dirección: {s_cont.get('direccion', '—')}\n"
    msg += f"⚠️ Riesgo: {s_cont.get('riesgo', 'N/A')}\n"
    msg += "📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.\n\n"
    msg += f"📥 Zona de reacción: {s_cont.get('zona_reaccion', '—')}\n"
    msg += f"🎯 TP1: {s_cont.get('tp1_rr', '1:1 (50% + BE)')}\n"
    msg += f"🎯 TP2: {s_cont.get('tp2_rr', '1:2 (50%)')}\n"
    msg += f"🛡️ SL: {s_cont.get('sl', '—')}\n\n"

    # Corrección
    msg += "🔴 Escenario de Corrección (Contra Tendencia)\n"
    msg += "──────────────────────────────\n"
    msg += f"📌 Estado: {_flag(s_corr.get('activo', False))}\n"
    msg += f"📈 Dirección: {s_corr.get('direccion', '—')}\n"
    msg += f"⚠️ Riesgo: {s_corr.get('riesgo', 'N/A')}\n"
    msg += "📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.\n\n"
    msg += f"📥 Zona de reacción: {s_corr.get('zona_reaccion', '—')}\n"
    msg += f"🎯 TP1: {s_corr.get('tp1_rr', '1:1 (50% + BE)')}\n"
    msg += f"🎯 TP2: {s_corr.get('tp2_rr', '1:2 (50%)')}\n"
    msg += f"🛡️ SL: {s_corr.get('sl', '—')}\n\n"

    # ============================
    # SWING
    # ============================
    msg += "📈 ESCENARIO SWING\n"
    msg += "──────────────────────────────\n"
    msg += f"📌 Estado: {_flag(s_swing.get('activo', False))}\n"
    msg += f"📈 Dirección: {s_swing.get('direccion', '—')}\n"
    msg += f"⚠️ Riesgo: {s_swing.get('riesgo', 'N/A')}\n"
    msg += "📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.\n\n"
    msg += f"📥 Zona de reacción: {s_swing.get('zona_reaccion', '—')}\n"
    msg += f"🎯 TP1: {s_swing.get('tp1_rr', '1:1 (BE)')}\n"
    msg += f"🎯 TP2: {s_swing.get('tp2_rr', '1:2 (50%)')}\n"
    msg += f"🎯 TP3: {s_swing.get('tp3_objetivo', 'Alto/Bajo H4')}\n"
    msg += f"🛡️ SL: {s_swing.get('sl', '—')}\n\n"

    # ============================
    # REFLEXIÓN
    # ============================
    msg += "📓 Reflexión TESLABTC A.P.\n"
    msg += "──────────────────────────────\n"
    msg += f"💭 {reflexion}\n\n"
    msg += "⚠️ Análisis SCALPING exclusivo para la apertura de la sesión NY (primeras 2 horas).\n"
    msg += "⚠️ Análisis SWING actualizado cada vela de 1H.\n"
    msg += slogan

    return msg


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
# 🧩 FORMATEADOR FREE (modo básico)
# ============================================================

def construir_mensaje_free(data: Dict[str, Any]) -> str:
    fecha = data.get("fecha", "—")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    estructura = data.get("estructura_detectada", {})

    h4 = estructura.get("H4", {}).get("estado", "—")
    h1 = estructura.get("H1", {}).get("estado", "—")
    m15 = estructura.get("M15", {}).get("estado", "—")

    msg = f"""
📋 **TESLABTC Free — Vista General**
──────────────────────────────
📅 Fecha: {fecha}
💵 Precio actual: {precio}
🕒 Sesión: {sesion}

🧭 **Estructura Detectada**
──────────────────────────────
H4: {h4}
H1: {h1}
M15: {m15}

💭 Accede al modo *Premium* para ver zonas, confirmaciones y setups activos.
"""
    return safe_markdown(msg.strip())
