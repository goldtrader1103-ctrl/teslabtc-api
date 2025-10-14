from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, obtener_klines_binance
from utils.estructura_utils import estructura_y_zonas

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))

@router.get("/", tags=["TESLABTC"])
def analizar():
    ahora = datetime.now(TZ_COL)
    sesion = "✅ Activa (Sesión New York)" if 7 <= (ahora.hour + ahora.minute/60) < 13.5 else "❌ Cerrada (Fuera de NY)"

    p = obtener_precio("BTCUSDT")
    precio, fuente = p.get("precio"), p.get("fuente")
    precio_str = f"{precio:,.2f} USD" if isinstance(precio, (int, float)) else "⚙️ No disponible"

    h4 = obtener_klines_binance("BTCUSDT", "4h", 240) or []
    h1 = obtener_klines_binance("BTCUSDT", "1h", 300) or []
    m15 = obtener_klines_binance("BTCUSDT", "15m", 300) or []

    ez = estructura_y_zonas(h4, h1, m15)
    macro_estado = ez["macro"]["estado"]
    intradia_estado = ez["intradía"]["estado"]

    body = {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "fuente": fuente,
            "precio_actual": precio_str,
            "macro": ez["macro"],
            "intradía": ez["intradía"],
            "reaccion": ez["reaccion"],
            "mensaje": "✅ Análisis completado correctamente"
        }
    }

    return body
