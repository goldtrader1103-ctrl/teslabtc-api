# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.8 PRO LIMPIO)
# ============================================================
# - Escenarios SCALPING (continuación / corrección) + SWING
# - Muestra rangos operativos H4 y H1 en el contexto
# - Soporta claves antiguas y nuevas (punto_entrada / zona_reaccion,
#   tp1 / tp1_rr, etc.)
# - Pensado para usarse tanto en la API como en el BOT
# ============================================================

import random
import re
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
    "El éxito llega cuando la disciplina se vuelve natural.",
]


def frase_motivacional() -> str:
    return random.choice(FRASES_TESLA)

# ============================================================
# 🛡️ SAFE MARKDOWN
# ============================================================

def safe_markdown(text: str) -> str:
    """Evita que caracteres sueltos rompan Markdown en Telegram."""
    if not text:
        return ""
    text = re.sub(r"(?<!\*)\*(?!\*)", "✱", text)
    text = re.sub(r"(?<!_)_(?!_)", "‗", text)
    text = text.replace("[", "〔").replace("]", "〕").replace("(", "（").replace(")", "）")
    return text

# Helper común de precios
def _fmt_precio(v: Any) -> str:
    if v in (None, "-", "—", ""):
        return "—"
    try:
        return f"{float(v):,.2f} USD"
    except Exception:
        return str(v)

# ============================================================
# 🧩 FORMATEADOR FREE (modo básico)
# ============================================================

def construir_mensaje_free(data: Dict[str, Any]) -> str:
    fecha = data.get("fecha", "—")
    sesion = data.get("sesión", data.get("sesion", "—"))
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

# ============================================================
# 🔹 MENSAJE PRINCIPAL PREMIUM — "SEÑALES ACTIVAS"
# ============================================================

def construir_mensaje_operativo(data: Dict[str, Any]) -> str:
    """
    Mensaje que ve el usuario en el chat:
      - Escenario de Continuación (SCALPING)
      - Escenario de Corrección (SCALPING)
      - Escenario SWING
    Los detalles finos se ven al pulsar el botón de contexto.
    """
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    precio = data.get("precio_actual", "—")
    sesion = data.get("sesión", data.get("sesion", "—"))

    estructura = data.get("estructura_detectada", {}) or {}
    scalping = data.get("scalping", {}) or {}
    swing = data.get("swing", {}) or {}
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
    )

    cont = scalping.get("continuacion", {}) or {}
    corr = scalping.get("correccion", {}) or {}

    def estado(flag: Any) -> str:
        return "✅ ACTIVO" if flag else "⏳ En espera"

    # Dirección basada en H1 si el análisis no manda texto propio
    estado_h1 = str(estructura.get("H1", {}).get("estado", "—")).upper()

    dir_cont = cont.get("direccion")
    if not dir_cont:
        if estado_h1 == "ALCISTA":
            dir_cont = "BUY a favor de H1"
        elif estado_h1 == "BAJISTA":
            dir_cont = "SELL a favor de H1"
        else:
            dir_cont = "Esperando claridad en H1"

    dir_corr = corr.get("direccion")
    if not dir_corr:
        if estado_h1 == "ALCISTA":
            dir_corr = "SELL contra H1 (retroceso)"
        elif estado_h1 == "BAJISTA":
            dir_corr = "BUY contra H1 (retroceso)"
        else:
            dir_corr = "Retroceso no definido (H1 en rango)"

    # Campos SCALPING (aceptamos nombres nuevos y viejos)
    cont_entrada = cont.get("punto_entrada") or cont.get("zona_reaccion") or "—"
    cont_tp1 = cont.get("tp1") or cont.get("tp1_rr") or "1:1 (50% + BE)"
    cont_tp2 = cont.get("tp2") or cont.get("tp2_rr") or "1:2 (50%)"
    cont_sl = cont.get("sl") or cont.get("sl_tecnico") or "—"

    corr_entrada = corr.get("punto_entrada") or corr.get("zona_reaccion") or "—"
    corr_tp1 = corr.get("tp1") or corr.get("tp1_rr") or "1:1 (50% + BE)"
    corr_tp2 = corr.get("tp2") or corr.get("tp2_rr") or "1:2 (50%)"
    corr_sl = corr.get("sl") or corr.get("sl_tecnico") or "—"

    # Campos SWING
    swing_activo = swing.get("activo", False)
    swing_dir = swing.get("direccion", "—")
    swing_riesgo = swing.get("riesgo", "N/A")

    # zona_reaccion puede venir como dict, lista [low, high] o string
    zona = swing.get("premium_zone") or swing.get("zona_reaccion") or "—"
    if isinstance(zona, dict):
        z_min = zona.get("min") or zona.get("low") or zona.get("zona_min")
        z_max = zona.get("max") or zona.get("high") or zona.get("zona_max")
        if z_min is not None and z_max is not None:
            swing_zona_txt = f"{_fmt_precio(z_min)}–{_fmt_precio(z_max)}"
        else:
            swing_zona_txt = "—"
    elif isinstance(zona, (list, tuple)) and len(zona) == 2:
        swing_zona_txt = f"{_fmt_precio(zona[0])}–{_fmt_precio(zona[1])}"
    else:
        swing_zona_txt = str(zona)

    swing_punto_entrada = swing.get("punto_entrada") or "—"
    swing_tp1 = swing.get("tp1") or swing.get("tp1_rr") or "—"
    swing_tp2 = swing.get("tp2") or swing.get("tp2_rr") or "—"
    swing_tp3 = swing.get("tp3") or swing.get("tp3_objetivo") or "—"
    swing_sl = swing.get("sl") or "—"

    # Si no hay entrada de swing todavía, mostramos solo la zona
    if swing_punto_entrada in ("—", None, ""):
        swing_detalle = f"""📥 Zona de reacción: {swing_zona_txt}
🎯 TP1: —
🎯 TP2: —
🎯 TP3: —
🛡️ SL: —"""
    else:
        swing_detalle = f"""📥 Zona de reacción: {swing_zona_txt}
📍 Punto de entrada: {_fmt_precio(swing_punto_entrada)} (quiebre + cierre H1)
🎯 TP1: {_fmt_precio(swing_tp1)}
🎯 TP2: {_fmt_precio(swing_tp2)}
🎯 TP3: {_fmt_precio(swing_tp3)}
🛡️ SL: {_fmt_precio(swing_sl)}"""

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
📌 Estado: {estado(cont.get("activo"))}
📈 Dirección: {dir_cont}
⚠️ Riesgo: {cont.get("riesgo", "N/A")}
📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.

📥 Punto de entrada: {_fmt_precio(cont_entrada)}
🎯 TP1: {_fmt_precio(cont_tp1)}
🎯 TP2: {_fmt_precio(cont_tp2)}
🛡️ SL: {_fmt_precio(cont_sl)}

*🔷 Escenario de Corrección (Contra Tendencia)*
──────────────────────────────
📌 Estado: {estado(corr.get("activo"))}
📈 Dirección: {dir_corr}
⚠️ Riesgo: {corr.get("riesgo", "N/A")}
📍 Contexto: Pulsa el botón de contexto para ver la explicación completa del trade.

📥 Punto de entrada: {_fmt_precio(corr_entrada)}
🎯 TP1: {_fmt_precio(corr_tp1)}
🎯 TP2: {_fmt_precio(corr_tp2)}
🛡️ SL: {_fmt_precio(corr_sl)}

*📈 ESCENARIO SWING*
──────────────────────────────
📌 Estado: {estado(swing_activo)}
📈 Dirección: {swing_dir}
⚠️ Riesgo: {swing_riesgo}
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
# 🧠 CONTEXTO DETALLADO TESLABTC (botón de contexto)
# ============================================================

def construir_contexto_detallado(data: Dict[str, Any], tipo_escenario: str) -> str:
    """
    Contexto para:
      - "scalping_continuacion"
      - "scalping_correccion"
      - "swing"
    Incluye rangos H4/H1 y la recomendación de operar
    las 2 primeras horas de la sesión.
    """
    activo = data.get("activo", "BTCUSDT")
    precio_actual = data.get("precio_actual", "—")
    sesion = data.get("sesión", data.get("sesion", "—"))

    estructura = data.get("estructura_detectada", {}) or {}
    scalping = data.get("scalping", {}) or {}
    swing_data = data.get("swing", {}) or {}

    # --------- helpers de estructura ---------
    def _extra_tf(tf: str):
        info = estructura.get(tf, {}) or {}
        estado = str(info.get("estado", "sin_datos")).upper()
        hi = info.get("RANGO_HIGH") or info.get("high") or info.get("swing_high")
        lo = info.get("RANGO_LOW") or info.get("low") or info.get("swing_low")
        return estado, hi, lo

    def _fmt_rango(lo, hi):
        if lo is None or hi is None:
            return "N/D"
        try:
            lo_f = float(lo)
            hi_f = float(hi)
            return f"{lo_f:,.2f} – {hi_f:,.2f} USD"
        except Exception:
            return "N/D"

    estado_h4, hi_h4, lo_h4 = _extra_tf("H4")
    estado_h1, hi_h1, lo_h1 = _extra_tf("H1")

    rango_h4_txt = _fmt_rango(lo_h4, hi_h4)
    rango_h1_txt = _fmt_rango(lo_h1, hi_h1)

    partes: list[str] = []

    # ========= CABECERA =========
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

    # ========= SCALPING CONTINUACIÓN =========
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
            "3. La operación busca acompañar la direccionalidad intradía.\n\n"
        )

        partes.append(
            f"📥 Punto de entrada estimado: {_fmt_precio(entrada)}\n"
            f"🎯 TP1 (1:1 + BE / parciales): {_fmt_precio(tp1)}\n"
            f"🎯 TP2 (1:2 objetivo completo): {_fmt_precio(tp2)}\n"
            f"🛡️ SL técnico: {_fmt_precio(sl)}\n\n"
        )

    # ========= SCALPING CORRECCIÓN =========
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
            "2. Se espera un *BOS en M5* contra H1 dentro de un rango claro.\n"
            "3. El objetivo es capturar el retroceso, no la tendencia completa.\n\n"
        )

        partes.append(
            f"📥 Punto de entrada estimado: {_fmt_precio(entrada)}\n"
            f"🎯 TP1 (1:1 + BE / parciales): {_fmt_precio(tp1)}\n"
            f"🎯 TP2 (1:2 objetivo completo): {_fmt_precio(tp2)}\n"
            f"🛡️ SL técnico: {_fmt_precio(sl)}\n\n"
        )

    # ========= SWING =========
    elif tipo_escenario == "swing":
        zona = swing_data.get("premium_zone") or swing_data.get("zona_reaccion") or {}

        if isinstance(zona, dict):
            z_min = zona.get("min") or zona.get("low") or zona.get("zona_min")
            z_max = zona.get("max") or zona.get("high") or zona.get("zona_max")
            zona_txt = _fmt_rango(z_min, z_max)
        elif isinstance(zona, (list, tuple)) and len(zona) == 2:
            zona_txt = _fmt_rango(zona[0], zona[1])
        else:
            zona_txt = str(zona) if zona else "—"

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

    # ========= RECOMENDACIÓN GENERAL =========
    partes.append(
        "🕒 *Recomendación operativa TESLABTC:*\n"
        "• Priorizar las *primeras 2 horas* de la sesión activa (Asia, Londres o NY).\n"
        "• 1 trade por día y por sesión, en *un solo activo*.\n"
        "• Si el precio ya está cerca del borde del rango de H4 o H1, "
        "ser más selectivo con las entradas.\n"
        "• Evitar operar en medio de noticias fuertes o dentro de zonas de "
        "alta indecisión.\n"
    )

    return "".join(partes)
