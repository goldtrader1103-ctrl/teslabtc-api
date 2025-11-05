# 🔰 INICIO DE BLOQUE (intelligent_formatter.py)
# ============================================================
# 🧠 TESLABTC.KG — FORMATEADOR INTELIGENTE DE TEXTO
# ============================================================
# Limpia acentos, corrige UTF-8 y da formato legible a los reportes
# enviados por la API y el bot, incluyendo las confirmaciones del setup.
# ============================================================

import unicodedata
import json

# ------------------------------------------------------------
# 🧹 LIMPIEZA GENERAL DE TEXTO
# ------------------------------------------------------------
def limpiar_texto(valor: str) -> str:
    """Normaliza y limpia texto sin eliminar emojis."""
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
# 🎨 CONSTRUCCIÓN DE MENSAJE OPERATIVO PREMIUM
# ------------------------------------------------------------
def construir_mensaje_operativo(data: dict) -> str:
    """
    Convierte el análisis dict de la API en texto formateado para el bot.
    Incluye todas las confirmaciones con ✅ o ❌.
    """
    try:
        fecha = data.get("fecha", "—")
        sesion = data.get("sesion", "—")
        activo = data.get("activo", "BTCUSDT")
        precio = data.get("precio_actual", "—")
        prob = data.get("probabilidad", "—")
        setup = data.get("setup_tesla", {})
        confs = data.get("confirmaciones", {})
        conclusion = data.get("conclusion_general", "—")

        # 🔹 Formato de confirmaciones
        confs_txt = "\n".join([f"• {k}: {v}" for k, v in confs.items()])

        # 🔹 Formato de setup
        setup_txt = (
            f"📍 Zona de entrada: {setup.get('zona_entrada','—')}\n"
            f"⛔ SL: {setup.get('sl','—')}\n"
            f"🎯 TP1: {setup.get('tp1','—')}\n"
            f"🎯 TP2: {setup.get('tp2','—')}\n"
            f"🎯 TP3: {setup.get('tp3','—')}\n"
            f"🧭 Observación: {setup.get('observacion','—')}"
        )

        texto = (
            f"📋 *REPORTE TESLABTC A.P. – Sesión NY*\n"
            f"📅 {fecha}\n"
            f"💰 {activo}\n"
            f"🕒 {sesion}\n"
            f"💵 {precio}\n"
            f"📊 Probabilidad: *{prob}*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *CONFIRMACIONES TESLA:*\n{confs_txt}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *SETUP TESLA:*\n{setup_txt}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 *CONCLUSIÓN:*\n{conclusion}\n\n"
            "📓 El mercado recompensa la disciplina, no la emoción."
        )

        return limpiar_texto(texto)
    except Exception as e:
        return f"⚠️ Error al formatear mensaje: {e}"

# 🔰 FIN DE BLOQUE


# ============================================================
# 🧪 PRUEBA LOCAL
# ============================================================
if __name__ == "__main__":
    ejemplo = {
        "fecha": "04/11/2025 15:40:00",
        "activo": "BTCUSDT",
        "sesion": "New York",
        "precio_actual": "100,428 USD",
        "direccion_general": "Alcista (H1 y M15)",
        "zonas_detectadas": {"PDH": "101,200", "PDL": "99,800"},
        "confirmaciones_detectadas": {"BOS": "✔️", "Barrida": "✔️", "OB válido": "❌"},
        "escenario_1": "Compra hacia PDH",
        "escenario_2": "Venta hacia PDL",
        "conclusion": "Esperar reacción en OB H1 con volumen.",
        "fuente_precio": "Binance REST"
    }
    print(construir_mensaje_operativo(ejemplo))
