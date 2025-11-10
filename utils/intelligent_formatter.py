from __future__ import annotations
from typing import Dict, Any
import unicodedata
import random

__all__ = [
    "limpiar_texto",
    "construir_mensaje_free",
    "construir_mensaje_operativo_premium",
]

def limpiar_texto(valor: str) -> str:
    if not isinstance(valor, str):
        valor = str(valor)
    texto = unicodedata.normalize("NFKC", valor)
    reemplazos = {
        "Ã³":"ó","Ã¡":"á","Ã©":"é","Ã­":"í","Ãº":"ú","Ã±":"ñ",
        "â":"'","â":"-","â":"\"","â":"\"","â¢":"•",
        "â":"✔️","â":"❌","Â":"","â¦":"…"
    }
    for k,v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto.encode("utf-8","ignore").decode("utf-8","ignore").strip()

# ---------------------------
# FREE
# ---------------------------
def construir_mensaje_free(data: Dict[str, Any]) -> str:
    fecha   = data.get("fecha","—")
    activo  = "BTCUSDT"
    sesion  = data.get("sesión") or data.get("sesion","—")
    precio  = data.get("precio_actual","—")
    tfs     = "D | H4 | H1 | M15"
    conexion= data.get("conexion_binance","—")

    cuerpo = (
        "📋 REPORTE TESLABTC A.P. – Sesión NY\n"
        "──────────────────────────────\n\n"
        f"📅 Fecha: {fecha}\n"
        f"💰 Activo: {activo}\n"
        f"💵 Precio actual: {precio}\n"
        f"🕒 Sesión: {sesion}\n"
        f"📊 Temporalidades analizadas: {tfs}\n\n"
        "🧭 DIRECCIÓN GENERAL\n\n"
        "Tendencia principal: (calculada por estructura D/H4/H1)\n"
        "Contexto: (explicado por el motor de escenarios y zonas)\n\n"
        "📍 ZONAS RELEVANTES: 🔒 Disponible en Premium\n"
        "✅ CONFIRMACIONES CLAVE: 🔒 Disponible en Premium\n"
        "🟢/🔴 ESCENARIOS: 🔒 Disponible en Premium\n\n"
        "📓 Reflexión TESLABTC A.P.: Desbloquéalo con Premium.\n"
    )
    return limpiar_texto(cuerpo)

# ---------------------------
# PREMIUM
# ---------------------------
def _fmt_confs(d: Dict[str,str]) -> str:
    if not d: return "—"
    return "\n".join([f"• {k}: {v}" for k,v in d.items()])

def _fmt_zonas(d: Dict[str,Any]) -> str:
    if not d: return "—"
    parts = []
    for k,v in d.items():
        parts.append(f"- {k}: {v}")
    return "\n".join(parts)

def construir_mensaje_operativo(data: Dict[str, Any]) -> str:
    fecha   = data.get("fecha","—")
    activo  = data.get("activo","BTCUSDT")
    sesion  = data.get("sesión") or data.get("sesion","—")
    precio  = data.get("precio_actual","—")
    tfs     = "D | H4 | H1 | M15 | M5"

    zonas   = data.get("zonas_detectadas", {})
    confs   = data.get("confirmaciones", {})
    esc1    = data.get("escenario_1", {})
    esc2    = data.get("escenario_2", {})
    concl   = data.get("conclusion_general","—")
    reflex  = data.get("reflexion","El mercado recompensa la disciplina, no la emoción.")
    slogan  = data.get("slogan","✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    # Si el setup_tesla está activo, lo imprimimos como bloque especial
    setup  = data.get("setup_tesla", {}) or {}
    setup_block = ""
    if setup.get("activo"):
        setup_block = (
            "\n⚙️ SETUP ACTIVO – LEVEL ENTRY (M5)\n\n"
            f"{setup.get('contexto','')}\n\n"
            f"📈 Zona de entrada: {setup.get('zona_entrada','—')}\n"
            f"⛔ SL: {setup.get('sl','—')}\n"
            f"🎯 TP1: {setup.get('tp1','—')}\n"
            f"🎯 TP2: {setup.get('tp2','—')}\n"
            f"🧭 Comentario: {setup.get('comentario','—')}\n"
        )

    texto = (
        "📋 REPORTE TESLABTC A.P. – Sesión NY\n"
        "──────────────────────────────\n\n"
        f"📅 Fecha: {fecha}\n"
        f"💰 Activo: {activo}\n"
        f"💵 Precio actual: {precio}\n"
        f"🕒 Sesión: {sesion}\n"
        f"📊 Temporalidades analizadas: {tfs}\n\n"

        "🧭 DIRECCIÓN GENERAL\n"
        "──────────────────────────────\n"
        f"D: {data['estructura_detectada'].get('D', '—')}\n"
        f"H4: {data['estructura_detectada'].get('H4', '—')}\n"
        f"H1: {data['estructura_detectada'].get('H1', '—')}\n\n"
        f"🧠 Contexto macro: {data.get('contexto_general', '—')}\n\n"

        "📍 ZONAS RELEVANTES\n"
        "──────────────────────────────\n"
        f"• PDH: {zonas.get('PDH','—')}\n"
        f"• PDL: {zonas.get('PDL','—')}\n"
        f"• D HIGH / LOW: {zonas.get('D_HIGH','—')} / {zonas.get('D_LOW','—')}\n"
        f"• H4 HIGH / LOW: {zonas.get('H4_HIGH','—')} / {zonas.get('H4_LOW','—')}\n"
        f"• H1 HIGH / LOW: {zonas.get('H1_HIGH','—')} / {zonas.get('H1_LOW','—')}\n\n"

        "✅ CONFIRMACIONES CLAVE\n"
        "──────────────────────────────\n"
        f"• Tendencia macro (D): {confs.get('Tendencia macro (D) definida','❌')}\n"
        f"• Intradía (H1): {confs.get('Tendencia intradía (H1) definida','❌')}\n"
        f"• OB válido H1/H15: {confs.get('OB válido en H1/H15','❌')}\n"
        f"• Barrida PDH: {confs.get('Barrida PDH','❌')}\n"
        f"• Barrida Bajo Asia: {confs.get('Barrida Bajo Asia','❌')}\n\n"

        "🟢 ESCENARIO 1 — A favor de tendencia\n"
        "──────────────────────────────\n"
        f"Tipo: {esc1.get('tipo','—')} | Probabilidad: {esc1.get('probabilidad','—')} | Riesgo: {esc1.get('riesgo','—')}\n\n"
        f"{esc1.get('texto','—')}\n\n"
        f"Contexto: {esc1.get('contexto','—')}\n\n"
        "Confirmaciones:\n"
        f"{_fmt_confs(esc1.get('confirmaciones', {}))}\n\n"
        f"{esc1.get('setup_estado','⏳ Sin setup válido. Intenta en unos minutos.')}\n\n"

        "🔶 ESCENARIO 2 — Contra-tendencia / retroceso\n"
        "──────────────────────────────\n"
        f"Tipo: {esc2.get('tipo','—')} | Probabilidad: {esc2.get('probabilidad','—')} | Riesgo: {esc2.get('riesgo','—')}\n\n"
        f"{esc2.get('texto','—')}\n\n"
        f"Contexto: {esc2.get('contexto','—')}\n\n"
        "Confirmaciones:\n"
        f"{_fmt_confs(esc2.get('confirmaciones', {}))}\n\n"
        f"{esc2.get('setup_estado','⏳ Sin setup válido. Intenta en unos minutos.')}\n\n"
        f"{_fmt_confs(esc2.get('setup', {}))}\n\n"
        f"{setup_block}\n"

        "🧠 CONCLUSIÓN OPERATIVA\n"
        "──────────────────────────────\n"
        f"{concl}\n\n"

        "📓 Reflexión TESLABTC A.P.\n"
        "──────────────────────────────\n"
        f"💭 {reflex}\n\n"
        "⚠️ Análisis exclusivo para la sesión N.Y\n"
        f"{slogan}\n"
    )

    return limpiar_texto(texto)
