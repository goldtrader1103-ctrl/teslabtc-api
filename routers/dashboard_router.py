from fastapi import APIRouter
from utils.price_utils import obtener_precio, obtener_klines_binance
from datetime import datetime
import pytz

router = APIRouter()

@router.get("/estado_general", tags=["TESLABTC"])
def estado_general_teslabtc():
    """
    Análisis TESLABTC A.P. — versión con detección de setups A+ y estructura H1–M5.
    """
    timestamp = datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")
    precio = obtener_precio()

    # -------------------------------
    # Sesión NY (7:00 a 13:30 COL)
    # -------------------------------
    hora_actual = datetime.now(pytz.timezone("America/Bogota")).hour + datetime.now(pytz.timezone("America/Bogota")).minute/60
    sesion_activa = 7 <= hora_actual <= 13.5
    sesion_ny = "✅ Activa (07:00–13:30 COL)" if sesion_activa else "🕓 Fuera de sesión NY"

    # -------------------------------
    # Confirmaciones simuladas (debes conectar con tus condiciones reales)
    # -------------------------------
    bos_h1 = True       # Flujo macro bajista
    bos_m15 = False     # Sin BOS M15 (impulso extendido)
    bos_m5 = True       # Confirmación interna M5
    barrida_liquidez = True  # Barrida de Asia o PDH detectada

    # -------------------------------
    # Setup A+ y clasificación de probabilidad
    # -------------------------------
    if bos_h1 and bos_m5 and barrida_liquidez and not bos_m15:
        escenario_probabilidad = "ALTA 🔥"
        detalle_escenario = "BOS M5 alineado con BOS H1 tras barrida de liquidez — setup A+ TESLABTC A.P."
        escenario_sugerido = "Esperar redistribución o reacción en OB/FVG M5 a favor de H1."
    elif bos_m15:
        escenario_probabilidad = "MEDIA ✅"
        detalle_escenario = "BOS M15 confirmado dentro de zona H1/H4 — setup clásico TESLABTC."
        escenario_sugerido = "Retroceso M5 dentro de OB/FVG M15."
    else:
        escenario_probabilidad = "BAJA ⚠️"
        detalle_escenario = "Sin BOS claro en M15 ni M5 — observación de estructura."
        escenario_sugerido = "Esperar BOS confirmatorio o mitigación profunda."

    # -------------------------------
    # Klines (velas recientes para análisis futuro)
    # -------------------------------
    velas = obtener_klines_binance("1h", limite=20)
    ultima_vela = velas[-1] if velas else None

    # -------------------------------
    # Respuesta JSON
    # -------------------------------
    resultado = {
        "timestamp": timestamp,
        "precio_actual": precio,
        "direccion_macro": "Bajista 📉" if bos_h1 else "Rango ⏸️",
        "sesion_NY": sesion_ny,
        "escenario_probabilidad": escenario_probabilidad,
        "detalle_escenario": detalle_escenario,
        "escenario_sugerido": escenario_sugerido,
        "confirmaciones": {
            "BOS H1": "✅" if bos_h1 else "❌",
            "BOS M15": "✅" if bos_m15 else "❌",
            "BOS M5": "✅" if bos_m5 else "❌",
            "Barrida": "✅" if barrida_liquidez else "❌",
            "Sesión NY": "✅" if sesion_activa else "❌"
        },
        "ultima_vela": ultima_vela,
        "conclusion": f"TESLABTC A.P. — Acción del Precio Pura. Escenario {escenario_probabilidad}. 💬 'Tu mentalidad, disciplina y constancia definen tus resultados.'"
    }

    return resultado
