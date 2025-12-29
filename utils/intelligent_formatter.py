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
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    precio = data.get("precio_actual", "—")
    sesion = data.get("sesión", "—")
    scalping = data.get("scalping", {})
    swing = data.get("swing", {})
    reflexion = data.get("reflexion", "")
    slogan = data.get("slogan", "")

    cont = scalping.get("continuacion", {})
    corr = scalping.get("correccion", {})

    def estado(activo_flag: Any) -> str:
        return "✅ ACTIVO" if activo_flag else "⏳ En espera"

    # ============================
    # 🎯 LÓGICA ESPECIAL SWING
    # ============================
    swing_punto_entrada = swing.get("punto_entrada", "—")
    swing_zona = swing.get("premium_zone") or swing.get("zona_reaccion", "—")
    swing_tp1 = swing.get("tp1_rr", "1:1 (BE)")
    swing_tp2 = swing.get("tp2_rr", "1:2 (50%)")
    swing_tp3 = swing.get("tp3_objetivo", "—")
    swing_sl = swing.get("sl", "—")

    # Si NO hay punto de entrada (precio aún no está en la zona 61.8–88.6)
    if not swing_punto_entrada or swing_punto_entrada == "—":
        swing_detalle = f"""📥 Zona de reacción: {swing_zona}
📍 Punto de entrada: --
🎯 TP1: --
🎯 TP2: --
🎯 TP3: --
🛡️ SL: --"""
    else:
        # Precio DENTRO de la zona: usamos el último alto/bajo de H1 como punto de entrada
        swing_detalle = f"""📥 Zona de reacción: {swing_zona}
📍 Punto de entrada: {swing_punto_entrada} (quiebre y cierre H1)
🎯 TP1: {swing_tp1}
🎯 TP2: {swing_tp2}
🎯 TP3: {swing_tp3}
🛡️ SL: {swing_sl}"""

    msg = f"""*📋 SEÑALES ACTIVAS*
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio actual: {precio}
🕒 Sesión: {sesion}

*📊 ESCENARIOS OPERATIVOS SCALPING*
──────────────────────────────
*🔷 Escenario de Continuación (Tendencia Principal)*
──────────────────────────────
📌 Estado: {estado(cont.get('activo'))}
📈 Dirección: {cont.get('direccion', '—')}
⚠️ Riesgo: {cont.get('riesgo', 'N/A')}
📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.

📥 Punto de entrada: {cont.get('zona_reaccion', '—')}
🎯 TP1: {cont.get('tp1_rr', '1:1 (50% + BE)')}
🎯 TP2: {cont.get('tp2_rr', '1:2 (50%)')}
🛡️ SL: {cont.get('sl', '—')}

*🔷 Escenario de Corrección (Contra Tendencia)*
──────────────────────────────
📌 Estado: {estado(corr.get('activo'))}
📈 Dirección: {corr.get('direccion', '—')}
⚠️ Riesgo: {corr.get('riesgo', 'N/A')}
📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.

📥 Punto de entrada: {corr.get('zona_reaccion', '—')}
🎯 TP1: {corr.get('tp1_rr', '1:1 (50% + BE)')}
🎯 TP2: {corr.get('tp2_rr', '1:2 (50%)')}
🛡️ SL: {corr.get('sl', '—')}

*📈 ESCENARIO SWING*
──────────────────────────────
📌 Estado: {estado(swing.get('activo'))}
📈 Dirección: {swing.get('direccion', '—')}
⚠️ Riesgo: {swing.get('riesgo', 'N/A')}
📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.

{swing_detalle}

*📓 Reflexión TESLABTC A.P.*
──────────────────────────────
💭 {reflexion}

⚠️ Análisis SCALPING diseñado para la apertura de cada sesión (Asia, Londres y NY).
⚠️ Análisis SWING actualizado cada vela de 1H.
{slogan}"""
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
# 🧠 Contexto detallado por escenario
# ============================================================

from typing import Dict, Any

def construir_contexto_detallado(data: Dict[str, Any], escenario: str) -> str:
    """
    Escenario puede ser:
      - 'scalping_continuacion'
      - 'scalping_correccion'
      - 'swing'
    Devuelve un texto explicando el porqué de la operación.
    """
    estructura = data.get("estructura_detectada", {}) or {}
    dir_h4 = estructura.get("H4", "sin_datos")
    dir_h1 = estructura.get("H1", "sin_datos")
    sesion_ny = estructura.get("sesion_ny_activa", False)
    ventana_ny = estructura.get("ventana_scalping_ny", False)

    scalping = (data.get("scalping") or {}).copy()
    swing = (data.get("swing") or {}).copy()

    cont = scalping.get("continuacion") or {}
    corr = scalping.get("correccion") or {}

    def _txt_sesion():
        if sesion_ny and ventana_ny:
            return "Estamos dentro de la ventana operativa de la sesión de Nueva York (primeras 2 horas)."
        elif sesion_ny and not ventana_ny:
            return "La sesión de Nueva York está activa, pero fuera de la ventana principal de scalping."
        else:
            return "La sesión de Nueva York está cerrada; este contexto es solo de referencia."

    # ==========================
    # SCALPING — CONTINUACIÓN
    # ==========================
    if escenario == "scalping_continuacion":
        dir_op = cont.get("direccion", "—")
        riesgo = cont.get("riesgo", "—")
        zona = cont.get("zona_reaccion", "—")
        sl = cont.get("sl", "—")
        tp1 = cont.get("tp1_rr", "1:1 (50% + BE)")
        tp2 = cont.get("tp2_rr", "1:2 (50%)")

        return (
            "🎯 *Contexto SCALPING — Escenario de Continuación*\n\n"
            f"- Estructura H4: *{dir_h4.upper()}*\n"
            f"- Estructura H1 (intradía): *{dir_h1.upper()}*\n"
            f"- Operación propuesta: *{dir_op.upper()}* a favor de la estructura intradía.\n"
            f"- Riesgo estimado: *{riesgo}*.\n\n"
            f"La idea de esta entrada es aprovechar el *impulso principal del día*.\n"
            f"Se trabaja con órdenes pendientes en M5, esperando el *quiebre del nivel* definido como zona de reacción:\n"
            f"- Zona de reacción (quiebre): `{zona}`\n"
            f"- Stop Loss sugerido: `{sl}`\n"
            f"- TP1: `{tp1}`\n"
            f"- TP2: `{tp2}`\n\n"
            f"{_txt_sesion()}\n\n"
            "El objetivo es capturar un tramo del movimiento direccional principal con gestión rápida, "
            "sin buscar el swing completo, sólo el impulso intradía más claro."
        )

    # ==========================
    # SCALPING — CORRECCIÓN
    # ==========================
    if escenario == "scalping_correccion":
        dir_op = corr.get("direccion", "—")
        riesgo = corr.get("riesgo", "—")
        zona = corr.get("zona_reaccion", "—")
        sl = corr.get("sl", "—")
        tp1 = corr.get("tp1_rr", "1:1 (50% + BE)")
        tp2 = corr.get("tp2_rr", "1:2 (50%)")

        return (
            "🎯 *Contexto SCALPING — Escenario de Corrección*\n\n"
            f"- Estructura H4: *{dir_h4.upper()}*\n"
            f"- Estructura H1 (intradía): *{dir_h1.upper()}*\n"
            f"- Operación propuesta: *{dir_op.upper()}* *contra* la estructura intradía.\n"
            f"- Riesgo estimado: *{riesgo}*.\n\n"
            "Este escenario busca aprovechar una *corrección profunda* o un posible *falso quiebre* del movimiento principal.\n"
            "Es una operación más agresiva: el precio puede extender el retroceso antes de retomar la tendencia.\n\n"
            f"Parámetros sugeridos (M5):\n"
            f"- Zona de reacción (quiebre): `{zona}`\n"
            f"- Stop Loss sugerido: `{sl}`\n"
            f"- TP1: `{tp1}`\n"
            f"- TP2: `{tp2}`\n\n"
            f"{_txt_sesion()}\n\n"
            "El objetivo aquí es capturar el *respiro* del precio, no el impulso macro. "
            "Por eso se clasifica como operación de mayor riesgo y requiere disciplina absoluta en el SL."
        )

    # ==========================
    # SWING — A FAVOR DE H4
    # ==========================
    if escenario == "swing":
        dir_op = swing.get("direccion", "—")
        zona = swing.get("zona_reaccion", "—")
        tp1 = swing.get("tp1_rr", "1:1 (BE)")
        tp2 = swing.get("tp2_rr", "1:2 (50%)")
        tp3 = swing.get("tp3_objetivo", "Alto/Bajo H4")
        sl = swing.get("sl", "—")

        return (
            "🎯 *Contexto SWING — Estructura H4/H1*\n\n"
            f"- Estructura H4 (macro): *{dir_h4.upper()}*\n"
            f"- Estructura H1 (intradía): *{dir_h1.upper()}* alineada con H4.\n"
            f"- Operación propuesta: *{dir_op.upper()}* siguiendo la tendencia macro.\n\n"
            "La lógica aquí es operar únicamente cuando H1 confirma la dirección de H4 con un *BOS claro* "
            "y el precio reacciona en *zona premium* (descuento/prima según el caso).\n\n"
            f"Condición de activación:\n"
            f"- Quiebre y cierre del nivel clave de H1 en zona premium: `{zona}`\n\n"
            "Gestión sugerida:\n"
            f"- SL: `{sl}` (por detrás del último alto/bajo relevante de H1)\n"
            f"- TP1: `{tp1}`\n"
            f"- TP2: `{tp2}`\n"
            f"- TP3: `{tp3}`\n\n"
            "Este tipo de operación tiene vocación de *swing*: puede durar varias horas o días, "
            "buscando acompañar el tramo completo de la estructura de H4."
        )

    return "No se pudo construir el contexto para el escenario solicitado."


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
