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

    Incluye:
      - Dirección H4 / H1
      - Rango H4 / H1
      - Explicación pedagógica del gatillo
    """
    estructura = data.get("estructura_detectada", {}) or {}

    def _get_tf_block(*nombres):
        """Intenta encontrar el bloque de una TF con varios nombres posibles."""
        for n in nombres:
            if n in estructura:
                return estructura.get(n) or {}
        # búsqueda por contains por si viene como "H4 (macro)" etc
        for k, v in estructura.items():
            if any(n.lower() in str(k).lower() for n in nombres):
                return v or {}
        return {}

    def _extraer_direccion(info: dict) -> str | None:
        if not isinstance(info, dict):
            return None
        return (
            info.get("direccion")
            or info.get("tendencia")
            or info.get("estado")
            or info.get("trend")
        )

    def _extraer_rango(info: dict):
        """
        Devuelve (min, max) si encuentra algo tipo:
          - info["rango"] = {"min": x, "max": y}
          - info["rango"] = {"low": x, "high": y}
          - info["min"], info["max"]
          - info["low"], info["high"]
          - info["rango"] = [x, y] / (x, y)
        """
        if not isinstance(info, dict):
            return None

        r = (
            info.get("rango")
            or info.get("rango_operativo")
            or info.get("rango_h1")
            or info.get("rango_h4")
        )

        low = high = None

        if isinstance(r, dict):
            low = (
                r.get("min")
                or r.get("low")
                or r.get("inferior")
            )
            high = (
                r.get("max")
                or r.get("high")
                or r.get("superior")
            )
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            low, high = r[0], r[1]
        else:
            low = info.get("min") or info.get("low")
            high = info.get("max") or info.get("high")

        if low is None or high is None:
            return None

        try:
            return float(low), float(high)
        except Exception:
            return None

    def _fmt_rango(rango):
        if not rango:
            return "N/D"
        lo, hi = rango
        try:
            return f"{lo:,.2f} – {hi:,.2f} USD"
        except Exception:
            return f"{lo} – {hi}"

    # 🔎 Extraemos H4 y H1
    h4 = _get_tf_block("H4", "4h", "macro")
    h1 = _get_tf_block("H1", "1h", "intradía", "intra")

    dir_h4 = _extraer_direccion(h4) or "N/D"
    dir_h1 = _extraer_direccion(h1) or "N/D"

    rango_h4 = _extraer_rango(h4)
    rango_h1 = _extraer_rango(h1)

    rango_h4_txt = _fmt_rango(rango_h4)
    rango_h1_txt = _fmt_rango(rango_h1)

    # 🧩 Info general del activo (si está)
    activo = data.get("activo", "BTCUSDT")
    fecha = data.get("fecha", "")
    sesion = data.get("sesión") or data.get("sesion") or ""

    # ========================================================
    # 🟢 CONTEXTO SCALPING CONTINUACIÓN
    # ========================================================
    if tipo == "scalping_continuacion":
        texto = f"""📘 *CONTEXTO SCALPING DE CONTINUACIÓN — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión:* {sesion or 'Sesión NY'}
📌 *Escenario:* Operar *a favor* de la tendencia intradía (H1).

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
• H1 (intradía): *{dir_h1}*

*2️⃣ Rangos de trabajo*
• 🟣 Rango H4 (macro): `{rango_h4_txt}`
  → Zona donde se está moviendo la estructura principal.
• 🔵 Rango H1 (operativo): `{rango_h1_txt}`
  → Rango donde buscamos el setup intradía.

*3️⃣ Lógica del escenario de CONTINUACIÓN*
• El escenario de *continuación* no significa siempre compra.
• Significa operar *en la misma dirección que la tendencia de H1*:
  - Si H1 está alcista → buscamos compras.
  - Si H1 está bajista → buscamos ventas.
• El gatillo se da cuando el precio respeta la estructura y se forma un *BOS (Break of Structure)* en M5/M3/M1 *a favor* de H1.

*4️⃣ Uso práctico dentro del rango*
• Si H4 también acompaña la dirección de H1:
  → Escenario de alta alineación (macro + intradía).
• Si H4 va en contra de H1:
  → Entendemos que H1 puede estar profundizando dentro de H4 antes de girarse.
  → Aun así, el escenario de continuación sigue la dirección actual de H1.

*5️⃣ Recomendación operativa TESLA*
• Ventana de mayor probabilidad: *primeras 2 horas de la sesión NY*.
• Sugerencia: *1 trade al día* por par.
• Confirmaciones mínimas:
  - Tendencia definida en H1.
  - BOS claro en M5/M3/M1 en la misma dirección.
  - Respeto de estructura sin rupturas caóticas.

Lee esto como tu “mapa mental” antes de disparar el gatillo.
Tu trabajo no es adivinar el giro, sino sincronizarte con la dirección que el mercado ya mostró en H1.
"""
        return texto

    # ========================================================
    # 🟠 CONTEXTO SCALPING CORRECCIÓN
    # ========================================================
    if tipo == "scalping_correccion":
        texto = f"""📕 *CONTEXTO SCALPING DE CORRECCIÓN — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión:* {sesion or 'Sesión NY'}
📌 *Escenario:* Operar el *retroceso* en contra de la tendencia de H1.

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
• H1 (intradía): *{dir_h1}*

*2️⃣ Rangos de trabajo*
• 🟣 Rango H4 (macro): `{rango_h4_txt}`
  → Marco donde H4 sigue mandando la “historia grande”.
• 🔵 Rango H1 (operativo): `{rango_h1_txt}`
  → Ahí es donde se ve el retroceso que queremos aprovechar.

*3️⃣ Lógica del escenario de CORRECCIÓN*
• El escenario de *corrección* tampoco es siempre venta.
• Es un movimiento *en contra de la tendencia de H1*:
  - Si H1 está alcista → la corrección será bajista.
  - Si H1 está bajista → la corrección será alcista.
• El gatillo se da cuando:
  - El precio entra en una zona donde es razonable que corrija (extremos del rango H1, cercanía a rango H4, etc.).
  - Se forma un *BOS en micro (M5/M3/M1)* en contra de la dirección de H1, mostrando pérdida de fuerza del tramo previo.

*4️⃣ Relación con H4 (macro)*
• Muchas correcciones de H1 son el “respiro” que necesita el precio dentro de la estructura de H4.
• Si H4 es bajista y H1 viene alcista:
  → H1 puede estar profundizando en H4 para luego girarse a favor de H4.
  → El escenario de corrección puede aprovechar ese agotamiento de H1.

*5️⃣ Recomendación operativa TESLA*
• Ventana sugerida: *primeras 2 horas de la sesión NY*.
• Sugerencia: *1 trade al día* por par, sin sobreoperar correcciones.
• Confirmaciones mínimas:
  - Tendencia clara de H1.
  - Movimiento extendido hacia un extremo del rango H1.
  - BOS en contra de H1 en microestructura.

La corrección es el “respiro”, no el cambio de historia.
Tu rol es capturar un tramo lógico del retroceso, no enamorarte del giro.
"""
        return texto

    # ========================================================
    # 🔵 CONTEXTO SWING (H4 + BOS H1)
    # ========================================================
    if tipo == "swing":
        texto = f"""📗 *CONTEXTO SWING TESLABTC — {activo}*

📅 *Fecha:* {fecha}
🕒 *Sesión de referencia:* {sesion or 'NY (pero swing no depende solo de la sesión)'}
📌 *Escenario:* Operar movimientos amplios guiados por H4, confirmados por H1.

*1️⃣ Lectura de contexto estructural*
• H4 (macro): *{dir_h4}*
  → Define la dirección principal del swing.
• H1 (intradía): *{dir_h1}*
  → Muestra cómo el precio construye la transición hacia el movimiento grande.

*2️⃣ Rangos clave para el swing*
• 🟣 Rango H4 (macro swing): `{rango_h4_txt}`
  → Zona donde identificamos si el precio está en descuento (parte baja) o premium (parte alta).
• 🔵 Rango H1 (estructura de transición): `{rango_h1_txt}`
  → Donde se ve el proceso de acumulación / distribución que prepara el swing.

*3️⃣ Condición CLAVE del swing TESLA*
• El swing no se activa solo porque H4 está en una dirección.
• Necesitamos:
  1. *Profundidad en H4*: el precio se adentra en el rango (descuento/premium).
  2. *BOS + CIERRE de H1*:
     - Quiebre y CIERRE de H1 por encima del último alto clave → swing alcista.
     - Quiebre y CIERRE de H1 por debajo del último bajo clave → swing bajista.
  3. Luego, el pullback sobre esa ruptura es la zona donde se estructura la entrada swing.

*4️⃣ Diferencia con el scalping*
• Scalping:
  - Opera tramos dentro del rango intradía (H1) con gatillos en M5/M3/M1.
  - Depende mucho de la ventana de sesión (primeras horas).
• Swing:
  - Opera el “cambio de capítulo” estructural.
  - Es menos dependiente de la hora exacta; más dependiente de la *estructura H4 + validación H1*.

*5️⃣ Recomendaciones operativas TESLA para swing*
• Priorizar:
  - H4 en zona de interés (parte extrema del rango).
  - BOS de H1 con CIERRE sólido.
  - Entrada en el retroceso controlado posterior a ese BOS.
• Gestión:
  - RRR amplio (1:3 o más).
  - Parciales en zonas de liquidez importantes.
  - SL protegido bajo/encima del punto estructural validado por H1.

El swing es donde la historia de H4 se confirma a través de la decisión de H1.
No es una vela bonita: es estructura limpia validada con quiebre y cierre.
"""
        return texto

    # ========================================================
    # 💤 Tipo desconocido: devolvemos algo genérico
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
