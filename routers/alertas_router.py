from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import obtener_precio

router = APIRouter()

@router.get("/alertas")
def alertas_teslabtc():
    try:
        precio_actual = obtener_precio()
        if not precio_actual:
            return {"error": "No se pudo obtener el precio real de BTCUSDT."}

        if precio_actual > 125000:
            alerta = "⚠️ BTCUSDT tocó zona de oferta (PDH)"
            estado = "ACTIVA 🔔"
        elif precio_actual < 122000:
            alerta = "🟢 BTCUSDT tocó zona de demanda (PDL)"
            estado = "ACTIVA 🔔"
        else:
            alerta = "🟢 Sin alertas activas"
            estado = "SILENCIO"

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "precio_actual": precio_actual,
            "alerta": alerta,
            "estado_alerta": estado,
            "estrategia": "TESLABTC A.P.",
            "nota": "Basado en zonas H1/H4 y liquidez."
        }

    except Exception as e:
        return {"error": str(e)}
