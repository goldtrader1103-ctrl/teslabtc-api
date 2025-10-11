# routers/alertas_router.py
from fastapi import APIRouter
from utils.price_utils import obtener_precio

router = APIRouter()

@router.get("/precio/{simbolo}", tags=["TESLABTC"])
def get_precio(simbolo: str):
    """
    📊 Devuelve el precio actual en tiempo real desde Binance.
    Ejemplo: /precio/BTCUSDT
    """
    precio = obtener_precio(simbolo)
    if precio == 0.0:
        return {"simbolo": simbolo.upper(), "precio": "⚙️ No disponible (sin lectura en vivo)"}
    return {"simbolo": simbolo.upper(), "precio": precio}
