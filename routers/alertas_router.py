from fastapi import APIRouter
from datetime import datetime
import requests

router = APIRouter()

@router.get("/alertas")
def alertas_teslabtc():
    try:
        # Obtener precio en tiempo real desde Binance
        url_binance = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url_binance)
        data = response.json()

        if "price" not in data:
            return {"error": "No se pudo obtener el precio real de BTCUSDT."}

        precio_actual = float(data["price"])

        # Lógica de ejemplo para alerta
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
            "nota": "Basado en niveles de liquidez y zonas H1/H4."
        }

    except Exception as e:
        return {"error": str(e)}
