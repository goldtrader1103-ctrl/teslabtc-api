# ============================================================
# 🧠 TESLABTC.KG — Intelligent Formatter (v5.4 PRO FINAL)
# ============================================================
# Integración completa: Zonas, Escenarios, Confirmaciones contextuales,
# Asia, OB/POI, Reflexión dinámica y protección Markdown Telegram.
# ============================================================

import random, re
from datetime import datetime

# ============================================================
# 🌟 FRASES MOTIVACIONALES TESLABTC (100)
# ============================================================
FRASES_TESLA = [
    "Tu mentalidad define tu rentabilidad.",
    "Disciplina no es hacer lo que amas, sino hacerlo incluso cuando no quieres.",
    "El mercado premia la paciencia, no la prisa.",
    "Cada clic debe tener un propósito, no una emoción.",
    "Tu constancia es tu verdadero edge.",
    "El dinero sigue a la claridad, no a la confusión.",
    "Operar menos es ganar más.",
    "Si no tienes un plan, eres parte del plan de otro.",
    "No se trata de acertar siempre, sino de perder correctamente.",
    "Ser trader es dominarse a uno mismo, no al mercado.",
    "El trading no se domina; se respeta cada día.",
    "Cierra el gráfico, abre la mente.",
    "Pierdes solo cuando dejas de aprender.",
    "Un setup no te define, tu disciplina sí.",
    "La consistencia no se busca, se construye.",
    "El impulso emocional es el enemigo del capital.",
    "Saber esperar es la mayor forma de poder.",
    "Ganarás cuando dejes de buscar dinero y empieces a buscar calidad.",
    "Cada pérdida enseña algo que una ganancia no podría.",
    "Ser paciente no es debilidad, es inteligencia emocional.",
    "Una semana disciplinada vale más que un mes de impulsos.",
    "La constancia vence a la motivación pasajera.",
    "No necesitas operar más, necesitas operar mejor.",
    "Tu plan de trading es tu escudo, no lo rompas.",
    "El ego es el costo oculto más caro del trading.",
    "No hay mal trade si sigues el plan.",
    "El mercado no se equivoca, tú interpretas mal.",
    "El éxito en trading no se mide por dinero, sino por control.",
    "Tus emociones son parte del sistema; apréndelas, no las ignores.",
    "Cada stop loss bien puesto es una victoria silenciosa.",
    "Ser profesional es aburrido: sigue el proceso.",
    "No te compares, cada cuenta tiene su camino.",
    "La paciencia paga dividendos invisibles.",
    "El mercado te paga por esperar, no por actuar.",
    "Domina una sola estrategia y tendrás libertad.",
    "El proceso es lento, pero el resultado es eterno.",
    "No corras tras el precio, deja que el precio venga a ti.",
    "El setup ideal no existe, la ejecución disciplinada sí.",
    "Tu mente es tu primer mercado.",
    "La verdadera fortaleza es cerrar la plataforma a tiempo.",
    "Si no puedes controlar una pérdida, no mereces una ganancia.",
    "Cada trade tiene una lección; solo si la anotas, la capitalizas.",
    "El mejor trader no es el que más gana, sino el que menos pierde por error.",
    "Aprende a estar cómodo en la espera.",
    "Sin control emocional no hay estrategia que funcione.",
    "No busques operar, busca confirmar.",
    "El silencio del gráfico es tu mayor aliado.",
    "El precio habla, pero pocos escuchan.",
    "Tu bitácora es el espejo de tu progreso.",
    "No todo movimiento es una oportunidad.",
    "Deja que la estructura valide tu idea, no tu deseo.",
    "El mercado siempre tendrá la última palabra, y está bien.",
    "Tus resultados reflejan tu disciplina, no tu suerte.",
    "La gestión de riesgo no limita, te protege.",
    "Operar sin esperar confirmación es como saltar sin paracaídas.",
    "Tu trabajo no es adivinar, es reaccionar con criterio.",
    "Cada día disciplinado es un paso más cerca del control total.",
    "La constancia vence al talento indisciplinado.",
    "Si no puedes medirlo, no puedes mejorarlo.",
    "Aprende a no operar: ahí está la verdadera libertad.",
    "El trader exitoso no busca trades, busca razones.",
    "La calma es el arma más poderosa en una sesión volátil.",
    "Tu control es tu ventaja competitiva.",
    "El respeto al plan genera resultados exponenciales.",
    "No operes por aburrimiento, opera por confirmación.",
    "Cada sesión cerrada según el plan es una victoria.",
    "Controla el impulso, mantén la dirección.",
    "El éxito se construye en silencio, sesión a sesión.",
    "Ser consistente es aburrido, pero es lo que paga.",
    "Tu límite es la calidad de tu paciencia.",
    "Cada día sin sobreoperar es un día ganado.",
    "Un buen trader pierde poco y aprende mucho.",
    "El trading recompensa a los que siguen reglas, no impulsos.",
    "No necesitas más setups, necesitas más enfoque.",
    "El autocontrol no se estudia, se entrena en cada trade.",
    "Tu única competencia es tu versión de ayer.",
    "No esperes motivación, crea disciplina.",
    "Sin registro no hay mejora.",
    "El gráfico no cambia, tú sí.",
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
    esc1 = data.get("escenario_1", {})
    esc2 = data.get("escenario_2", {})
    setup = data.get("setup_tesla", {})
    reflexion = data.get("reflexion") or frase_motivacional()
    slogan = data.get("slogan", "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    # --------------------------------------------------------
    # 🧭 DIRECCIÓN GENERAL
    # --------------------------------------------------------
    d, h4, h1 = estructura.get("D", {}), estructura.get("H4", {}), estructura.get("H1", {})
    direccion = (
        f"📈 D: {d.get('estado','—').upper()} ({d.get('BOS','—')}) | HH: {d.get('HH','—')} | LL: {d.get('LL','—')}\n"
        f"⚙️ H4: {h4.get('estado','—').upper()} ({h4.get('BOS','—')}) | HH: {h4.get('HH','—')} | LL: {h4.get('LL','—')}\n"
        f"🔹 H1: {h1.get('estado','—').upper()} ({h1.get('BOS','—')}) | HH: {h1.get('HH','—')} | LL: {h1.get('LL','—')}"
    )

    # --------------------------------------------------------
    # 💎 ZONAS DE LIQUIDEZ Y ASIA
    # --------------------------------------------------------
    zonas_txt = []
    if zonas.get("PDH") or zonas.get("PDL"):
        zonas_txt.append(f"• PDH: {zonas.get('PDH','—')} | • PDL: {zonas.get('PDL','—')}")
    asia_high, asia_low = zonas.get("ASIAN_HIGH"), zonas.get("ASIAN_LOW")
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
    zonas_final = "\n".join(zonas_txt)

    # --------------------------------------------------------
    # ✅ CONFIRMACIONES CON CONTEXTO
    # --------------------------------------------------------
    conf_desc = {
        "macro": "Tendencia macro (D) a favor del contexto general.",
        "intradía": "Dirección intradía (H1/H4) coherente con la estructura actual.",
        "ob_valido": "OB válido y no mitigado dentro de la sesión.",
        "barrida_pdh": "Barrida de liquidez superior detectada.",
        "bajo_asia": "Reacción en bajo asiático o zona inferior relevante."
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
            f"📈 Zona: {setup.get('zona_entrada','—')} | ⛔ SL: {setup.get('sl','—')} | 🎯 TP1: {setup.get('tp1','—')} | 🎯 TP2: {setup.get('tp2','—')}\n"
            f"{setup.get('comentario','')}"
        )
    else:
        setup_txt = "⏳ Sin setup activo — esperando confirmaciones estructurales (BOS + POI + Sesión NY)."

    # --------------------------------------------------------
    # 📊 ESCENARIOS
    # --------------------------------------------------------
    escenarios_txt = []
    if esc1 or esc2:
        if esc1:
            escenarios_txt.append(f"🟢 *Escenario de Continuación:* {esc1.get('descripcion','—')}")
        if esc2:
            escenarios_txt.append(f"🔴 *Escenario de Corrección:* {esc2.get('descripcion','—')}")
    escenarios_final = "\n".join(escenarios_txt) if escenarios_txt else "—"

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
    estructura = data.get("estructura_detectada",{})
    d, h4, h1 = estructura.get("D",{}), estructura.get("H4",{}), estructura.get("H1",{})
    reflex = frase_motivacional()
    slogan = data.get("slogan","✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")
    return f"""
📋 **TESLABTC.KG — Análisis Gratuito**
──────────────────────────────
📅 Fecha: {fecha}
💰 Activo: {activo}
💵 Precio: {precio}
🕒 Sesión: {sesion}
🧭 D: {d.get('estado','—').upper()} | H4: {h4.get('estado','—').upper()} | H1: {h1.get('estado','—').upper()}
💭 {reflex}
⚠️ Accede a TESLABTC Premium para ver:
• Confirmaciones estructurales
• Zonas institucionales (PDH/PDL/Asia)
• Setup activo y conclusiones dinámicas
{slogan}
"""

# ============================================================
# 🛡️ SAFE MARKDOWN
# ============================================================
def safe_markdown(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'(?<!\*)\*(?!\*)', '✱', text)
    text = re.sub(r'(?<!_)_(?!_)', '‗', text)
    text = text.replace("[","〔").replace("]","〕").replace("(","（").replace(")","）")
    return text
# ============================================================
# 🧹 ALIAS DE COMPATIBILIDAD (para versiones previas de main.py)
# ============================================================
def limpiar_texto(text: str) -> str:
    """Compatibilidad con versiones antiguas — mantiene limpieza de texto."""
    if not isinstance(text, str):
        return ""
    text = text.replace("  ", " ").replace(" | ", " |").strip()
    return text
