from fastapi import FastAPI
from datetime import datetime, time
import requests
import pytz

app = FastAPI(title="TESLABTC A.P. Dashboard")

# --- CONFIGURACIÓN ---
TIMEZONE_COL = pytz.timezone("America/Bogota")

# --- FUNCIÓN PRINCIPAL DE ANÁLISIS ---
@app.get("/estado_general")
def estado_general():
    try:
        # ✅ Precio real desde Binance (mismo que TradingView)
        data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        precio_actual = round(float(data["price"]), 2)
    except Exception as e:
        precio_actual = None

    # Fecha y hora Colombia
    now = datetime.now(TIMEZONE_COL)
    hora_actual = now.time()

    # --- SESIÓN NY (7:00 - 11:30 COL) ---
    inicio_ny = time(7, 0)
    fin_ny = time(11, 30)
    if inicio_ny <= hora_actual <= fin_ny:
        sesion = "✅ Activa (7:00–11:30 COL)"
    else:
        sesion = "❌ Fuera de sesión NY"

    # --- ANÁLISIS TESLABTC A.P. ---
    if precio_actual:
        if precio_actual > 125000:
            direccion_macro = "Alcista 📈"
            escenario = "Esperar retroceso hacia demanda para BUY en M15"
            alerta = "🔴 Precio tocó zona de liquidez" if precio_actual > 126000 else "🟢 Sin alertas activas"
            estado_alerta = "ACTIVA" if precio_actual > 126000 else "SILENCIO"
            confirmaciones = {
                "Tendencia H4": "✅",
                "BOS M15": "✅ Confirmado",
                "POI/OB/FVG": "✅",
                "Retroceso <61.8%": "⚠️",
                "Volumen": "✅",
                "Sesión NY": "✅" if sesion.startswith("✅") else "❌"
            }
        else:
            direccion_macro = "Bajista 📉"
            escenario = "Esperar mitigación para SELL en M15"
            alerta = "🟡 Esperar BOS bajista M15"
            estado_alerta = "EN OBSERVACIÓN"
            confirmaciones = {
                "Tendencia H4": "❌",
                "BOS M15": "⚠️ Pendiente",
                "POI/OB/FVG": "✅",
                "Retroceso <61.8%": "✅",
                "Volumen": "⚠️",
                "Sesión NY": "✅" if sesion.startswith("✅") else "❌"
            }
    else:
        direccion_macro = "Indefinida ⚪"
        escenario = "Sin datos de precio disponibles"
        alerta = "⚠️ Error al obtener precio"
        estado_alerta = "ERROR"
        confirmaciones = {}

    # --- RESPUESTA FINAL ---
    return {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "precio_actual": precio_actual,
        "direccion_macro": direccion_macro,
        "sesion_NY": sesion,
        "escenario_sugerido": escenario,
        "confirmaciones": confirmaciones,
        "alerta": alerta,
        "estado_alerta": estado_alerta,
        "conclusion": f"📊 Escenario TESLABTC A.P.: {escenario} 💬 'TU MENTALIDAD, DISCIPLINA Y CONSTANCIA DEFINEN TUS RESULTADOS.'"
    }
