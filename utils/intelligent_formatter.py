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

import random, re
from datetime import datetime

# ============================================================
# 🌟 FRASES MOTIVACIONALES TESLABTC (recortado a las más usadas)
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
    slogan = data.get("slogan", "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    # --------------------------------------------------------
    # 🧭 DIRECCIÓN GENERAL
    #   D → muestra estado + BOS + RANGO (HH–LL) sin hablar de HH/LL como estructura.
    #   H4 / H1 → se mantienen con HH/LL como lo venías usando.
    # --------------------------------------------------------
    d  = estructura.get("D", {}) or {}
    h4 = estructura.get("H4", {}) or {}
    h1 = estructura.get("H1", {}) or {}

    d_estado = str(d.get("estado", "—")).upper()
    d_bos    = d.get("BOS", "—")
    d_hh     = d.get("HH", "—")
    d_ll     = d.get("LL", "—")

    # Rango D: si hay datos, se muestra como rango puro
    if d_hh not in (None, "—") and d_ll not in (None, "—"):
        d_line = f"📈 D: {d_estado} ({d_bos}) | RANGO: {d_hh}–{d_ll}"
    else:
        d_line = f"📈 D: {d_estado} ({d_bos})"

    h4_line = (
        f"⚙️ H4: {str(h4.get('estado','—')).upper()} ({h4.get('BOS','—')}) "
        f"| HH: {h4.get('HH','—')} | LL: {h4.get('LL','—')}"
    )
    h1_line = (
        f"🔹 H1: {str(h1.get('estado','—')).upper()} ({h1.get('BOS','—')}) "
        f"| HH: {h1.get('HH','—')} | LL: {h1.get('LL','—')}"
    )

    direccion = f"{d_line}\n{h4_line}\n{h1_line}"

    # --------------------------------------------------------
    # 💎 ZONAS DE LIQUIDEZ + ASIA + OB/POI
    # --------------------------------------------------------
    zonas_txt = []

    pdh = zonas.get("PDH")
    pdl = zonas.get("PDL")
    if pdh or pdl:
        zonas_txt.append(f"• PDH: {pdh or '—'} | • PDL: {pdl or '—'}")

    asia_high = zonas.get("ASIAN_HIGH")
    asia_low  = zonas.get("ASIAN_LOW")
    if asia_high and asia_low:
        zonas_txt.append(f"• ASIAN HIGH: {asia_high} | • ASIAN LOW: {asia_low}")
    elif asia_high or asia_low:
        zonas_txt.append(f"• ASIAN HIGH: {asia_high or '—'} | • ASIAN LOW: {asia_low or '—'}")
    else:
        zonas_txt.append("• Rango Asiático: — (sin datos)")

    if zonas.get("OB_H4"):
        zonas_txt.append(f"• OB H4 Cercano: {zonas['OB_H4']}")
    if zonas.get("POI_H1"):
        zonas_txt.append(f"• POI H1 Cercano: {zonas['POI_H1']}")

    zonas_final = "\n".join(zonas_txt) if zonas_txt else "—"

    # --------------------------------------------------------
    # ✅ CONFIRMACIONES CON CONTEXTO
    #   Se mantienen como bloque general, pero también las usamos
    #   para construir los escenarios (continuación / corrección).
    # --------------------------------------------------------
    conf_desc = {
        "macro":       "Tendencia macro (D) a favor del contexto general.",
        "intradía":    "Dirección intradía (H1/H4) coherente con la estructura actual.",
        "ob_valido":   "OB válido y no mitigado dentro de la sesión.",
        "barrida_pdh": "Barrida de liquidez superior detectada.",
        "bajo_asia":   "Reacción en bajo asiático o zona inferior relevante."
    }

    conf_txt = []
    for k, v in confs.items():
        texto = conf_desc.get(k, k.replace("_", " ").capitalize())
        conf_txt.append(f"• {texto}: {v}")
    conf_final = "\n".join(conf_txt) if conf_txt else "—"

    # --------------------------------------------------------
    # ⚙️ SETUP TESLABTC
    # --------------------------------------------------------
    if setup.get("activo"):
        setup_txt = (
            f"{setup.get('nivel','SETUP ACTIVO')}\n"
            f"{setup.get('contexto','')}\n"
            f"📈 Zona: {setup.get('zona_entrada','—')} | "
            f"⛔ SL: {setup.get('sl','—')} | "
            f"🎯 TP1: {setup.get('tp1','—')} | 🎯 TP2: {setup.get('tp2','—')}\n"
            f"{setup.get('comentario','')}"
        )
    else:
        setup_txt = "⏳ Sin setup activo — esperando confirmaciones estructurales (BOS + POI + Sesión NY)."

    # --------------------------------------------------------
    # 📊 ESCENARIOS OPERATIVOS
    #   - Si la API envía escenario_1 / escenario_2 → se usan.
    #   - Si NO los envía → fallback inteligente basado en:
    #       * tendencias D/H4/H1
    #       * zonas PDH/PDL/Asia
    #       * confirmaciones ✅ / ❌
    # --------------------------------------------------------
    escenarios_txt = []

    def _extraer_ok_pendientes():
        oks, pendientes = [], []
        for clave, desc in conf_desc.items():
            v = confs.get(clave)
            if v == "✅":
                oks.append(desc)
            elif v == "❌":
                pendientes.append(desc)
        return oks, pendientes

    oks, pendientes = _extraer_ok_pendientes()

    # Si la API ya manda escenarios, los respetamos
    if esc1 or esc2:
        if esc1:
            desc1 = esc1.get("descripcion") or esc1.get("texto") or "Escenario de continuación a favor de tendencia."
            escenarios_txt.append(f"🟢 Escenario de Continuación (bajo riesgo relativo):\n{desc1}")
        if esc2:
            desc2 = esc2.get("descripcion") or esc2.get("texto") or "Escenario de corrección / contra-tendencia."
            escenarios_txt.append(f"🔴 Escenario de Corrección (mayor riesgo):\n{desc2}")
    else:
        # 🔁 Fallback dinámico
        estado_h4 = str(h4.get("estado", "—")).lower()
        estado_h1 = str(h1.get("estado", "—")).lower()

        sesgo = "neutro"
        if "bajista" in (estado_h4, estado_h1):
            sesgo = "bajista"
        elif "alcista" in (estado_h4, estado_h1):
            sesgo = "alcista"

        # Zonas para target
        target_superior = []
        target_inferior = []
        if pdh:        target_superior.append(f"PDH: {pdh}")
        if zonas.get("ASIAN_HIGH"): target_superior.append(f"ASIAN HIGH: {zonas['ASIAN_HIGH']}")
        if pdl:        target_inferior.append(f"PDL: {pdl}")
        if zonas.get("ASIAN_LOW"):  target_inferior.append(f"ASIAN LOW: {zonas['ASIAN_LOW']}")

        if sesgo == "bajista":
            # Continuación: ventas hacia liquidez inferior
            cont_text = "Continuación bajista: priorizar ventas tras retrocesos a oferta/OB válido."
            if target_inferior:
                cont_text += " Objetivo en liquidez inferior → " + ", ".join(target_inferior) + "."
            corr_text = "Corrección alcista: sólo compras en rebotes claros desde demanda fuerte, con gestión conservadora."
            if target_superior:
                corr_text += " Potenciales zonas de toma de parciales en liquidez superior → " + ", ".join(target_superior) + "."
        elif sesgo == "alcista":
            cont_text = "Continuación alcista: priorizar compras tras mitigación en demanda válida."
            if target_superior:
                cont_text += " Objetivo en liquidez superior → " + ", ".join(target_superior) + "."
            corr_text = "Corrección bajista: ventas sólo si hay BOS claro contra tendencia y reacción fuerte en oferta."
            if target_inferior:
                corr_text += " Zonas probables de toma de beneficio en liquidez inferior → " + ", ".join(target_inferior) + "."
        else:
            cont_text = "Estructura en rango / transición: esperar BOS claro a favor de tendencia antes de operar."
            corr_text = "Escenario de corrección: operar contra este contexto implica riesgo elevado, priorizar la espera."

        # Añadimos confirmaciones al texto
        if oks:
            cont_text += "\n   ✔️ Confirmaciones a favor: " + "; ".join(oks) + "."
        if pendientes:
            corr_text += "\n   ⚠️ Confirmaciones pendientes / no cumplidas: " + "; ".join(pendientes) + "."

        escenarios_txt.append(f"🟢 Escenario de Continuación (bajo riesgo relativo):\n{cont_text}")
        escenarios_txt.append(f"🔴 Escenario de Corrección (mayor riesgo / contra-tendencia):\n{corr_text}")

    escenarios_final = "\n\n".join(escenarios_txt) if escenarios_txt else "—"

    # --------------------------------------------------------
    # 🧠 CONCLUSIÓN OPERATIVA
    # --------------------------------------------------------
    conclusion = data.get("conclusion_general", "Sin conclusión registrada.")

    # --------------------------------------------------------
    # 💭 REFLEXIÓN
    # --------------------------------------------------------
    reflex = reflexion or frase_motivacional()

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
📊 Temporalidades: D | H4 | H1 | M15 | M5

🧭 **DIRECCIÓN GENERAL**
──────────────────────────────
{direccion}

💎 **ZONAS DE LIQUIDEZ**
──────────────────────────────
{zonas_final}

✅ **CONFIRMACIONES CLAVE**
──────────────────────────────
{conf_final}

⚙️ **SETUP TESLABTC**
──────────────────────────────
{setup_txt}

📊 **ESCENARIOS OPERATIVOS**
──────────────────────────────
{escenarios_final}

🧠 **CONCLUSIÓN OPERATIVA**
──────────────────────────────
{conclusion}

📓 **Reflexión TESLABTC A.P.**
──────────────────────────────
💭 {reflex}

⚠️ Análisis exclusivo para la sesión NY.
{slogan}
"""
    return safe_markdown(msg.strip())

# ============================================================
# 🌙 MODO FREE
# ============================================================
def construir_mensaje_free(data):
    fecha = data.get("fecha","—")
    activo = data.get("activo","BTCUSDT")
    precio = data.get("precio_actual","—")
    sesion = data.get("sesión","—")
    estructura = data.get("estructura_detectada",{}) or {}
    d  = estructura.get("D",{}) or {}
    h4 = estructura.get("H4",{}) or {}
    h1 = estructura.get("H1",{}) or {}

    reflex = frase_motivacional()
    slogan = data.get("slogan","✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    msg = f"""
📋 **TESLABTC.KG — Análisis Gratuito**
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio: {precio}
🕒 Sesión: {sesion}

🧭 D: {str(d.get('estado','—')).upper()} | H4: {str(h4.get('estado','—')).upper()} | H1: {str(h1.get('estado','—')).upper()}

💭 {reflex}

⚠️ Accede a TESLABTC Premium para ver:
• Confirmaciones estructurales
• Zonas institucionales (PDH/PDL/Asia)
• Setup activo y conclusiones dinámicas
{slogan}
"""
    return safe_markdown(msg.strip())

# ============================================================
# 🛡️ SAFE MARKDOWN
# ============================================================
def safe_markdown(text: str) -> str:
    if not text:
        return ""
    # asteriscos sueltos → ✱
    text = re.sub(r'(?<!\*)\*(?!\*)', '✱', text)
    # guiones bajos sueltos → ‗
    text = re.sub(r'(?<!_)_(?!_)', '‗', text)
    # corchetes y paréntesis → variantes seguras
    text = text.replace("[","〔").replace("]","〕").replace("(","（").replace(")","）")
    return text

# ============================================================
# 🧹 ALIAS COMPATIBILIDAD
# ============================================================
def limpiar_texto(text: str) -> str:
    """Compatibilidad con versiones antiguas — mantiene limpieza básica."""
    if not isinstance(text, str):
        return ""
    text = text.replace("  ", " ").replace(" | ", " |").strip()
    return text
