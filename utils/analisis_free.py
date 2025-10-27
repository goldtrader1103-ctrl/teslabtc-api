# ============================================================
# 📊 analisis_free.py — Lógica de análisis Free (educativa v4.0)
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios, sesion_ny_activa

def generar_analisis_free(precio_actual):
    precios = obtener_precios()
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    return {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Free",
        "activo": "BTCUSDT",
        "sesion": sesion,
        "precio_actual": f"{precio_actual:,.2f} USD",
        "fuente_precio": precios.get("fuente", "Binance (REST)"),
        "temporalidades": "D | H4 | H1 | M15",

        # Educativo, no operativo
        "estructura_detectada": {
            "H4 (macro)": {"estado": "Bajista"},
            "H1 (intradía)": {"estado": "Rango"}
        },

        "zonas_relevantes": "🔒 Desbloquea con Premium",
        "confirmaciones": "🔒 Desbloquea con Premium",
        "escenario_continuacion": "🔒 Desbloquea con Premium",
        "escenario_correccion": "🔒 Desbloquea con Premium",

        "conclusion": "🧠 Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
        "conexion_binance": precios.get("estado", "🦎 Fallback CoinGecko activo"),
        "reflexion": "📘 El mercado recompensa la disciplina, no la emoción.",
        "nota": "⚠️ Diseñado para operar exclusivamente en la Sesión de Nueva York (NY)."
    }
