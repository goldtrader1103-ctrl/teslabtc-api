# routers/alertas_router.py
from fastapi import APIRouter
from utils.price_utils import obtener_precio

router = APIRouter()

@router.get("/precio/{simbolo}", tags=["Alertas"])
def get_precio(simbolo: str):
    """
    Endpoint para obtener el precio actual desde Binance.
    Ejemplo: /alertas/precio/BTCUSDT
    """
    precio = obtener_precio(simbolo)
    if precio == 0.0:
        return {"simbolo": simbolo.upper(), "precio": "⚙️ No disponible (sin lectura en vivo)"}
    return {"simbolo": simbolo.upper(), "precio": precio}
