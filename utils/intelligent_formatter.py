# ============================================================
# 🧠 TESLABTC.KG — INTELLIGENT FORMATTER MODULE
# Genera conclusiones precisas, amigables y coherentes
# ============================================================

from datetime import datetime

def construir_mensaje_operativo(escenario: dict) -> str:
    """
    Recibe la data cruda del análisis (estructuras, BOS, POI, etc.)
    y devuelve un texto listo para mostrar al usuario.
    """

    # 🕒 Sesión y hora
    hora = datetime.now().strftime("%H:%M")
    sesion = escenario.get("sesion", "Desconocida")

    # 📈 Tendencias
    tendencia_h1 = escenario.get("tendencia_h1", "Indefinida")
    tendencia_m15 = escenario.get("tendencia_m15", "Indefinida")

    # 📊 Elementos estructurales
    bos = escenario.get("bos", "Sin BOS")
    poi = escenario.get("poi", {})
    fvg = escenario.get("fvg", None)
    volumen = escenario.get("volumen", 0.0)

    # ============================================================
    # 🧩 Lógica contextual (precisión y coherencia)
    # ============================================================
    direccion = "alcista" if tendencia_h1 == "alcista" else "bajista"
    direccion_icon = "📈" if direccion == "alcista" else "📉"

    mensaje = f"{direccion_icon} *ESCENARIO TESLABTC.KG — Sesión {sesion} ({hora})*\n\n"
    mensaje += f"🧭 **Dirección general:** {tendencia_h1.upper()}\n"
    mensaje += f"🪞 **Tendencia interna (M15):** {tendencia_m15}\n"

    # POI o FVG
    if poi:
        mensaje += f"📍 **Zona de interés:** {poi.get('nombre', 'POI detectado')} ({poi.get('nivel', 'sin nivel')})\n"
    elif fvg:
        mensaje += f"⚡ **FVG detectado:** {fvg}\n"
    else:
        mensaje += f"⚠️ Sin zonas activas relevantes.\n"

    # BOS
    if bos.lower() == "alcista":
        mensaje += "🔹 Se confirma un **BOS alcista**, posible continuación del impulso.\n"
    elif bos.lower() == "bajista":
        mensaje += "🔹 Se confirma un **BOS bajista**, posible inicio de corrección o retroceso.\n"
    else:
        mensaje += "🔸 No hay BOS confirmado en el marco operativo.\n"

    # ============================================================
    # 🎯 Conclusión final (humanizada e inteligente)
    # ============================================================
    if tendencia_h1 == tendencia_m15 == bos:
        conclusion = (
            "✅ *Alta confluencia:* el precio mantiene alineación estructural en H1 y M15. "
            "Podría darse una entrada operativa tras retroceso controlado."
        )
    elif tendencia_h1 != tendencia_m15:
        conclusion = (
            "⚠️ *Contradicción temporal:* la estructura interna no acompaña la tendencia general. "
            "Esperar confirmación antes de ejecutar cualquier entrada."
        )
    elif volumen < 0.5:
        conclusion = (
            "💤 *Volumen débil:* el movimiento actual carece de fuerza institucional. "
            "Evita anticipar rupturas sin validación adicional."
        )
    else:
        conclusion = (
            "🤔 *Escenario neutro:* aún no hay suficientes confirmaciones para una dirección clara. "
            "Monitorear zonas marcadas."
        )

    # ============================================================
    # 📊 Coherencia e interpretación
    # ============================================================
    confiabilidad = _calcular_confiabilidad(escenario)
    mensaje += f"\n🎯 **Nivel de confiabilidad:** {confiabilidad}\n\n"
    mensaje += f"📘 *Conclusión TESLABTC.KG:*\n{conclusion}"

    return mensaje


def _calcular_confiabilidad(data: dict) -> str:
    """Calcula un índice simple de coherencia estructural."""
    score = 0
    if data.get("tendencia_h1") == data.get("tendencia_m15"): score += 0.3
    if data.get("bos") == data.get("tendencia_m15"): score += 0.3
    if data.get("poi"): score += 0.2
    if data.get("sesion") == "NY": score += 0.2
    total = round(score, 2)

    if total >= 0.8: return "Alta ✅"
    elif total >= 0.5: return "Media ⚠️"
    else: return "Baja ❌"
