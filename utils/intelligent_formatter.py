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

def construir_contexto_detallado(data: dict, tipo: str) -> str:
    """
    Genera un contexto explicativo por escenario:
      - scalping_continuacion
      - scalping_correccion
      - swing

    Usa directamente la salida de evaluar_estructura:
      { "estado": ..., "high": ..., "low": ... }
    para H4 y H1 dentro de data["estructura_detectada"].
    """
    estructura = data.get("estructura_detectada", {}) or {}

    # ----------------------------
    # Helpers internos
    # ----------------------------
    def _get_tf_block(*nombres):
        """Busca el bloque de una TF por nombre exacto o parcial."""
        # intento por clave exacta
        for n in nombres:
            if n in estructura:
                return estructura.get(n) or {}
        # intento por "contiene"
        for k, v in estructura.items():
            if any(n.lower() in str(k).lower() for n in nombres):
                return v or {}
        return {}

    def _extraer_direccion(info: dict) -> str:
        """Usa 'estado' como dirección principal."""
        if not isinstance(info, dict):
            return "N/D"
        return (
            info.get("estado")              # alcista / bajista / rango
            or info.get("direccion")
            or info.get("tendencia")
            or "N/D"
        )

    def _extraer_high_low(info: dict):
        """
        Saca high / low por TF usando las claves que devuelve evaluar_estructura:
          - high / low
        y, si existen, también:
          - ultimo_high / ultimo_low
        """
        if not isinstance(info, dict):
            return None, None

        hi = info.get("high") or info.get("ultimo_high")
        lo = info.get("low") or info.get("ultimo_low")

        try:
            hi_f = float(hi) if hi is not None else None
        except Exception:
            hi_f = None

        try:
            lo_f = float(lo) if lo is not None else None
        except Exception:
            lo_f = None

        return hi_f, lo_f

    def _fmt_precio(v):
        if v is None:
            return "N/D"
        try:
            return f"{v:,.2f} USD"
        except Exception:
            return str(v)

    def _fmt_rango(low, high):
        if low is None or high is None:
            return "N/D"
        try:
            return f"{low:,.2f} – {high:,.2f} USD"
        except Exception:
            return f"{low} – {high}"

    # ----------------------------
    # Extraer H4 y H1
    # ----------------------------
    h4 = _get_tf_block("H4", "4h", "macro")
    h1 = _get_tf_block("H1", "1h", "intradía", "intra")

    dir_h4 = _extraer_direccion(h4)
    dir_h1 = _extraer_direccion(h1)

    h4_high, h4_low = _extraer_high_low(h4)
    h1_high, h1_low = _extraer_high_low(h1)

    h4_high_txt = _fmt_precio(h4_high)
    h4_low_txt  = _fmt_precio(h4_low)
    h1_high_txt = _fmt_precio(h1_high)
    h1_low_txt  = _fmt_precio(h1_low)

    rango_h4_txt = _fmt_rango(h4_low, h4_high)
    rango_h1_txt = _fmt_rango(h1_low, h1_high)

    activo = data.get("activo", "BTCUSDT")
    fecha  = data.get("fecha", "")
    sesion = data.get("sesión") or data.get("sesion") or "Sesión NY"

    # ========================================================
    # 🟢 CONTEXTO SCALPING CONTINUACIÓN
    # ========================================================
    if tipo == "scalping_continuacion":
        return f"""📘 *CONTEXTO SCALPING DE CONTINUACIÓN — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión:* {sesion}
📌 *Escenario:* Operar *a favor* de la tendencia intradía (H1).

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
  ├─ 🔽 Bajo H4: `{h4_low_txt}`
  └─ 🔼 Alto H4: `{h4_high_txt}`
• H1 (intradía): *{dir_h1}*
  ├─ 🔽 Bajo H1: `{h1_low_txt}`
  └─ 🔼 Alto H1: `{h1_high_txt}`

*2️⃣ Rangos de trabajo*
• 🟣 Rango H4 (macro): `{rango_h4_txt}`
  → Zona donde se mueve la estructura principal.
• 🔵 Rango H1 (operativo): `{rango_h1_txt}`
  → Zona donde buscamos el setup intradía.

*3️⃣ Lógica del escenario de CONTINUACIÓN*
• No siempre es compra: es *a favor de la dirección de H1*:
  - H1 alcista → buscamos compras.
  - H1 bajista → buscamos ventas.
• Gatillo: *BOS en micro (M5/M3/M1) a favor de H1* dentro del rango operativo.

*4️⃣ Relación H4 ↔ H1*
• Si H4 y H1 van en la misma dirección:
  → Contexto fuerte y alineado.
• Si H4 va en contra de H1:
  → Entendemos que H1 puede estar profundizando dentro de H4 antes de girarse,
    pero el scalping de continuación sigue obedeciendo a H1.

*5️⃣ Recomendación TESLA*
• Mayor probabilidad: *primeras 2 horas de la sesión NY*.
• Sugerencia: *1 trade al día* por par.
• Confirmaciones mínimas:
  - Tendencia definida en H1.
  - BOS claro en micro a favor de H1.
  - Estructura respetada (sin velas caóticas rompiendo todo).
"""

    # ========================================================
    # 🟠 CONTEXTO SCALPING CORRECCIÓN
    # ========================================================
    if tipo == "scalping_correccion":
        return f"""📕 *CONTEXTO SCALPING DE CORRECCIÓN — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión:* {sesion}
📌 *Escenario:* Operar el *retroceso* en contra de la tendencia de H1.

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
  ├─ 🔽 Bajo H4: `{h4_low_txt}`
  └─ 🔼 Alto H4: `{h4_high_txt}`
• H1 (intradía): *{dir_h1}*
  ├─ 🔽 Bajo H1: `{h1_low_txt}`
  └─ 🔼 Alto H1: `{h1_high_txt}`

*2️⃣ Rangos de trabajo*
• 🟣 Rango H4 (macro): `{rango_h4_txt}`
  → Marco de la historia grande.
• 🔵 Rango H1 (operativo): `{rango_h1_txt}`
  → Zona donde se dibuja el retroceso que queremos aprovechar.

*3️⃣ Lógica del escenario de CORRECCIÓN*
• No siempre es venta:
  - Si H1 es alcista → la corrección será bajista.
  - Si H1 es bajista → la corrección será alcista.
• Buscamos:
  - Movimiento extendido hacia un extremo del rango H1.
  - Señales de agotamiento y *BOS en micro en contra de H1*.

*4️⃣ Relación con H4*
• Muchas veces el retroceso de H1 es solo el respiro que necesita
  H4 para seguir su historia.
• Si H4 es bajista y H1 alcista:
  → H1 puede estar profundizando en zona premium de H4 antes de girarse.

*5️⃣ Recomendación TESLA*
• Usar también ventana de alta energía: *primeras 2 horas de NY*.
• Operar correcciones con tamaño de posición más conservador.
• Confirmaciones mínimas:
  - Tendencia clara en H1.
  - Extensión hacia extremo de rango.
  - BOS en micro en contra de H1.
"""

    # ========================================================
    # 🔵 CONTEXTO SWING (H4 + BOS H1)
    # ========================================================
    if tipo == "swing":
        return f"""📗 *CONTEXTO SWING TESLABTC — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión de referencia:* {sesion}
📌 *Escenario:* Operar el movimiento amplio guiado por H4 y validado por H1.

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
  ├─ 🔽 Bajo H4: `{h4_low_txt}`
  └─ 🔼 Alto H4: `{h4_high_txt}`
• H1 (transición): *{dir_h1}*
  ├─ 🔽 Bajo H1: `{h1_low_txt}`
  └─ 🔼 Alto H1: `{h1_high_txt}`

*2️⃣ Rangos clave*
• 🟣 Rango swing H4: `{rango_h4_txt}`
  → Nos dice si el precio está en zona de descuento o de premium.
• 🔵 Rango H1: `{rango_h1_txt}`
  → Donde se ve la acumulación / distribución previa al swing.

*3️⃣ Condición CLAVE del swing TESLA*
• No basta con que H4 esté alcista o bajista.
• Se necesita:
  1. Profundidad en zona de interés H4 (extremos del rango).
  2. *BOS + CIERRE de H1*:
     - Ruptura y cierre por encima del último alto relevante → swing alcista.
     - Ruptura y cierre por debajo del último bajo relevante → swing bajista.
  3. Entrada en el pullback controlado posterior a ese BOS.

*4️⃣ Diferencia con scalping*
• Scalping:
  - Opera dentro del rango intradía (H1) con gatillos en M5/M3/M1.
  - Muy dependiente de ventana horaria de la sesión.
• Swing:
  - Mira el “cambio de capítulo” de H4 validado por H1.
  - Menos dependiente de la hora exacta, más de la estructura limpia.

*5️⃣ Recomendaciones TESLA*
• Buscar con calma:
  - H4 en extremo del rango.
  - BOS de H1 con cierre sólido.
  - Pullback ordenado a la zona recién rota.
• Gestión:
  - RRR amplio (≥ 1:3).
  - Parciales en piscinas de liquidez.
  - SL detrás del nivel estructural validado.

Aquí el objetivo no es capturar una vela bonita,
sino participar en el movimiento que confirma la historia de H4.
"""

    # ========================================================
    # Tipo desconocido
    # ========================================================
    return "⚠️ Escenario de contexto no reconocido. Usa scalping_continuacion, scalping_correccion o swing."


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
