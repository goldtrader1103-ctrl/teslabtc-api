# ============================================================
# 📊 analisis_free.py — TESLABTC.KG (versión Free reducida)
# Mantiene mensaje resumido y claves mínimas para tu bot.
# ============================================================

from datetime import datetime
from utils.price_utils import sesion_ny_activa

def _fmt_usd(x: float) -> str:
    try:
        return f"{x:,.2f} USD"
    except Exception:
        return str(x)

def generar_analisis_free(precio_actual: float) -> dict:
    ahora = datetime.now()
    sesion_ok = sesion_ny_activa()
    sesion_txt = "✅ Activa (Sesión NY)" if sesion_ok else "❌ Cerrada (Fuera de NY)"

    mensaje = (
        "Estructura bajista mayor con retroceso activo hacia oferta H1. "
        "Escenarios y confirmaciones BOS disponibles en Premium."
    )

    return {
        "fecha": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "nivel_usuario": "Free",
        "activo": "BTCUSDT",
        "sesión": sesion_txt,
        "precio_actual": _fmt_usd(precio_actual),
        "temporalidades": ["D", "H4", "H1", "M15"],

        "estructura_detectada": {
            "H4 (macro)": {"estado": "bajista"},
            "H1 (intradía)": {"estado": "retroceso"},
            "M15 (reacción)": {"estado": "neutro"},
        },

        # Campos que el bot ya usa:
        "mensaje": "🍀 Nivel Free — acceso limitado. Actualiza a Premium para escenarios y alertas BOS.",
        "zonas": "🔒 Desbloquea con Premium",
        "confirmaciones": "🔒 Desbloquea con Premium",
        "escenario_1": "🔒 Desbloquea con Premium",
        "escenario_2": "🔒 Desbloquea con Premium",
    }
