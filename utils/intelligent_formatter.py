from __future__ import annotations
# ============================================================
# 🧠 TESLABTC.KG — FORMATEADOR INTELIGENTE DE TEXTO (Free + Premium)
# ============================================================

import unicodedata
import random
from typing import Dict

__all__ = ["construir_mensaje_free", "construir_mensaje_operativo", "limpiar_texto"]

# ------------------------------------------------------------
# 🧹 LIMPIEZA GENERAL DE TEXTO
# ------------------------------------------------------------
def limpiar_texto(valor: str) -> str:
    """Normaliza y limpia texto sin eliminar emojis."""
    if not isinstance(valor, str):
        valor = str(valor)
    texto = unicodedata.normalize("NFKC", valor)
    reemplazos = {
        "Ã³": "ó", "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ãº": "ú", "Ã±": "ñ",
        "â": "'", "â": "-", "â": "\"", "â": "\"", "â¢": "•",
        "â": "✔️", "â": "❌", "â¡": "⚡", "â": "⚠️",
        "â": "✈️", "â": "☕", "â³": "⏳", "â": "♂️",
        "â": "♀️", "Â": "", "â¦": "…"
    }
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore").strip()


# ------------------------------------------------------------
# 🌟 FRASES DE REFLEXIÓN
# ------------------------------------------------------------
REFLEXIONES = [
    "El mercado recompensa la paciencia y castiga la impulsividad.",
    "Cada trade perdido enseña más que diez ganados.",
    "Operar menos, pensar más: el secreto de la consistencia.",
    "El análisis sin gestión es como un mapa sin brújula.",
    "No hay setups perfectos, solo ejecuciones disciplinadas.",
    "Esperar la confirmación correcta siempre paga.",
    "La calma en la zona es la ventaja del trader profesional.",
    "Tu resultado de hoy no define tu capacidad, define tu control emocional.",
    "La estructura manda, el ego obedece.",
    "El precio siempre cuenta la historia, si sabes escucharla."
]


# ------------------------------------------------------------
# 📄 FREE — estilo explicativo con secciones bloqueadas
# ------------------------------------------------------------
def construir_mensaje_free(data: dict) -> str:
    fecha   = data.get("fecha", "—")
    activo  = "BTCUSDT"
    sesion  = data.get("sesión") or data.get("sesion", "New York")
    tfs     = "D | H4 | H1 | M15"
    precio  = data.get("precio_actual", "—")
    reflexion = random.choice(REFLEXIONES)

    est = data.get("estructura_detectada", {})
    d, h4, h1 = est.get("D", {}), est.get("H4", {}), est.get("H1", {})
    tend = (d.get("estado") or h1.get("estado") or "—").upper()

    zonas = data.get("zonas", {})
    high_macro = zonas.get("D_HIGH", "—")
    low_macro  = zonas.get("D_LOW",  "—")

    cuerpo = (
        f"📅 Fecha: {fecha}\n"
        f"💰 Activo: {activo}\n"
        f"💵 Precio actual: {precio}\n"
        f"🕒 Sesión: {sesion}\n"
        f"📊 Temporalidades analizadas: {tfs}\n"
        "________________________________________\n"
        "🧭 DIRECCIÓN GENERAL\n"
        f"Tendencia principal: {tend}\n"
        "Contexto:\n"
        f"• High macro: {high_macro} USDT • Low macro: {low_macro} USDT\n"
        "• Rango actual: dentro del bloque de demanda diario (OB D), con posible reacción inminente.\n\n"
        "📍 ZONAS RELEVANTES \"DESBLOQUEA CON PREMIUM\"\n"
        "✅ CONFIRMACIONES CLAVE \"DESBLOQUEA CON PREMIUM\"\n"
        "🟢 ESCENARIO 1 \"DESBLOQUEA CON PREMIUM\"\n"
        "🔴 ESCENARIO 2 \"DESBLOQUEA CON PREMIUM\"\n"
        "🧠 CONCLUSIÓN OPERATIVA: \"DESBLOQUEA CON PREMIUM\"\n\n"
        f"📓 Reflexión TESLABTC A.P.: 💭 {reflexion}\n"
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    )
    return limpiar_texto(cuerpo)


# ------------------------------------------------------------
# 🎨 PREMIUM — reporte operativo completo
# ------------------------------------------------------------
def construir_mensaje_operativo(data: dict) -> str:
    """
    Render amigable para Premium con 2 escenarios:
    - Escenario 1: a favor de tendencia (alta prob/bajo riesgo)
    - Escenario 2: contra-tendencia (media/baja prob; mayor riesgo)
    """
    try:
        fecha   = data.get("fecha", "—")
        sesion  = data.get("sesion", data.get("sesión", "—"))
        activo  = data.get("activo", data.get("simbolo", "BTCUSDT"))
        precio  = data.get("precio_actual", "—")
        zonas   = data.get("zonas_detectadas", data.get("zonas", {})) or {}
        confs   = data.get("confirmaciones", {}) or {}
        esc1    = data.get("escenario_1", {}) or {}
        esc2    = data.get("escenario_2", {}) or {}
        concl   = data.get("conclusion_general", data.get("conclusion", "—"))
        reflexion = random.choice(REFLEXIONES)

        def _fmt_confs(d: Dict[str, str]) -> str:
            if not d:
                return "—"
            return "\n".join([f"• {k}: {v}" for k, v in d.items()])

        def _fmt_setup(esc: dict) -> str:
            s = esc.get("setup", {})
            if not s:
                return "⏳ Sin setup válido. Intenta en unos minutos."
            return (
                f"📍 Zona de entrada: {s.get('zona_entrada','—')}\n"
                f"⛔ SL: {s.get('sl','—')}\n"
                f"🎯 TP1: {s.get('tp1','—')}\n"
                f"🎯 TP2: {s.get('tp2','—')}\n"
                f"🎯 TP3: {s.get('tp3','—')}\n"
                f"🧭 Observación: {s.get('observacion','—')}"
            )

        texto = (
            "📋 *REPORTE TESLABTC A.P. – Sesión NY*\n"
            "──────────────────────────────\n\n"
            f"📅 Fecha: {fecha}\n"
            f"💰 Activo: {activo}\n"
            f"💵 Precio actual: {precio}\n"
            f"🕒 Sesión: {sesion}\n"
            "📊 Temporalidades analizadas: D | H4 | H1 | M15\n\n"
            "🧭 *DIRECCIÓN GENERAL*\n\n"
            "Tendencia principal: (calculada por estructura D/H4/H1)\n"
            "Contexto: (explicado por el motor de escenarios y zonas)\n\n"
            "📍 *ZONAS RELEVANTES*\n"
            + ("\n".join([f"- {k}: {v}" for k, v in zonas.items()]) if zonas else "—")
            + "\n\n"
            "✅ *CONFIRMACIONES CLAVE*\n"
            f"{_fmt_confs(confs)}\n\n"
            "🟢 *ESCENARIO 1 — A favor de tendencia*\n"
            f"Tipo: {esc1.get('tipo','—')} | Probabilidad: {esc1.get('probabilidad','—')} | Riesgo: {esc1.get('riesgo','—')}\n"
            f"{esc1.get('texto','—')}\n"
            f"Contexto: {esc1.get('contexto','—')}\n"
            "Confirmaciones:\n"
            f"{_fmt_confs(esc1.get('confirmaciones', {}))}\n"
            f"{_fmt_setup(esc1)}\n\n"
            "🔶 *ESCENARIO 2 — Contra-tendencia / retroceso*\n"
            f"Tipo: {esc2.get('tipo','—')} | Probabilidad: {esc2.get('probabilidad','—')} | Riesgo: {esc2.get('riesgo','—')}\n"
            f"{esc2.get('texto','—')}\n"
            f"Contexto: {esc2.get('contexto','—')}\n"
            "Confirmaciones:\n"
            f"{_fmt_confs(esc2.get('confirmaciones', {}))}\n"
            f"{_fmt_setup(esc2)}\n\n"
            "🧠 *CONCLUSIÓN OPERATIVA*\n"
            f"{concl}\n\n"
            "📓 *Reflexión TESLABTC A.P.*:\n"
            f"💭 {reflexion}\n\n"
            "⚠️ Análisis exclusivo para la sesión N.Y\n"
            "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
        )
        return limpiar_texto(texto)

    except Exception as e:
        return f"⚠️ Error al formatear mensaje: {e}"
