from fastapi import APIRouter
import requests
from datetime import datetime

router = APIRouter()

@router.get("/alertas")
def alertas():
    """Verifica si el precio de BTCUSDT toca zonas clave de liquidez"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    precio = float(data["price"])

    zonas = {
        "PDH": 125300,
        "PDL": 122300,
        "zona_demanda": 122800,
        "zona_oferta": 125700
    }

    alerta = None
    if precio >= zonas["PDH"]:
        alerta = "🚨 Barrida de PDH detectada (Posible reversión)"
    elif precio <= zonas["PDL"]:
        alerta = "⚠️ Barrida de PDL detectada (Posible rebote alcista)"
    elif zonas["zona_demanda"] <= precio <= zonas["zona_oferta"]:
        alerta = "💤 Precio dentro del rango — esperar confirmación TESLABTC"

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio,
        "alerta": alerta or "Sin alerta en zonas clave."
    }
