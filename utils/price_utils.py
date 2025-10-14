# ============================================================
# 🧠 DETECTOR ESTRUCTURAL TESLABTC.KG (versión estable 3.1)
# ============================================================

from datetime import datetime
from utils.price_utils import obtener_klines_binance, detectar_estructura

# ============================================================
# 🔍 Evaluar estructura macro, intradía y de reacción
# ============================================================

def evaluar_estructura(simbolo: str = "BTCUSDT") -> dict:
    """
    Analiza tres niveles de estructura (H4, H1, M15)
    y determina dirección general y zonas de reacción reales.
    """
    try:
        data = {
            "H4": obtener_klines_binance(simbolo, "4h", 120),
            "H1": obtener_klines_binance(simbolo, "1h", 120),
            "M15": obtener_klines_binance(simbolo, "15m", 120),
        }

        estructura = {}
        zonas = {}
        for tf, velas in data.items():
            info = detectar_estructura(velas)
            estructura[tf] = info["estado"]
            zonas[tf] = {
                "High": info.get("zona_high"),
                "Low": info.get("zona_low")
            }

        return {
            "estructura": {
                "H4 (macro)": estructura["H4"],
                "H1 (intradía)": estructura["H1"],
                "M15 (reacción)": estructura["M15"]
            },
            "zonas": {
                "ZONA H4 (macro)": zonas["H4"],
                "ZONA H1 (intradía)": zonas["H1"],
                "ZONA M15 (reacción)": zonas["M15"],
            }
        }

    except Exception as e:
        print(f"[evaluar_estructura] Error: {e}")
        return {
            "estructura": {
                "H4 (macro)": "sin_datos",
                "H1 (intradía)": "sin_datos",
                "M15 (reacción)": "sin_datos"
            },
            "zonas": {}
        }

# ============================================================
# 🧭 Determinar escenario operativo TESLABTC.KG
# ============================================================

def definir_escenario(estructura: dict) -> dict:
    """
    Usa la estructura detectada (macro, intradía, micro)
    para determinar el tipo de operación más probable.
    """

    h4 = estructura.get("H4 (macro)")
    h1 = estructura.get("H1 (intradía)")
    m15 = estructura.get("M15 (reacción)")

    # ————————————————————————————————
    # ESCENARIO PRINCIPAL (CONSERVADOR 1)
    # ————————————————————————————————
    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razón": "H4 y H1 alineados al alza. Flujo institucional activo.",
            "acción": (
                "Operar BUY A+ con confirmación BOS M5 dentro del POI M15 en dirección principal.\n"
                "Objetivo: 1:3 o más, priorizando estructuras limpias.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            ),
            "tipo": "principal"
        }

    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razón": "H4 y H1 alineados a la baja. Flujo institucional bajista.",
            "acción": (
                "Operar SELL A+ con confirmación BOS M5 dentro del POI M15 en dirección principal.\n"
                "Objetivo: 1:3 o más, priorizando estructuras limpias.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            ),
            "tipo": "principal"
        }

    # ————————————————————————————————
    # ESCENARIO DE REENTRADA (CONSERVADOR 2)
    # ————————————————————————————————
    if h4 == h1 and m15 == "neutra":
        return {
            "escenario": "CONSERVADOR 2 (Reentrada)",
            "nivel": "Reentrada dentro de estructura principal",
            "razón": "El precio podría estar mitigando zonas pendientes dentro de la estructura principal.",
            "acción": (
                "Esperar pullback sobre la zona previa o segunda zona de interés para una nueva entrada alineada con H1.\n"
                "Ajustar SL cubriendo ambas zonas y mantener gestión 1:3."
            ),
            "tipo": "reentrada"
        }

    # ————————————————————————————————
    # ESCENARIO SCALPING CONTRA-TENDENCIA
    # ————————————————————————————————
    if h1 != h4 and (m15 in ["alcista", "bajista"]):
        return {
            "escenario": "SCALPING CONTRA-TENDENCIA",
            "nivel": "Scalping intradía",
            "razón": f"M15 en retroceso dentro de zona opuesta, flujo intradía limitado.",
            "acción": (
                "Operación rápida (1:1 – 1:2 máx) dentro de POI M15 con confirmación M3–M5.\n"
                "💡 Riesgo reducido y cierre parcial recomendado."
            ),
            "tipo": "scalp"
        }

    # ————————————————————————————————
    # SIN ESTRUCTURA CLARA
    # ————————————————————————————————
    return {
        "escenario": "NEUTRO / SIN CONFIRMACIÓN",
        "nivel": "Estructura indefinida",
        "razón": "No hay alineación clara entre temporalidades.",
        "acción": "Esperar confirmaciones o BOS válidos antes de ejecutar cualquier operación.",
        "tipo": "neutral"
    }
