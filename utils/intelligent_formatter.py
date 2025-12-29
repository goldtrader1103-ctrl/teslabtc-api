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
def _fmt_escenarios_operativos(data: Dict[str, Any]) -> str:
    """
    Construye el texto de los escenarios operativos a partir de:
      - data["scalping"]["continuacion"]
      - data["scalping"]["correccion"]
      - data["swing"]

    Si no hay datos, devuelve un mensaje neutro.
    """
    scalping = data.get("scalping", {}) or {}
    swing = data.get("swing", {}) or {}

    def _estado(flag: Any) -> str:
        return "✅ ACTIVO" if flag else "⏳ En espera"

    bloques = []

    # ------------------------
    # SCALPING CONTINUACIÓN
    # ------------------------
    cont = scalping.get("continuacion", {}) or {}
    if cont:
        bloques.append(
            "🔷 *Escenario SCALPING — Continuación*\n"
            f"• Estado: {_estado(cont.get('activo'))}\n"
            f"• Dirección: {cont.get('direccion', '—')}\n"
            f"• Zona de reacción: {cont.get('zona_reaccion', '—')}\n"
            f"• TP1: {cont.get('tp1_rr', '—')} | TP2: {cont.get('tp2_rr', '—')}\n"
            f"• SL: {cont.get('sl', '—')}"
        )

    # ------------------------
    # SCALPING CORRECCIÓN
    # ------------------------
    corr = scalping.get("correccion", {}) or {}
    if corr:
        bloques.append(
            "🔷 *Escenario SCALPING — Corrección*\n"
            f"• Estado: {_estado(corr.get('activo'))}\n"
            f"• Dirección: {corr.get('direccion', '—')}\n"
            f"• Zona de reacción: {corr.get('zona_reaccion', '—')}\n"
            f"• TP1: {corr.get('tp1_rr', '—')} | TP2: {corr.get('tp2_rr', '—')}\n"
            f"• SL: {corr.get('sl', '—')}"
        )

    # ------------------------
    # SWING
    # ------------------------
    if swing:
        zona = swing.get("zona_reaccion") or swing.get("premium_zone", "—")
        bloques.append(
            "📈 *Escenario SWING H4*\n"
            f"• Estado: {_estado(swing.get('activo'))}\n"
            f"• Dirección: {swing.get('direccion', '—')}\n"
            f"• Zona de reacción: {zona}\n"
            f"• TP1: {swing.get('tp1_rr', '—')} | TP2: {swing.get('tp2_rr', '—')} | TP3: {swing.get('tp3_objetivo', '—')}\n"
            f"• SL: {swing.get('sl', '—')}"
        )

    if not bloques:
        return "No hay escenarios activos por ahora. Esperando BOS + zona institucional."

    return "\n\n".join(bloques)

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

def construir_mensaje_senales(data: Dict[str, Any]) -> str:
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

def construir_contexto_detallado(data: dict, tipo_escenario: str) -> str:
    """
    Construye el contexto para:
      - scalping_continuacion
      - scalping_correccion
      - swing

    Muestra:
      - Meta: activo, precio, sesión
      - Estructura + rangos H4 y H1
      - Lógica del escenario (qué busca exactamente)
      - Niveles de entrada / TP / SL si existen
      - Recomendación TESLABTC (2 primeras horas, 1 trade por sesión, etc.)
    """
    activo = data.get("activo", "BTCUSDT")
    precio_actual = data.get("precio_actual", "—")
    sesion = data.get("sesión", data.get("sesion", "—"))

    estructura = data.get("estructura_detectada", {}) or {}
    scalping = data.get("scalping", {}) or {}
    swing_data = data.get("swing", {}) or {}

    # -----------------------------
    # Helpers de formato
    # -----------------------------
    def _extra_tf(tf: str):
        """
        Extrae estado + rango de una TF, siendo tolerante si `estado`
        viene raro (por ejemplo como dict en versiones viejas).
        """
        info = estructura.get(tf, {}) or {}

        raw_estado = info.get("estado", "sin_datos")

        # 👇 Blindaje: si viene dict u otra cosa rara, lo pisamos
        if isinstance(raw_estado, dict):
            estado = "SIN_DATOS"
        else:
            estado = str(raw_estado).upper()

        hi = (
            info.get("RANGO_HIGH")
            or info.get("high")
            or info.get("swing_high")
        )
        lo = (
            info.get("RANGO_LOW")
            or info.get("low")
            or info.get("swing_low")
        )

        return estado, hi, lo

    def _fmt_rango(lo, hi):
        if lo is None or hi is None:
            return "N/D"
        try:
            return f"{float(lo):,.2f} – {float(hi):,.2f} USD"
        except Exception:
            return "N/D"

    def _fmt_precio(v):
        if v in (None, "-", "—"):
            return "—"
        try:
            return f"{float(v):,.2f} USD"
        except Exception:
            return str(v)

    estado_h4, hi_h4, lo_h4 = _extra_tf("H4")
    estado_h1, hi_h1, lo_h1 = _extra_tf("H1")

    rango_h4_txt = _fmt_rango(lo_h4, hi_h4)
    rango_h1_txt = _fmt_rango(lo_h1, hi_h1)

    partes: list[str] = []

    # =====================================================
    # 🧩 CABECERA GENERAL
    # =====================================================
    partes.append(
        "📘 *Contexto TESLABTC A.P.*\n\n"
        f"• Activo: *{activo}*\n"
        f"• Precio actual: {precio_actual}\n"
        f"• Sesión actual: {sesion}\n"
        f"• Estructura H4: *{estado_h4}*\n"
        f"• Estructura H1: *{estado_h1}*\n\n"
        "📐 *Rangos estructurales*\n"
        f"• H4 — Rango operativo: {rango_h4_txt}\n"
        f"• H1 — Rango operativo: {rango_h1_txt}\n"
    )

    # Comentario de relación H4 vs H1
    if estado_h4 in ("ALCISTA", "BAJISTA") and estado_h1 in ("ALCISTA", "BAJISTA"):
        if estado_h4 == estado_h1:
            partes.append(
                "\n🧭 Cuando *H4 y H1 van en la misma dirección* hablamos de "
                "*continuidad institucional* del movimiento.\n"
            )
        else:
            partes.append(
                "\n🧭 Cuando *H4 y H1 van en direcciones opuestas*, interpretamos "
                "que H1 está profundizando hacia la *zona premium de H4* antes de "
                "reanudarse la tendencia macro.\n"
            )

    # =====================================================
    # 🔷 ESCENARIO SCALPING CONTINUACIÓN
    # =====================================================
    if tipo_escenario == "scalping_continuacion":
        esc = scalping.get("continuacion", {}) or {}

        entrada = esc.get("punto_entrada") or esc.get("zona_reaccion") or "—"
        tp1 = esc.get("tp1") or esc.get("tp1_rr") or "—"
        tp2 = esc.get("tp2") or esc.get("tp2_rr") or "—"
        sl = esc.get("sl") or esc.get("sl_tecnico") or "—"

        partes.append(
            "\n🔷 *Escenario SCALPING de Continuación*\n\n"
            "Este escenario *siempre opera a favor de la estructura de H1* "
            "(puede ser BUY o SELL, según esté H1 alcista o bajista):\n"
            "1. Se toma como referencia el *último HIGH/LOW relevante en M5*.\n"
            "2. Se espera un *BOS claro en M5* en la dirección de H1.\n"
            "3. La operación busca acompañar la direccionalidad intradía, no ir contra ella.\n\n"
        )

        partes.append(
            f"📥 Punto de entrada estimado / zona operativa: {_fmt_precio(entrada)}\n"
            f"🎯 TP1 (1:1 + BE / parciales): {_fmt_precio(tp1)}\n"
            f"🎯 TP2 (1:2 objetivo completo): {_fmt_precio(tp2)}\n"
            f"🛡️ SL técnico: {_fmt_precio(sl)}\n\n"
        )

    # =====================================================
    # 🔷 ESCENARIO SCALPING CORRECCIÓN
    # =====================================================
    elif tipo_escenario == "scalping_correccion":
        esc = scalping.get("correccion", {}) or {}

        entrada = esc.get("punto_entrada") or esc.get("zona_reaccion") or "—"
        tp1 = esc.get("tp1") or esc.get("tp1_rr") or "—"
        tp2 = esc.get("tp2") or esc.get("tp2_rr") or "—"
        sl = esc.get("sl") or esc.get("sl_tecnico") or "—"

        partes.append(
            "\n🔷 *Escenario SCALPING de Corrección*\n\n"
            "Este escenario *siempre va en contra de H1* (es el retroceso intradía):\n"
            "1. H1 marca la dirección principal, pero el precio corrige contra ella.\n"
            "2. Se busca un *BOS en M5* contra H1, dentro de un rango claro.\n"
            "3. El objetivo es capturar el retroceso, no toda la tendencia.\n\n"
        )

        partes.append(
            f"📥 Punto de entrada estimado / zona operativa: {_fmt_precio(entrada)}\n"
            f"🎯 TP1 (1:1 + BE / parciales): {_fmt_precio(tp1)}\n"
            f"🎯 TP2 (1:2 objetivo completo): {_fmt_precio(tp2)}\n"
            f"🛡️ SL técnico: {_fmt_precio(sl)}\n\n"
        )

    # =====================================================
    # 📈 ESCENARIO SWING (H4 + BOS H1)
    # =====================================================
    elif tipo_escenario == "swing":
        zona = swing_data.get("zona_reaccion") or swing_data.get("premium_zone") or {}

        if isinstance(zona, dict):
            z_min = zona.get("min") or zona.get("low") or zona.get("zona_min")
            z_max = zona.get("max") or zona.get("high") or zona.get("zona_max")
            zona_txt = _fmt_rango(z_min, z_max)
        elif isinstance(zona, (list, tuple)) and len(zona) == 2:
            zona_txt = _fmt_rango(zona[0], zona[1])
        else:
            zona_txt = "—"

        tp1 = swing_data.get("tp1") or swing_data.get("tp1_rr") or "—"
        tp2 = swing_data.get("tp2") or swing_data.get("tp2_rr") or "—"
        tp3 = swing_data.get("tp3") or swing_data.get("tp3_objetivo") or "—"
        sl = swing_data.get("sl") or "—"

        partes.append(
            "\n📈 *Escenario SWING H4*\n\n"
            "El swing se construye a partir del *último impulso válido de H4*:\n"
            "1. Se identifica el tramo de impulso actual en H4.\n"
            "2. Sobre ese impulso se calcula la *zona premium 61.8 % – 88.6 %*.\n"
            "3. En esa zona se exige *quiebre y cierre de H1* a favor de la "
            "tendencia de H4 antes de validar el setup.\n\n"
        )

        partes.append(
            f"📥 Zona de reacción H4 (premium): {zona_txt}\n"
            f"🎯 TP1: {_fmt_precio(tp1)}\n"
            f"🎯 TP2: {_fmt_precio(tp2)}\n"
            f"🎯 TP3: {_fmt_precio(tp3)}\n"
            f"🛡️ SL técnico: {_fmt_precio(sl)}\n\n"
        )

    else:
        return "⚠️ Escenario de contexto no reconocido. Usa scalping_continuacion, scalping_correccion o swing."

    # =====================================================
    # 🕒 RECOMENDACIÓN OPERATIVA TESLABTC
    # =====================================================
    partes.append(
        "🕒 *Recomendación operativa TESLABTC:*\n"
        "• Priorizar las *primeras 2 horas* de la sesión activa (Londres o NY).\n"
        "• 1 trade por día y por sesión, en *un solo activo*.\n"
        "• Si el precio está muy cerca del borde del rango H4/H1, ser más selectiva con las entradas.\n"
        "• Evitar operar en medio de noticias fuertes o en plena zona de indecisión.\n"
    )

    return "".join(partes)

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
