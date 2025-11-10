# ============================================================
# 🧠 TESLABTC.KG — utils/intelligent_formatter.py (v5.2)
# Salidas Free + Premium (Markdown seguro) — INDENTACIÓN OK
# ============================================================
from __future__ import annotations
from typing import Dict, Any
import unicodedata

__all__ = ["construir_mensaje_free", "construir_mensaje_operativo"]

def _clean(texto: str) -> str:
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize("NFKC", texto)
    rep = {
        "Ã³":"ó","Ã¡":"á","Ã©":"é","Ã­":"í","Ãº":"ú","Ã±":"ñ",
        "â":"'","â":"-","â":"\"","â":"\"","â¢":"•",
        "â":"✔️","â":"❌","Â":"","â¦":"…"
    }
    for k,v in rep.items():
        texto = texto.replace(k, v)
    return texto.strip()

def construir_mensaje_free(data: Dict[str, Any]) -> str:
    fecha   = data.get("fecha","—")
    sesion  = data.get("sesión") or data.get("sesion","—")
    precio  = data.get("precio_actual","—")
    cuerpo = (
        "📋 REPORTE TESLABTC A.P. – Sesión NY\n"
        "──────────────────────────────\n\n"
        f"📅 Fecha: {fecha}\n"
        f"💰 Activo: BTCUSDT\n"
        f"💵 Precio actual: {precio}\n"
        f"🕒 Sesión: {sesion}\n"
        "📊 Temporalidades analizadas: D | H4 | H1 | M15\n\n"
        "🧭 DIRECCIÓN GENERAL (Premium)\n"
        "📍 ZONAS / CONFIRMACIONES / ESCENARIOS → 🔒 Premium\n"
        "📓 Desbloquéalo con Premium.\n"
    )
    return _clean(cuerpo)

def construir_mensaje_operativo(data: Dict[str, Any]) -> str:
    fecha   = data.get("fecha","—")
    activo  = data.get("activo","BTCUSDT")
    sesion  = data.get("sesión") or data.get("sesion","—")
    precio  = data.get("precio_actual","—")

    estructura = data.get("estructura_detectada", {})
    d  = estructura.get("D", {})
    h4 = estructura.get("H4", {})
    h1 = estructura.get("H1", {})
    zonas = data.get("zonas_detectadas") or data.get("zonas") or {}

    confs = data.get("confirmaciones", {})
    esc1  = data.get("escenario_1", {})
    esc2  = data.get("escenario_2", {})
    concl = data.get("conclusion_general","—")
    reflex= data.get("reflexion","El mercado recompensa la disciplina, no la emoción.")
    slogan= data.get("slogan","✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!")

    setup = data.get("setup_tesla", {}) or {}
    setup_block = ""
    if setup.get("activo"):
        setup_block = (
            "\n⚙️ SETUP ACTIVO – LEVEL ENTRY (M5)\n"
            f"{setup.get('contexto','')}\n"
            f"📈 Zona: {setup.get('zona_entrada','—')}\n"
            f"⛔ SL: {setup.get('sl','—')} | 🎯 TP1: {setup.get('tp1','—')} | 🎯 TP2: {setup.get('tp2','—')}\n"
        )

    texto = (
        "📋 REPORTE TESLABTC A.P. – Sesión NY\n"
        "──────────────────────────────\n\n"
        f"📅 Fecha: {fecha}\n"
        f"💰 Activo: {activo}\n"
        f"💵 Precio actual: {precio}\n"
        f"🕒 Sesión: {sesion}\n"
        "📊 Temporalidades analizadas: D | H4 | H1 | M15 | M5\n\n"

        "🧭 DIRECCIÓN GENERAL\n"
        "──────────────────────────────\n"
        f"📈 D (Macro): {d.get('estado','—')} — BOS: {d.get('BOS','—')} | HH: {d.get('HH','—')} | LL: {d.get('LL','—')}\n"
        f"⚙️ H4 (Intradía): {h4.get('estado','—')} — BOS: {h4.get('BOS','—')} | HH: {h4.get('HH','—')} | LL: {h4.get('LL','—')}\n"
        f"🔹 H1 (Reacción): {h1.get('estado','—')} — BOS: {h1.get('BOS','—')} | HH: {h1.get('HH','—')} | LL: {h1.get('LL','—')}\n\n"

        "📍 ZONAS REALES (Día operativo y Asia cerrados)\n"
        "──────────────────────────────\n"
        f"• PDH: {zonas.get('PDH','—')} | • PDL: {zonas.get('PDL','—')}\n"
        f"• ASIAN HIGH: {zonas.get('ASIAN_HIGH','—')} | • ASIAN LOW: {zonas.get('ASIAN_LOW','—')}\n"
        f"• Horario Día: {zonas.get('horario_dia','—')}\n"
        f"• Horario Asia: {zonas.get('horario_asia','—')}\n\n"

        "✅ CONFIRMACIONES CLAVE (con contexto)\n"
        "──────────────────────────────\n"
        f"• BOS: {confs.get('bos_texto','—')}\n"
        ('✔️ Activa' if confs.get('sesion_ny_activa') else '❌ Cerrada')
        f"• Tendencia H1: {confs.get('tendencia_h1','—')}\n"
        f"• Tendencia M15: {confs.get('tendencia_m15','—')}\n"
        f"• Volumen/Asia: {confs.get('vol_asia','—')}\n"
        f"• Comentarios: {confs.get('comentarios','—')}\n\n"

        "🟢 ESCENARIO 1 — A favor de tendencia\n"
        "──────────────────────────────\n"
        f"{esc1.get('texto','—')}\n\n"

        "🔶 ESCENARIO 2 — Contra-tendencia / retroceso\n"
        "──────────────────────────────\n"
        f"{esc2.get('texto','—')}\n"
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
    return _clean(texto)
