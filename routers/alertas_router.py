from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from utils.price_utils import (
    obtener_klines_binance,
    detectar_estructura,
    _pdh_pdl,
    _asia_range,
    obtener_precio,
    TZ_COL,
)

router = APIRouter()


@router.get("/alertas", tags=["TESLABTC"])
def alertas_teslabtc() -> Dict[str, Any]:
    """
    Monitorea BTCUSDT en tiempo real y genera alertas TESLABTC A.P.
    - Solo activa alertas cuando hay Setup A+ (H1 + M5 + barrida) o Setup Base (BOS M15)
    - Usa PDH/PDL y rango asiático para validar zonas de reacción
    - Acción del precio puro: estructura + liquidez
    """
    ahora_col = datetime.now(TZ_COL)
    precio_actual = obtener_precio()

    if precio_actual is None:
        return {
            "error": "No se pudo obtener el precio real de BTCUSDT.",
            "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        }

    # 1️⃣ Velas recientes
    velas_h1 = obtener_klines_binance("1h", 120)
    velas_m15 = obtener_klines_binance("15m", 120)
    velas_m5 = obtener_klines_binance("5m", 150)

    if not velas_h1 or not velas_m15 or not velas_m5:
        return {"error": "No se pudieron obtener velas reales desde Binance."}

    # 2️⃣ Estructura
    estr_h1 = detectar_estructura(velas_h1, lookback=20)
    estr_m15 = detectar_estructura(velas_m15, lookback=20)
    estr_m5 = detectar_estructura(velas_m5, lookback=20)

    # 3️⃣ Niveles clave
    pdh, pdl = _pdh_pdl(velas_h1)
    asia_high, asia_low = _asia_range(velas_m15)

    # 4️⃣ Determinación de setup
    setup = None
    alerta = "🟢 Sin alertas activas"
    nivel = "—"
    accion_recomendada = "Esperar confirmación adicional"
    estado_alerta = "SILENCIO"

    # Setup A+ BUY
    if estr_h1.get("tipo_BOS") == "alcista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "alcista" and estr_m5.get("barrida_bajista"):
        setup = "🔥 Setup A+ BUY"
        alerta = f"⚠️ BTCUSDT tocó zona de demanda ({pdl:.2f}) con BOS M5 alcista"
        nivel = "Demanda validada + barrida bajista"
        accion_recomendada = "Buscar entrada M5 (Level Entry)"
        estado_alerta = "ACTIVA 🔔"

    # Setup A+ SELL
    elif estr_h1.get("tipo_BOS") == "bajista" and estr_m5.get("BOS") and estr_m5.get("tipo_BOS") == "bajista" and estr_m5.get("barrida_alcista"):
        setup = "🔥 Setup A+ SELL"
        alerta = f"⚠️ BTCUSDT tocó zona de oferta ({pdh:.2f}) con BOS M5 bajista"
        nivel = "Oferta validada + barrida alcista"
        accion_recomendada = "Buscar entrada M5 (Level Entry)"
        estado_alerta = "ACTIVA 🔔"

    # Setup Base BUY
    elif estr_m15.get("BOS") and estr_m15.get("tipo_BOS") == "alcista":
        setup = "✅ Setup BASE BUY"
        alerta = f"🟢 BOS M15 alcista confirmado sobre {asia_high:.2f}"
        nivel = "Confirmación estructural intradía"
        accion_recomendada = "Esperar retroceso M5"
        estado_alerta = "MONITOREO"

    # Setup Base SELL
    elif estr_m15.get("BOS") and estr_m15.get("tipo_BOS") == "bajista":
        setup = "✅ Setup BASE SELL"
        alerta = f"🔴 BOS M15 bajista confirmado bajo {asia_low:.2f}"
        nivel = "Confirmación estructural intradía"
        accion_recomendada = "Esperar retroceso M5"
        estado_alerta = "MONITOREO"

    # Sin setup
    else:
        setup = "⏸️ Sin setup activo"
        alerta = "📉 Esperar BOS M15 o barrida en PDH/PDL"
        nivel = "Sin desequilibrio relevante"
        accion_recomendada = "Sin entrada válida"

    return {
        "timestamp": ahora_col.strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": round(precio_actual, 2),
        "setup": setup,
        "alerta": alerta,
        "nivel": nivel,
        "accion_recomendada": accion_recomendada,
        "estado_alerta": estado_alerta,
        "rango_asia": {"High": asia_high, "Low": asia_low},
        "pdh_pdl": {"PDH": pdh, "PDL": pdl},
        "estrategia": "TESLABTC A.P. — Alertas automáticas basadas en estructura, liquidez y confirmación del flujo institucional.",
    }
