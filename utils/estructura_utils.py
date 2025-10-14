# ============================================================
# 🧭 TESLABTC.KG — Evaluación estructural macro/micro
# ============================================================

from datetime import datetime, timedelta, timezone
TZ_COL = timezone(timedelta(hours=-5))

def evaluar_estructura(H4_dir, H1_dir, M15_dir, tipo_operacion="institucional"):
    """
    Analiza coherencia estructural y define escenarios:
    1️⃣ Conservador (principal)
    2️⃣ Conservador 2 (reentrada)
    3️⃣ Scalping (contra tendencia)
    """

    if tipo_operacion == "scalping":
        if H1_dir == "bajista" and M15_dir == "alcista":
            return {
                "escenario": "SCALPING BUY",
                "nivel": "Riesgo alto (contra tendencia intradía)",
                "razon": "H1 bajista pero M15 desarrolla retroceso alcista (pullback activo).",
                "accion": (
                    "Ejecutar SCALPING BUY solo si hay BOS micro M5–M3 "
                    "dentro del POI M15 o retroceso profundo del impulso previo.\n"
                    "Objetivo: RRR 1:1 a 1:2 máximo.\n"
                    "💡 La gestión del riesgo es la clave de un trader profesional."
                ),
                "tipo": "scalping"
            }
        elif H1_dir == "alcista" and M15_dir == "bajista":
            return {
                "escenario": "SCALPING SELL",
                "nivel": "Riesgo alto (contra tendencia intradía)",
                "razon": "H1 alcista pero M15 desarrolla retroceso bajista.",
                "accion": (
                    "Ejecutar SCALPING SELL solo con BOS micro M5–M3 en el POI M15.\n"
                    "Objetivo: 1:1 o 1:2 máximo.\n"
                    "💡 La gestión del riesgo es la clave de un trader profesional."
                ),
                "tipo": "scalping"
            }

    if H1_dir == H4_dir:
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razon": f"H4 y H1 alineados en estructura {H1_dir.upper()}.",
            "accion": (
                f"Operar {H1_dir.upper()} A+ con confirmación BOS M5 "
                f"dentro del POI M15 en dirección principal.\n"
                "Objetivo: 1:3 o más, priorizando estructuras limpias.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            ),
            "tipo": "principal"
        }

    if H4_dir == H1_dir and M15_dir == H1_dir:
        return {
            "escenario": "CONSERVADOR 2",
            "nivel": "Reentrada institucional (mitigación adicional)",
            "razon": (
                f"Estructura {H4_dir.upper()} dominante con nueva mitigación "
                "de liquidez o POI secundario en desarrollo."
            ),
            "accion": (
                "Esperar segunda oportunidad en el siguiente rango institucional "
                "o zona de liquidez no mitigada.\n"
                "Ampliar SL cubriendo ambas zonas o dividir entrada en dos tramos.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            ),
            "tipo": "reentrada"
        }

    return {
        "escenario": "RANGO / NEUTRO",
        "nivel": "Sin dirección dominante",
        "razon": "H4 y H1 presentan direcciones opuestas o indecisión.",
        "accion": (
            "Esperar confirmación estructural (CHoCH o BOS fuerte) "
            "antes de ejecutar cualquier entrada."
        ),
        "tipo": "espera"
    }
