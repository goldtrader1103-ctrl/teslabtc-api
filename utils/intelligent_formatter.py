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

def construir_mensaje_operativo(data):

    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")

    estructura = data.get("estructura_detectada", {})
    zonas = data.get("zonas_detectadas", {})
    confs = data.get("confirmaciones", {})

    setup = data.get("setup_tesla", {}) or {}

    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados! "
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

    d_line = f"📈 D: {d_estado} ({d_bos}) | RANGO: {d_hi}–{d_lo}" if d_hi and d_lo else f"📈 D: {d_estado} ({d_bos})"
    h4_line = f"⚙️ H4: {h4_estado} ({h4_bos}) | RANGO: {h4_hi}–{h4_lo}" if h4_hi and h4_lo else f"⚙️ H4: {h4_estado} ({h4_bos})"
    h1_line = f"🔹 H1: {h1_estado} ({h1_bos}) | RANGO: {h1_hi}–{h1_lo}" if h1_hi and h1_lo else f"🔹 H1: {h1_estado} ({h1_bos})"

    direccion = f"{d_line}\n{h4_line}\n{h1_line}"

    # --------------------------------------------------------
    # 💎 ZONAS DE LIQUIDEZ
    # --------------------------------------------------------
    zonas_txt = []

    if zonas.get("PDH") or zonas.get("PDL"):
        zonas_txt.append(f"• PDH: {zonas.get('PDH', '—')} | • PDL: {zonas.get('PDL', '—')}")

    if zonas.get("ASIAN_HIGH") or zonas.get("ASIAN_LOW"):
        zonas_txt.append(f"• ASIAN HIGH: {zonas.get('ASIAN_HIGH', '—')} | • ASIAN LOW: {zonas.get('ASIAN_LOW', '—')}")
    else:
        zonas_txt.append("• Rango Asiático: — (sin datos)")

    if zonas.get("POI_H4"):
        zonas_txt.append(f"• POI H4: {zonas['POI_H4']}")
    if zonas.get("POI_H1"):
        zonas_txt.append(f"• POI H1: {zonas['POI_H1']}")
    if zonas.get("OB_H4"):
        zonas_txt.append(f"• OB H4: {zonas['OB_H4']}")
    if zonas.get("OB_H1"):
        zonas_txt.append(f"• OB H1: {zonas['OB_H1']}")

    zonas_final = "\n".join(zonas_txt)
    # --------------------------------------------------------
    # 📊 ESCENARIOS OPERATIVOS
    # --------------------------------------------------------
    try:
        escenarios_txt = _fmt_escenarios_operativos(data)
    except Exception as e:
        escenarios_txt = f"Error al generar escenarios: {e}"

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
    # 🧩 MENSAJE FINAL COMPLETO
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

📊 **ESCENARIOS OPERATIVOS**
──────────────────────────────
{escenarios_txt}

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
# 🔹 Escenarios Operativos TESLABTC (Continuación / Corrección)
# ============================================================
def _fmt_escenarios_operativos(payload: Dict[str, Any]) -> str:
    e1 = payload.get("escenario_1", {})
    e2 = payload.get("escenario_2", {})

    # Contexto general del análisis
    contexto_operativo = payload.get("contexto_operativo", "—")
    tipo_sugerido = payload.get("tipo_operacion_sugerida", "—")
    riesgo_operativo = payload.get("riesgo_operativo", "—")

    def _esc_txt(e, titulo, color):
        tipo = e.get("tipo", tipo_sugerido)
        riesgo = e.get("riesgo", riesgo_operativo)
        contexto = e.get("contexto", contexto_operativo)
        setup_estado = e.get("setup_estado", "⏳ Sin setup activo — esperando confirmaciones.")
        setup = e.get("setup", {})
        confs_favor = e.get("confs_favor", [])
        confs_pend = e.get("confs_pendientes", [])
        texto = e.get("texto", "—")

        # Fallback: asegurar que siempre haya contenido visible
        if not contexto or contexto == "—":
            contexto = contexto_operativo or "Sin contexto operativo."
        if not riesgo or riesgo == "—":
            riesgo = riesgo_operativo or "Medio"

        return (
f"{color} {titulo}\n"
f"──────────────────────────────\n"
f"📈 Dirección: {tipo}\n"
f"⚠️ Riesgo: {riesgo}\n"
f"📍 Contexto: {contexto}\n\n"
f"{texto}\n\n"
f"⚙️ Estado del Setup: {setup_estado}\n"
f"📥 Zona de reacción: {setup.get('zona_entrada', '—')}\n"
f"🎯 TP1: {setup.get('tp1', '—')}\n"
f"🎯 TP2: {setup.get('tp2', '—')}\n"
f"🎯 TP3: {setup.get('tp3', '—')}\n"
f"🛡️ SL: {setup.get('sl', '—')}\n"
f"💬 Nota: {setup.get('observacion', '—')}\n\n"
f"✅ Confirmaciones a favor: {', '.join(confs_favor) if confs_favor else '—'}\n"
f"⚠️ Confirmaciones faltantes: {', '.join(confs_pend) if confs_pend else '—'}\n"
        )

    msg = "📊 ESCENARIOS OPERATIVOS\n──────────────────────────────\n"
    msg += _esc_txt(e1, "Escenario de Continuación", "🟢") + "\n"
    msg += _esc_txt(e2, "Escenario de Corrección / Contra-tendencia", "🔴")

    # Agregar una línea contextual final (macro resumen)
    if contexto_operativo and contexto_operativo != "—":
        msg += (
            "\n──────────────────────────────\n"
            f"🧠 Contexto operativo global TESLABTC:\n{contexto_operativo}\n"
            f"📊 Operación sugerida: {tipo_sugerido} ({riesgo_operativo} riesgo)\n"
        )

    return msg

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
# ============================================================
# 🧩 COMPATIBILIDAD LEGACY — construir_mensaje_free
# ============================================================

def construir_mensaje_free(data: dict) -> str:
    """
    Versión simplificada para modo Free (dummy fallback).
    Se usa solo para evitar errores de importación en main.py.
    """
    return (
        "📋 TESLABTC Free Mode\n"
        "──────────────────────────────\n"
        "Este análisis pertenece a la versión gratuita del bot.\n"
        "Para ver estructuras, escenarios y zonas completas,\n"
        "activa tu cuenta Premium TESLABTC.\n"
    )
