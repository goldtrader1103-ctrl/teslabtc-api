# ============================================================
# 🧠 ESTRUCTURA Y ESCENARIOS TESLABTC.KG (Price Action Puro)
# ============================================================

from datetime import datetime, timezone, timedelta

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔍 FUNCIÓN PRINCIPAL: EVALUAR ESTRUCTURA
# ============================================================

def evaluar_estructura(velas: list[dict], marco: str) -> str:
    """
    Evalúa si la estructura del marco (H4, H1, M15) es alcista, bajista o sin datos,
    basada únicamente en acción del precio (High / Low / Close).
    """
    if not velas or len(velas) < 20:
        return "sin_datos"

    try:
        # Extraer últimos valores de cierre
        closes = [v["close"] for v in velas[-40:]]
        highs = [v["high"] for v in velas[-40:]]
        lows = [v["low"] for v in velas[-40:]]

        # Detectar BOS básico (últimos 10 velas)
        reciente_high = max(highs[-10:])
        reciente_low = min(lows[-10:])
        cierre_actual = closes[-1]

        # Evaluación estructural
        if cierre_actual > reciente_high:
            return "alcista"
        elif cierre_actual < reciente_low:
            return "bajista"
        else:
            return "rango"

    except Exception as e:
        print(f"[evaluar_estructura] Error ({marco}): {e}")
        return "sin_datos"

# ============================================================
# 🎯 FUNCIÓN: DEFINIR ESCENARIOS OPERATIVOS
# ============================================================

def definir_escenarios(estructura: dict, sesion_activa: bool) -> dict:
    """
    Define los escenarios operativos según las estructuras detectadas
    y si la sesión NY está activa.
    """

    h4 = estructura.get("H4 (macro)", "sin_datos")
    h1 = estructura.get("H1 (intradía)", "sin_datos")
    m15 = estructura.get("M15 (reacción)", "sin_datos")

    # ========== ESCENARIO CONSERVADOR 1 ==========
    if h4 == "bajista" and h1 == "bajista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (direccional principal)",
            "razon": "H4 y H1 alineados en estructura bajista.",
            "accion": (
                "Esperar BOS M5 bajista dentro del POI M15.\n"
                "Objetivo: 1:3 o más, priorizando estructuras limpias.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            ),
            "tipo": "principal"
        }

    # ========== ESCENARIO CONSERVADOR 2 (REENTRADA) ==========
    if h4 == "bajista" and h1 == "rango":
        return {
            "escenario": "CONSERVADOR 2 (reentrada)",
            "nivel": "Institucional",
            "razon": "H4 mantiene flujo bajista; H1 mitiga zona de liquidez superior.",
            "accion": (
                "Esperar nueva confirmación bajista (CHOCH o BOS M15/M5).\n"
                "Reentrar si el precio falla en romper estructura H1.\n"
                "Mantener SL cubriendo ambas zonas si hay liquidez extendida."
            ),
            "tipo": "reentrada"
        }

    # ========== ESCENARIO SCALPING (CONTRA-TENDENCIA) ==========
    if h4 == "bajista" and h1 == "alcista" and m15 == "alcista":
        return {
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Agresivo / bajo marco de reacción",
            "razon": "Microestructura M15 opuesta al flujo institucional bajista.",
            "accion": (
                "Buscar retroceso M15 y confirmar con BOS M5 antes de ejecutar.\n"
                "RRR máximo: 1:1 o 1:2 (operativa defensiva).\n"
                "⚠️ Solo apto para traders avanzados con gestión estricta."
            ),
            "tipo": "scalping"
        }

    # ========== ESCENARIO ALCISTA PRINCIPAL ==========
    if h4 == "alcista" and h1 == "alcista":
        return {
            "escenario": "CONSERVADOR 1",
            "nivel": "Institucional (flujo alcista principal)",
            "razon": "H4 y H1 alineados en estructura alcista.",
            "accion": (
                "Esperar BOS M5 alcista dentro del POI M15.\n"
                "Objetivo: 1:3 o más, priorizando confirmaciones limpias.\n"
                "💡 Mantener disciplina de gestión de riesgo."
            ),
            "tipo": "principal"
        }

    # ========== ESCENARIO ALCISTA DE REENTRADA ==========
    if h4 == "alcista" and h1 == "rango":
        return {
            "escenario": "CONSERVADOR 2 (reentrada)",
            "nivel": "Institucional",
            "razon": "H4 mantiene flujo alcista; H1 consolida mitigando liquidez inferior.",
            "accion": (
                "Esperar BOS M15/M5 a favor del flujo institucional.\n"
                "Reentrar si hay rechazo claro en zona de demanda refinada.\n"
                "Ajustar SL bajo el OB válido si se extiende el rango."
            ),
            "tipo": "reentrada"
        }

    # ========== ESCENARIO SCALPING ALCISTA (CONTRA-TENDENCIA) ==========
    if h4 == "alcista" and h1 == "bajista" and m15 == "bajista":
        return {
            "escenario": "SCALPING (contra-tendencia)",
            "nivel": "Agresivo / bajo confirmación rápida",
            "razon": "Microestructura M15 opuesta al flujo institucional alcista.",
            "accion": (
                "Buscar oportunidad rápida en retroceso M15.\n"
                "Confirmar con BOS M5 antes de ejecutar entrada.\n"
                "RRR máximo: 1:1 o 1:2. Evitar mantener posiciones fuera de sesión NY."
            ),
            "tipo": "scalping"
        }

    # ========== SIN ESCENARIO CLARO ==========
    return {
        "escenario": "SIN CONFIRMACIÓN",
        "nivel": "Neutro / rango",
        "razon": "Estructuras no alineadas o datos insuficientes.",
        "accion": (
            "Esperar ruptura limpia o confirmación en H1/M15.\n"
            "No operar sin estructura clara ni BOS confirmado.\n"
            "🕐 Modo observación hasta validación de flujo institucional."
        ),
        "tipo": "neutral"
    }
