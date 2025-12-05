# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.5 PRO)
# ============================================================
# - No modifica la lógica de la API, sólo el mensaje final.
# - Dirección D muestra RANGO en vez de HH/LL teóricos.
# - Zonas: PDH/PDL + Asia + OB/POI.
# - Confirmaciones sólo dentro de cada ESCENARIO (no bloque aparte).
# - Escenarios SIEMPRE: Continuación y Corrección (fallback si vienen vacíos).
# - El SETUP TESLABTC aparece DEBAJO de los escenarios
#   y sólo cuando hay entrada activa.
# - Protección Markdown para Telegram.
# ============================================================

import random, re
from datetime import datetime
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
# 📊 DETALLE DE ESCENARIO (helper)
# ============================================================
def _detalle_escenario(esc, zonas, titulo_base, emoji):
    if not esc:
        return ""

    tipo = esc.get("tipo", "Neutro")
    prob = esc.get("probabilidad", "Media")
    riesgo = esc.get("riesgo", "Medio")
    texto_base = esc.get("descripcion") or esc.get("texto") or ""
    contexto = esc.get("contexto") or ""

    # Dirección textual según el tipo
    if tipo == "Compra":
        dir_txt = "Alcista"
        sign = +1
    elif tipo == "Venta":
        dir_txt = "Bajista"
        sign = -1
    else:
        dir_txt = "Neutro"
        sign = 0

    titulo = titulo_base
    if dir_txt != "Neutro":
        titulo = f"{titulo_base} {dir_txt}"

    # POI/OB prioritario para la zona de entrada
    poi_h1 = zonas.get("POI_H1")
    poi_h4 = zonas.get("POI_H4")
    ob_h1 = zonas.get("OB_H1")
    ob_h4 = zonas.get("OB_H4")

    zona_txt = poi_h1 or poi_h4 or ob_h1 or ob_h4

    entry_low = entry_high = sl_price = None

    if isinstance(zona_txt, str):
        try:
            norm = (
                zona_txt.replace("–", "-")
                        .replace("—", "-")
                        .replace("−", "-")
            )
            nums = [float(x.strip()) for x in norm.split("-") if x.strip()]
            if len(nums) >= 2:
                entry_low, entry_high = min(nums), max(nums)
                # SL según tipo
                if tipo == "Compra":
                    sl_price = entry_low
                elif tipo == "Venta":
                    sl_price = entry_high
        except Exception:
            pass

    # TP1 / TP2 por múltiplos de R
    tp1 = tp2 = tp3 = None
    entry_price = None

    if (
        entry_low is not None
        and entry_high is not None
        and sl_price is not None
        and sign != 0
    ):
        entry_price = (entry_low + entry_high) / 2.0
        r = abs(entry_price - sl_price)
        if r > 0:
            tp1 = entry_price + sign * r
            tp2 = entry_price + sign * 2 * r

    # TP3 por zona de liquidez
    pdh = zonas.get("PDH")
    pdl = zonas.get("PDL")
    ah = zonas.get("ASIAN_HIGH")
    al = zonas.get("ASIAN_LOW")

    if sign > 0:  # Compras → liquidez superior
        candidatos = [x for x in (pdh, ah) if isinstance(x, (int, float, float))]
        if candidatos:
            tp3 = max(candidatos)
    elif sign < 0:  # Ventas → liquidez inferior
        candidatos = [x for x in (pdl, al) if isinstance(x, (int, float, float))]
        if candidatos:
            tp3 = min(candidatos)

    lineas: List[str] = [
        f"{emoji} {titulo} ({tipo} | riesgo {riesgo}, probabilidad {prob})",
    ]

    if texto_base:
        lineas.append(texto_base)
    if contexto:
        lineas.append(f"📌 Contexto: {contexto}")

    # Zona de entrada + SL/TP en PRECIOS
    if entry_low is not None and entry_high is not None:
        lineas.append(
            f"📥 Zona de entrada orientativa: {entry_low:,.2f}–{entry_high:,.2f}"
        )
    else:
        linea_zona = zona_txt or "zona institucional TESLABTC en H1/H4"
        lineas.append(f"📥 Zona de entrada orientativa: {linea_zona}")

    if sl_price is not None:
        lineas.append(f"⛔ Zona de invalidación (SL orientativo): {sl_price:,.2f}")
    else:
        lineas.append("⛔ Zona de invalidación (SL): último alto/bajo estructural en H1.")

    # TPs
    tp_lines = []
    if tp1 is not None:
        tp_lines.append(f"TP1: {tp1:,.2f} (≈ 1:1)")
    if tp2 is not None:
        tp_lines.append(f"TP2: {tp2:,.2f} (≈ 1:2)")
    if tp3 is not None:
        tp_lines.append(f"TP3: {tp3:,.2f} (siguiente zona de liquidez)")

    if tp_lines:
        lineas.append("🎯 Objetivos principales: " + " | ".join(tp_lines))
    else:
        lineas.append("🎯 Objetivos principales: esperar definición clara de estructura.")

    # Gestión estándar TESLABTC
    lineas.append(
        "💼 Gestión sugerida: mover a BE en TP1 y asegurar 50%; dejar correr hacia TP2/TP3 sólo si la estructura se mantiene a favor."
    )

    confs_favor = esc.get("confs_favor", []) or []
    confs_pend = esc.get("confs_pendientes", []) or []

    if confs_favor:
        lineas.append("")
        lineas.append("✅ Confirmaciones a favor del escenario:")
        for c in confs_favor:
            lineas.append(f"   • {c}")

    if confs_pend:
        lineas.append("")
        lineas.append("⚠️ Confirmaciones que FALTAN antes de ejecutar con confianza:")
        for c in confs_pend:
            lineas.append(f"   • {c}")
        lineas.append("")
        lineas.append(
            "📎 Recomendación: NO ejecutar mientras estas confirmaciones sigan pendientes en la zona de entrada."
        )

    return "\n".join(lineas)


# ============================================================
# 🧩 FORMATEADOR PREMIUM
# ============================================================
def construir_mensaje_operativo(data):
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    sesion = data.get("sesión", "—")
    precio = data.get("precio_actual", "—")
    estructura = data.get("estructura_detectada", {}) or {}
    zonas = data.get("zonas_detectadas", {}) or {}
    # Confirmaciones crudas de la API
    confs = data.get("confirmaciones", {}) or {}

    # Escenarios que vienen desde la API (pueden venir vacíos o None)
    esc1 = data.get("escenario_1")
    esc2 = data.get("escenario_2")

    setup = data.get("setup_tesla", {}) or {}
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    )

    # --------------------------------------------------------
    # Fallback de escenarios si la API no envía nada útil
    # --------------------------------------------------------
    def _fallback_escenario(nombre_visible):
        confs_favor = [k for k, v in confs.items() if str(v).startswith("✅")]
        confs_pend = [k for k, v in confs.items() if not str(v).startswith("✅")]
        return {
            "tipo": "Neutro",
            "probabilidad": "Media",
            "riesgo": "Medio",
            "texto": (
                f"{nombre_visible}: el precio está en fase de transición TESLABTC. "
                "Esperar que llegue a un POI (banda 61.8–88.6) y forme un BOS "
                "claro en M15/M5 antes de ejecutar."
            ),
            "contexto": data.get("contexto_general", ""),
            "confs_favor": confs_favor,
            "confs_pendientes": confs_pend,
        }

    if not esc1 or not isinstance(esc1, dict):
        esc1 = _fallback_escenario("Escenario de Continuación")

    if not esc2 or not isinstance(esc2, dict):
        esc2 = _fallback_escenario("Escenario de Corrección / contra-tendencia")

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

    # Rangos operativos: primero lo que viene en la estructura,
    # si no, fallback a zonas_detectadas.
    d_hi = d.get("RANGO_HIGH", zonas.get("D_HIGH"))
    d_lo = d.get("RANGO_LOW", zonas.get("D_LOW"))
    h4_hi = h4.get("RANGO_HIGH", zonas.get("H4_HIGH"))
    h4_lo = h4.get("RANGO_LOW", zonas.get("H4_LOW"))
    h1_hi = h1.get("RANGO_HIGH", zonas.get("H1_HIGH"))
    h1_lo = h1.get("RANGO_LOW", zonas.get("H1_LOW"))

    d_line = (
        f"📈 D: {d_estado} ({d_bos}) | RANGO: {d_hi}–{d_lo}"
        if d_hi is not None and d_lo is not None
        else f"📈 D: {d_estado} ({d_bos})"
    )
    h4_line = (
        f"⚙️ H4: {h4_estado} ({h4_bos}) | RANGO: {h4_hi}–{h4_lo}"
        if h4_hi is not None and h4_lo is not None
        else f"⚙️ H4: {h4_estado} ({h4_bos})"
    )
    h1_line = (
        f"🔹 H1: {h1_estado} ({h1_bos}) | RANGO: {h1_hi}–{h1_lo}"
        if h1_hi is not None and h1_lo is not None
        else f"🔹 H1: {h1_estado} ({h1_bos})"
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
    asia_low = zonas.get("ASIAN_LOW")
    if asia_high and asia_low:
        zonas_txt.append(f"• ASIAN HIGH: {asia_high} | • ASIAN LOW: {asia_low}")
    elif asia_high or asia_low:
        zonas_txt.append(
            f"• ASIAN HIGH: {asia_high or '—'} | • ASIAN LOW: {asia_low or '—'}"
        )
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
    # ⚙️ SETUP TESLABTC (sólo si hay entrada activa)
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
        setup_txt = ""

    # Este bloque se incrusta DESPUÉS de los escenarios
    setup_block = ""
    if setup_txt:
        setup_block = f"""

⚙️ **SETUP TESLABTC (M5 en POI H1)**
──────────────────────────────
{setup_txt}
"""

    # --------------------------------------------------------
    # 📊 ESCENARIOS OPERATIVOS (con confirmaciones por escenario)
    # --------------------------------------------------------
    escenarios_txt: List[str] = []

    esc1_txt = _detalle_escenario(esc1, zonas, "Escenario de Continuación", "🟢")
    esc2_txt = _detalle_escenario(
        esc2, zonas, "Escenario de Corrección / contra-tendencia", "🔴"
    )

    if esc1_txt:
        escenarios_txt.append(esc1_txt)
    if esc2_txt:
        if escenarios_txt:
            escenarios_txt.append("")
        escenarios_txt.append(esc2_txt)

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

📊 **ESCENARIOS OPERATIVOS**
──────────────────────────────
{escenarios_final}{setup_block}

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
    fecha = data.get("fecha", "—")
    activo = data.get("activo", "BTCUSDT")
    precio = data.get("precio_actual", "—")
    sesion = data.get("sesión", "—")
    estructura = data.get("estructura_detectada", {}) or {}
    d = estructura.get("D", {}) or {}
    h4 = estructura.get("H4", {}) or {}
    h1 = estructura.get("H1", {}) or {}

    reflex = frase_motivacional()
    slogan = data.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    )

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
• Zonas institucionales (PDH/PDL/Asia/OB/POI)
• Escenarios operativos y Setup TESLABTC
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
    text = re.sub(r"(?<!\*)\*(?!\*)", "✱", text)
    # guiones bajos sueltos → ‗
    text = re.sub(r"(?<!_)_(?!_)", "‗", text)
    # corchetes y paréntesis → variantes seguras
    text = (
        text
        .replace("[", "〔").replace("]", "〕")
        .replace("(", "（").replace(")", "）")
    )
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
