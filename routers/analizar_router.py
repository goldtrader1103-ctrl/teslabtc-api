# ============================================================
# 🚀 TESLABTC.KG — Análisis Operativo Principal (macro/micro/zonas)
# ============================================================

from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, obtener_klines_binance
from utils.estructura_utils import estructura_y_zonas

router = APIRouter()
TZ_COL = timezone(timedelta(hours=-5))

@router.get("/", tags=["TESLABTC"])
def analizar():
    """Devuelve análisis operativo con estructura macro/micro y zonas de reacción (precios)."""
    ahora = datetime.now(TZ_COL)
    sesion = "✅ Activa (Sesión New York)" if 7 <= (ahora.hour + ahora.minute/60) < 13.5 else "❌ Cerrada (Fuera de NY)"

    # Precio (multifuente ya lo tienes en utils/price_utils)
    p = obtener_precio("BTCUSDT")
    precio, fuente = p.get("precio"), p.get("fuente")
    precio_str = f"{precio:,.2f} USD" if isinstance(precio, (int, float, float)) else "⚙️ No disponible"

    # Velas por marco
    h4 = obtener_klines_binance("BTCUSDT", "4h", 240) or []
    h1 = obtener_klines_binance("BTCUSDT", "1h", 300) or []
    m15 = obtener_klines_binance("BTCUSDT", "15m", 300) or []

    # Estructura/zona (H4=macro, H1=intradía, M15=reacción)
    ez = estructura_y_zonas(h4, h1, m15)
    macro_estado = ez["macro"]["estado"]
    intradia_estado = ez["intradia"]["estado"]

    # Tendencia textual principal
    if macro_estado == "alcista":
        tendencia = "📈 Alcista estructural (H4)"
    elif macro_estado == "bajista":
        tendencia = "📉 Bajista estructural (H4)"
    else:
        tendencia = "⚙️ Rango (H4)"

    body = {
        "🧠 TESLABTC.KG": {
            "fecha": ahora.strftime("%d/%m/%Y %H:%M:%S"),
            "sesion": sesion,
            "fuente": fuente,
            "precio_actual": precio_str,
            "tendencia": tendencia,
            "estructura": {
                "macro": {"estado": macro_estado, "zonas": ez["macro"].get("zonas", {}), "nota": ez["macro"].get("nota")},
                "intradía": {"estado": intradia_estado, "zonas": ez["intradia"].get("zonas", {}), "nota": ez["intradia"].get("nota")},
                "reaccion": ez.get("reaccion", {})
            },
            "mensaje": "✨ Análisis completado correctamente" if isinstance(precio, (int, float)) else "⚠️ Precio no disponible",
            "error": "Ninguno" if isinstance(precio, (int, float)) else "Fuente temporalmente inactiva"
        }
    }

    # Sugerencia operativa (texto simple, sin volumen/fibo)
    z_h1 = ez["intradia"].get("zonas", {})
    z_m15 = ez.get("reaccion", {}).get("zona_1")
    if z_h1:
        z1 = z_h1.get("zona_1")
        if z1:
            body["🧠 TESLABTC.KG"]["sugerencia"] = (
                f"Reacción intradía H1 en {z1['inferior']:,.2f} – {z1['superior']:,.2f}. "
                f"{'Refinar en M15: ' + f'{z_m15["inferior"]:,.2f} – {z_m15["superior"]:,.2f}' if z_m15 else ''}"
            )
        z2 = z_h1.get("zona_2")
        if z2:
            body["🧠 TESLABTC.KG"]["sugerencia_secundaria"] = (
                f"Zona H1 de reentrada: {z2['inferior']:,.2f} – {z2['superior']:,.2f}. "
                "Si la zona 1 no reacciona, considerar ampliar SL para cubrir ambas."
            )

    return body
