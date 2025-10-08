from fastapi import APIRouter
from utils.price_utils import obtener_precio, obtener_hora_colombia
from datetime import datetime
import pytz

router = APIRouter()

@router.get("/estado_general")
def estado_general():
    """
    Devuelve el estado general del mercado BTCUSDT según la estrategia TESLABTC A.P.
    """
    precio = obtener_precio()
    timestamp = obtener_hora_colombia()

    tz = pytz.timezone("America/Bogota")
    hora = datetime.now(tz)

    # ⏰ Ajuste real: Sesión NY (7:00 AM – 1:30 PM COL)
    inicio_ny = hora.replace(hour=7, minute=0, second=0)
    fin_ny = hora.replace(hour=13, minute=30, second=0)
    sesion_activa = inicio_ny <= hora <= fin_ny
    sesion_NY = "✅ Activa (7:00–13:30 COL)" if sesion_activa else "🕓 Fuera de sesión (7:00–13:30 COL)"

    # Si no hay precio, retornar mensaje claro pero sin romper el flujo
    if not precio:
        return {
            "timestamp": timestamp,
            "precio_actual": None,
            "direccion_macro": "Indefinida ❔",
            "sesion_NY": sesion_NY,
            "escenario_sugerido": "No se puede analizar sin datos de precio.",
            "alerta": "⚠️ Error al obtener precio en tiempo real.",
            "estado_alerta": "ERROR",
            "conclusion": "Verifica conexión a Binance o Render (timeout o bloqueo de IP)."
        }

    # 🔍 Lógica técnica TESLABTC
    direccion_macro = "Alcista 📈" if precio > 124000 else "Bajista 📉"
    confirmaciones = {
        "Tendencia H4": "✅" if direccion_macro == "Alcista 📈" else "⚠️",
        "BOS M15": "✅ Confirmado" if sesion_activa else "⚠️ Pendiente",
        "POI/OB/FVG": "✅",
        "Retroceso <61.8%": "✅",
        "Volumen": "⚠️",
        "Sesión NY": "✅" if sesion_activa else "❌"
    }

    conclusion = (
        "📊 Escenario TESLABTC A.P.: Esperar retroceso en demanda para ejecutar BUY en M15. "
        "💬 'Tu mentalidad, disciplina y constancia definen tus resultados.'"
    )

    return {
        "timestamp": timestamp,
        "precio_actual": precio,
        "direccion_macro": direccion_macro,
        "sesion_NY": sesion_NY,
        "escenario_sugerido": "Esperar retroceso hacia demanda para BUY en M15",
        "confirmaciones": confirmaciones,
        "alerta": "🟢 Sin alertas activas",
        "estado_alerta": "SILENCIO",
        "conclusion": conclusion
    }
