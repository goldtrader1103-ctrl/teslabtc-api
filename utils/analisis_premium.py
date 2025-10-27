# ============================================================
# 📈 analisis_premium.py — Lógica de análisis Premium (versión extendida y educacional)
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios, _pdh_pdl, sesion_ny_activa
import random

def generar_analisis_premium(precio_actual):
    precios = obtener_precios()
    pd = _pdh_pdl()

    reflexiones = [
        "La paciencia paga más que la prisa.",
        "El mercado recompensa la disciplina, no la emoción.",
        "Cada pérdida bien gestionada es una victoria a largo plazo.",
        "Tu mente es tu mejor indicador.",
        "¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"
    ]

    # 🔍 Determinar sesión
    sesion = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # 🔍 Tendencia macro definida por estructura (H4)
    tendencia_macro = "Bajista"  # <--- puedes cambiarlo según análisis real

    # Dirección dinámica según tendencia
    if tendencia_macro.lower() == "bajista":
        continuacion_direccion = "Bajista (a favor de tendencia macro)"
        correccion_direccion = "Alcista (retroceso dentro de tendencia bajista)"
    else:
        continuacion_direccion = "Alcista (a favor de tendencia macro)"
        correccion_direccion = "Bajista (retroceso dentro de tendencia alcista)"

    return {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Premium",
        "activo": "BTCUSDT",
        "sesion": sesion,
        "precio_actual": f"{precio_actual:,.2f} USD",
        "precio_float": precio_actual,  # soporte interno
        "temporalidades": "D | H4 | H1 | M15",

        # =====================================
        # 📊 PDH / PDL ÚLTIMAS 24H
        # =====================================
        "liquidez": {
            "PDH": f"{pd['PDH']:,}" if pd["PDH"] else None,
            "PDL": f"{pd['PDL']:,}" if pd["PDL"] else None
        },

        # =====================================
        # 🧩 ESTRUCTURA
        # =====================================
        "estructura_detectada": {
            "H4 (macro)": {
                "estado": tendencia_macro,
                "high": 114000,
                "low": 103500
            },
            "H1 (intradía)": {
                "estado": "Rango",
                "high": 114000,
                "low": 106700
            }
        },

        # =====================================
        # 🔥 ZONAS
        # =====================================
        "zonas_relevantes": (
            "📍 POI principal: OB H1 (111.800 – 112.400) — oferta activa.\n"
            "📉 Order Block D: Demanda D (99.000 – 101.000) aún sin mitigar.\n"
            "📊 FVG: Gap leve entre 113.000 – 114.200.\n"
            "📈 Nivel Fibo: Retroceso 50–61.8% dentro del OB H1 → zona técnica de rechazo."
        ),

        # =====================================
        # ✅ CONFIRMACIONES
        # =====================================
        "confirmaciones": (
            "✔️ BOS bajista confirmado en H4 y D.\n"
            "🕒 Sesión NY activa con reacción sobre OB H1.\n"
            "📉 Tendencia H1: Bajista | M15: Neutra.\n"
            "📊 Volumen medio sin ruptura limpia."
        ),

        # =====================================
        # 🟢 CONTINUACIÓN (a favor de tendencia macro)
        # =====================================
        "escenario_continuacion": (
            f"🟢 *Escenario de continuación*:\n"
            f"Dirección: {continuacion_direccion}.\n"
            "Entrada: Reentrada en retroceso M5 tras BOS M15.\n"
            "Invalidación: Ruptura fuera de zona con vela amplia.\n"
            "TP: 113.800 (FVG H1) | SL: 110.700.\n"
            "Probabilidad: Media."
        ),

        # =====================================
        # 🔴 CORRECCIÓN (movimiento contrario a tendencia macro)
        # =====================================
        "escenario_correccion": (
            f"🔴 *Escenario correctivo*:\n"
            f"Dirección: {correccion_direccion}.\n"
            "Entrada: Tras confirmación de BOS contra tendencia local.\n"
            "Invalidación: Superar 112.800 con volumen fuerte.\n"
            "TP: 107.000 | SL: 112.600.\n"
            "Probabilidad: Alta."
        ),

        # =====================================
        # 🧠 ACLARACIÓN EDUCATIVA
        # =====================================
        "aclaracion": (
            "📌 Nota importante:\n"
            "Corrección y continuación NO son compra o venta por sí mismas.\n"
            "Dependen de la dirección de tendencia MACRO."
        ),

        # =====================================
        # 🧠 CONCLUSIÓN
        # =====================================
        "conclusion": (
            "🧠 Escenario más probable: 🔴 Corrección bajista.\n"
            "Motivo: Reacción sobre OB H1 + estructura bajista general.\n"
            "🎯 Recomendación: Esperar BOS M15 antes de ejecutar entrada."
        ),

        # =====================================
        # 🔌 ESTADO
        # =====================================
        "conexion_binance": precios.get("estado", "🦎 Fallback CoinGecko activo"),

        # =====================================
        # 📘 MENTALIDAD
        # =====================================
        "reflexion": f"📘 Reflexión TESLABTC A.P.: {random.choice(reflexiones)}",

        "nota": "⚠️ Diseñado para operar exclusivamente en la Sesión de Nueva York (NY)."
    }
