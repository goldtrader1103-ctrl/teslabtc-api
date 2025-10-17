# ============================================================
# 📊 analisis_free.py — Lógica de análisis Free
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_precios

def generar_analisis_free(precio_actual):
    datos = obtener_precios()

    analisis = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nivel_usuario": "Free",
        "precio_actual": f"{precio_actual:,.2f} USD",
        "sesion": "❌ Cerrada (Fuera de NY)",
        "macro": "Alcista",
        "estructura": "Consolidación",
        "mensaje": "Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
        "altos_bajos": datos,
        "nota": "Diseñado para operar en la sesión de Nueva York (NY). El análisis se muestra también fuera de la sesión.",
    }

    return analisis
