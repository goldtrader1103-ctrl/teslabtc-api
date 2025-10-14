# ============================================================
# 🧠 TESLABTC.KG – LÓGICA PRINCIPAL (estructura y escenarios)
# ============================================================

from fastapi import FastAPI
from datetime import datetime, timezone, timedelta
from utils.price_utils import (
    obtener_precio,
    obtener_klines_binance,
    detectar_estructura,
    sesion_ny_activa,
    _pdh_pdl,
)
from typing import Dict

app = FastAPI(title="TESLABTC.KG", version="3.2")

TZ_COL = timezone(timedelta(hours=-5))

# ============================================================
# 🔍 FUNCIÓN PRINCIPAL DE ANÁLISIS
# ============================================================

@app.get("/")
def analizar_mercado() -> Dict:
    try:
        # === 1️⃣ Datos base ===
        ahora = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")
        sesion = "✅ Activa (Sesión New York)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"
        precio_data = obtener_precio("BTCUSDT")
        precio = precio_data["precio"]
        fuente = precio_data["fuente"]

        # === 2️⃣ Estructuras multitemporales ===
        klines_h4 = obtener_klines_binance("BTCUSDT", "4h", 100)
        klines_h1 = obtener_klines_binance("BTCUSDT", "1h", 150)
        klines_m15 = obtener_klines_binance("BTCUSDT", "15m", 200)

        estructura_h4 = detectar_estructura(klines_h4)["estado"]
        estructura_h1 = detectar_estructura(klines_h1)["estado"]
        estructura_m15 = detectar_estructura(klines_m15)["estado"]

        # === 3️⃣ Zonas y contexto ===
        zonas = _pdh_pdl("BTCUSDT")
        zonas_h4 = {
            "High": max([v["high"] for v in klines_h4[-5:]]) if klines_h4 else None,
            "Low": min([v["low"] for v in klines_h4[-5:]]) if klines_h4 else None,
        }
        zonas_h1 = {
            "High": max([v["high"] for v in klines_h1[-5:]]) if klines_h1 else None,
            "Low": min([v["low"] for v in klines_h1[-5:]]) if klines_h1 else None,
        }
        zonas_m15 = {
            "High": max([v["high"] for v in klines_m15[-5:]]) if klines_m15 else None,
            "Low": min([v["low"] for v in klines_m15[-5:]]) if klines_m15 else None,
        }

        # === 4️⃣ Lógica de escenarios ===
        if estructura_h4 == "alcista" and estructura_h1 == "alcista":
            escenario = "CONSERVADOR 1"
            razon = "H4 y H1 alineados al alza — flujo limpio y confirmaciones activas."
            accion = (
                "Esperar BOS M5 en zona M15 para ejecutar compra con objetivo 1:3 o más.\n"
                "💡 La gestión del riesgo es la clave de un trader profesional."
            )
        elif estructura_h4 == "bajista" and estructura_h1 == "bajista":
            escenario = "CONSERVADOR 1"
            razon = "H4 y H1 alineados a la baja — continuación institucional bajista."
            accion = (
                "Esperar BOS M5 en retroceso hacia zona M15 para venta con objetivo 1:3.\n"
                "💡 Mantener gestión de riesgo estricta."
            )
        elif estructura_h1 != estructura_h4:
            escenario = "CONSERVADOR 2"
            razon = "H4 y H1 desalineados — posible reentrada o cambio de fase."
            accion = (
                "Esperar confirmación M15–M5 antes de ejecutar. Posible reentrada si hay nueva liquidez pendiente."
            )
        else:
            escenario = "SCALPING CONTRA-TENDENCIA"
            razon = "M15 en retroceso dentro de zona opuesta, flujo intradía limitado."
            accion = (
                "Operación rápida (1:1–1:2 máx) dentro de POI M15 con confirmación M3–M5.\n"
                "💡 Riesgo reducido y cierre parcial recomendado."
            )

        # === 5️⃣ Formato final ===
        resultado = {
            "🧠 TESLABTC.KG": {
                "fecha": ahora,
                "sesión": sesion,
                "precio_actual": f"{precio:,.2f} USD" if precio else "⚙️ No disponible",
                "fuente_precio": fuente,
                "estructura_detectada": {
                    "H4 (macro)": estructura_h4,
                    "H1 (intradía)": estructura_h1,
                    "M15 (reacción)": estructura_m15,
                },
                "zonas": {
                    "PDH (alto 24h)": zonas.get("PDH"),
                    "PDL (bajo 24h)": zonas.get("PDL"),
                    "ZONA H4 (macro)": zonas_h4,
                    "ZONA H1 (intradía)": zonas_h1,
                    "ZONA M15 (reacción)": zonas_m15,
                },
                "escenario": {
                    "escenario": escenario,
                    "nivel": "Institucional (direccional principal)" if "CONSERVADOR" in escenario else "Scalping intradía",
                    "razón": razon,
                    "acción": accion,
                    "tipo": "principal" if "CONSERVADOR" in escenario else "scalp",
                },
                "mensaje": "✨ Análisis completado correctamente",
                "error": "Ninguno",
            }
        }
        return resultado

    except Exception as e:
        return {
            "🧠 TESLABTC.KG": {
                "mensaje": "⚠️ Error durante el análisis",
                "error": str(e),
            }
        }

# ============================================================
# 🚀 EJECUCIÓN LOCAL (solo si se corre fuera de Render)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
