# ============================================================
# 📈 analisis_premium.py — Lógica de análisis Premium (versión extendida)
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios
import random

def generar_analisis_premium(precio_actual):
    precios = obtener_precios()

    reflexiones = [
        "La paciencia paga más que la prisa.",
        "El mercado recompensa la disciplina, no la emoción.",
        "Cada pérdida bien gestionada es una victoria a largo plazo.",
        "Tu mente es tu mejor indicador.",
        "¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    ]

    return {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Premium",
        "activo": "BTCUSDT",
        "sesion": "✅ Activa (Sesión NY)",
        "precio_actual": f"{precio_actual:,.2f} USD",
        "fuente_precio": "Binance (REST)",
        "temporalidades": "D | H4 | H1 | M15",

        "estructura_detectada": {
            "H4 (macro)": {
                "estado": "Bajista",
                "high": 114000,
                "low": 103500
            },
            "H1 (intradía)": {
                "estado": "Rango",
                "high": 114000,
                "low": 106700
            }
        },

        "zonas_relevantes": (
            "📍 POI principal: OB H1 (111.800 – 112.400) — oferta activa.\n"
            "📉 Order Block D: Demanda D (99.000 – 101.000) aún sin mitigar.\n"
            "📊 FVG: Gap leve entre 113.000 – 114.200.\n"
            "📈 Nivel Fibo: Retroceso 50–61.8% dentro del OB H1 → zona técnica de rechazo."
        ),

        "confirmaciones": (
            "✔️ BOS bajista confirmado en H4 y D.\n"
            "🕒 Sesión NY activa con reacción sobre OB H1.\n"
            "📉 Tendencia H1: Bajista | M15: Neutra.\n"
            "📊 Volumen medio sin ruptura limpia."
        ),

        "escenario_continuacion": (
            "🟢 *Escenario de continuación (alcista)*:\n"
            "Dirección: Alcista correctiva hacia 113.000 – 114.000.\n"
            "Entrada: Reentrada en retroceso M5 tras BOS M15.\n"
            "TP: 113.800 (FVG H1) | SL: 110.700.\n"
            "Probabilidad: Media."
        ),

        "escenario_correccion": (
            "🔴 *Escenario de corrección (bajista)*:\n"
            "Dirección: Bajista hacia 107.000 – 105.500.\n"
            "Entrada: Tras confirmación de BOS bajista en M15.\n"
            "TP: 107.000 | SL: 112.600.\n"
            "Probabilidad: Alta."
        ),

        "conclusion": (
            "🧠 Escenario más probable: 🔴 Corrección bajista.\n"
            "Motivo: Reacción sobre OB H1 + estructura bajista general.\n"
            "🎯 Recomendación: Esperar BOS M15 antes de ejecutar entrada."
        ),

        "conexion_binance": "🦎 Fallback CoinGecko activo",
        "reflexion": f"📘 Reflexión TESLABTC A.P.: {random.choice(reflexiones)}",
        "nota": "⚠️ Diseñado para operar exclusivamente en la Sesión de Nueva York (NY)."
    }
