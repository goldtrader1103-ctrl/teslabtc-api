# ============================================================
# 📊 analisis_free.py — Lógica de análisis Free (versión extendida)
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios

def generar_analisis_free(precio_actual):
    datos = obtener_precios()

    return {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Free",
        "activo": "BTCUSDT",
        "sesion": "❌ Cerrada (Fuera de NY)",
        "precio_actual": f"{precio_actual:,.2f} USD",
        "fuente_precio": "Binance (REST)",
        "temporalidades": "D | H4 | H1 | M15",

        "estructura_detectada": {
            "H4 (macro)": {
                "estado": "Rango",
                "high": 114000,
                "low": 103500
            },
            "H1 (intradía)": {
                "estado": "Bajista",
                "high": 114000,
                "low": 106700
            }
        },

        "zonas_relevantes": "🔒 Desbloquea con Premium",
        "confirmaciones": "🔒 Desbloquea con Premium",
        "escenario_continuacion": "🔒 Desbloquea con Premium",
        "escenario_correccion": "🔒 Desbloquea con Premium",

        "conclusion": "🧠 Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
        "conexion_binance": "🦎 Fallback CoinGecko activo",
        "reflexion": "📘 El mercado recompensa la disciplina, no la emoción.",
        "nota": "⚠️ Diseñado para operar exclusivamente en la Sesión de Nueva York (NY)."
    }
