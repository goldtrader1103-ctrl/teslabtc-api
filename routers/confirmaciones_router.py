from fastapi import APIRouter
from datetime import datetime
from utils.price_utils import obtener_precio
from utils.estructura_utils import obtener_klines, detectar_bos, detectar_barrida

router = APIRouter()

@router.get("/confirmaciones")
def obtener_confirmaciones():
    """
    Endpoint principal de confirmaciones TESLABTC A.P.
    Combina precio real, microestructura y contexto de sesión NY.
    """
    try:
        # 1️⃣ Precio actual
        precio = obtener_precio()

        # 2️⃣ Microestructura (M5)
        data_m5 = obtener_klines("5m")
        bos_m5 = detectar_bos(data_m5)
        barrida = detectar_barrida(data_m5)

        # 3️⃣ Macroestructura (H1 / H4)
        data_h1 = obtener_klines("1h")
        bos_h1 = detectar_bos(data_h1)
        data_h4 = obtener_klines("4h")
        bos_h4 = detectar_bos(data_h4)

        # 4️⃣ Determinar sesión NY (07:00 a 13:30 COL)
        hora_col = datetime.utcnow().hour - 5
        if 7 <= hora_col <= 13:
            sesion_ny = "✅ Activa (07:00–13:30 COL)"
        else:
            sesion_ny = "❌ Cerrada"

        # 5️⃣ Determinar tendencia general (macro)
        if bos_h1 == "BOS Alcista" or bos_h4 == "BOS Alcista":
            direccion_macro = "📈 Alcista"
        elif bos_h1 == "BOS Bajista" or bos_h4 == "BOS Bajista":
            direccion_macro = "📉 Bajista"
        else:
            direccion_macro = "⏸️ Rango / Neutra"

        # 6️⃣ Construir respuesta JSON para el GPT
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "precio_actual": precio,
            "direccion_macro": direccion_macro,
            "sesion_NY": sesion_ny,
            "bos_h4": bos_h4,
            "bos_h1": bos_h1,
            "bos_m5": bos_m5,
            "barrida": barrida,
            "confirmaciones": {
                "BOS H4": bos_h4,
                "BOS H1": bos_h1,
                "BOS M5": bos_m5,
                "Barrida": barrida,
                "Sesión NY": sesion_ny
            },
            "conclusion": f"TESLABTC A.P. — {direccion_macro}. BOS M5: {bos_m5}, Barrida: {barrida}. "
                          f"💬 'Tu mentalidad, disciplina y constancia definen tus resultados.'"
        }

    except Exception as e:
        return {"error": f"Error en confirmaciones TESLABTC: {str(e)}"}
