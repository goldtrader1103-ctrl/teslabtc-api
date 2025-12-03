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
    "El éxito llega cuando la disciplina se vuelve natural.",
    "Un POI es la estación donde el precio recoge combustible para continuar su viaje. Si el tren no se detiene allí, tú tampoco te subes.",
    "El bos siempre sera el mejor gatillo en el mercado"
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
    # 🧭 DIRECCIÓN GENERAL — RANGO REAL (v5.3.4)
    #   D/H4/H1 muestran SOLO estado + BOS + rango actual.
    # --------------------------------------------------------
    d  = estructura.get("D", {}) or {}
    h4 = estructura.get("H4", {}) or {}
    h1 = estructura.get("H1", {}) or {}

    d_estado  = str(d.get("estado", "—")).upper()
    h4_estado = str(h4.get("estado", "—")).upper()
    h1_estado = str(h1.get("estado", "—")).upper()

    d_bos  = d.get("BOS", "—")
    h4_bos = h4.get("BOS", "—")
    h1_bos = h1.get("BOS", "—")

    # Rangos operativos:
    # 1) Preferimos lo inyectado en estructura (RANGO_HIGH/LOW).
    # 2) Si por alguna capa se pierden, hacemos fallback a zonas_detectadas.
    d_hi  = d.get("RANGO_HIGH", zonas.get("D_HIGH"))
    d_lo  = d.get("RANGO_LOW",  zonas.get("D_LOW"))
    h4_hi = h4.get("RANGO_HIGH", zonas.get("H4_HIGH"))
    h4_lo = h4.get("RANGO_LOW",  zonas.get("H4_LOW"))
    h1_hi = h1.get("RANGO_HIGH", zonas.get("H1_HIGH"))
    h1_lo = h1.get("RANGO_LOW",  zonas.get("H1_LOW"))


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
    asia_low  = zonas.get("ASIAN_LOW")
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
            f"{setup.get('nivel','SETUP ACTIVO')}\n"
            f"{setup.get('contexto','')}\n"
            f"Zona de entrada: {setup.get('zona_entrada','—')}\n"
            f"SL: {setup.get('sl','—')}\n"
            f"TP1: {setup.get('tp1','—')} | TP2: {setup.get('tp2','—')}\n"
            f"Comentario: {setup.get('comentario','')}"
        )
    else:
        setup_txt = "⏳ Sin setup activo — esperando confirmaciones estructurales (BOS + POI + Sesión NY)."

    # --------------------------------------------------------
    # 📊 ESCENARIOS OPERATIVOS (con confirmaciones por escenario)
    # --------------------------------------------------------
    def _detalle_escenario(esc, zonas, titulo, emoji):
        if not esc:
            return ""

        tipo = esc.get("tipo", "Neutro")
        prob = esc.get("probabilidad", "Media")
        riesgo = esc.get("riesgo", "Medio")
        texto_base = esc.get("descripcion") or esc.get("texto") or ""
        contexto = esc.get("contexto") or ""
        poi_h1 = zonas.get("POI_H1")
        poi_h4 = zonas.get("POI_H4")
        ob_h1  = zonas.get("OB_H1")
        ob_h4  = zonas.get("OB_H4")

        zona_ref = (
            poi_h1 or poi_h4 or
            ob_h1  or ob_h4  or
            "zona institucional (POI/OB) relevante en H1/H4"
        )

        pdh = zonas.get("PDH")
        pdl = zonas.get("PDL")
        ah  = zonas.get("ASIAN_HIGH")
        al  = zonas.get("ASIAN_LOW")

        if tipo == "Compra":
            targets = []
            if pdh: targets.append(f"PDH: {pdh}")
            if ah:  targets.append(f"ASIAN HIGH: {ah}")
            target_txt = ", ".join(targets) if targets else "zonas de liquidez superior (máximos previos)"
            idea_operativa = (
                f"Buscar largos dentro de **{zona_ref}**, "
                f"con objetivo principal en {target_txt}."
            )
            sl_txt = "SL por debajo del OB o del último mínimo relevante en H1."
        elif tipo == "Venta":
            targets = []
            if pdl: targets.append(f"PDL: {pdl}")
            if al:  targets.append(f"ASIAN LOW: {al}")
            target_txt = ", ".join(targets) if targets else "zonas de liquidez inferior (mínimos previos)"
            idea_operativa = (
                f"Buscar cortos dentro de **{zona_ref}**, "
                f"con objetivo principal en {target_txt}."
            )
            sl_txt = "SL por encima del OB o del último máximo relevante en H1."
        else:
            idea_operativa = "Contexto neutro / en rango: esperar BOS claro en una zona institucional antes de operar."
            sl_txt = "SL siempre fuera de la zona institucional usada para la entrada."

        confs_favor = esc.get("confs_favor", []) or []
        confs_pend  = esc.get("confs_pendientes", []) or []

        lineas = [
            f"{emoji} {titulo} ({tipo} | riesgo {riesgo}, probabilidad {prob})",
        ]

        if texto_base:
            lineas.append(texto_base)
        if contexto:
            lineas.append(f"📌 Contexto: {contexto}")

        lineas.extend([
            f"📥 Zona de entrada orientativa: {zona_ref}",
            f"⛔ Zona de invalidación (SL orientativo): {sl_txt}",
            "🎯 Gestión sugerida: TP1 en 1:2 RRR | TP2 en 1:3 RRR si la estructura se mantiene a favor.",
        ])

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
            lineas.append("📎 Recomendación: NO ejecutar mientras estas confirmaciones sigan pendientes en la zona de entrada.")

        return "\n".join(lineas)

    escenarios_txt = []
    esc1_txt = _detalle_escenario(esc1, zonas, "Escenario de Continuación", "🟢")
    esc2_txt = _detalle_escenario(esc2, zonas, "Escenario de Corrección / contra-tendencia", "🔴")

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
