# ============================================================
# 📈 analisis_premium.py — Lógica de análisis Premium
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios

def generar_analisis_premium(precio_actual):
    precios = obtener_precios()

    analisis = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Premium",
        "precio_actual": f"{precio_actual:,.2f} USD",
        "sesion": "❌ Cerrada (Fuera de NY)",
        "estructura": "Detectando estructura...",
        "escenario": {
            "tipo": "Conservador (SELL A+)",
            "accion": "Esperar retroceso a zona H1/M15 y gatillo BOS M5 con confirmación de volumen.",
            "gestion": "SL en invalidación; TP en zonas de liquidez (RRR ≥ 1:3)",
            "mensaje": "Estructura macro e intradía alineadas a la baja."
        },
        "altos_bajos": precios,
        "nota": "Diseñado para operar en la sesión de Nueva York (NY). El análisis se muestra también fuera de la sesión."
    }

    return analisis
