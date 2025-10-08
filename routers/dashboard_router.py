from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import obtener_precio

router = APIRouter()

@router.get("/estado_general")
def estado_general():
    precio = obtener_precio()
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio,
        "direccion_macro": "Alcista 📈",
        "sesion_NY": "✅ Activa (13:30–17:00 COL)",
        "escenario_sugerido": "Esperar retroceso hacia demanda para BUY en M15",
        "confirmaciones": {
            "Tendencia H4": "✅",
            "BOS M15": "✅ Confirmado",
            "POI/OB/FVG": "✅",
            "Retroceso <61.8%": "⚠️",
            "Volumen": "✅",
            "Sesión NY": "✅"
        },
        "alerta": "🟢 Sin alertas activas",
        "estado_alerta": "SILENCIO",
        "conclusion": "📊 Escenario TESLABTC A.P.: Esperar retroceso en demanda para ejecutar BUY en M15. 💬 'Tu mentalidad, disciplina y constancia definen tus resultados.'"
    }

