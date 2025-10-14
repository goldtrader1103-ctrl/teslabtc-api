# ============================================================
# 🔔 MONITOR EN VIVO — TESLABTC.KG v3.5.0
# ============================================================

import asyncio
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, obtener_klines_binance, sesion_ny_activa
from utils.estructura_utils import evaluar_estructura, definir_escenarios

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ============================================================

TZ_COL = timezone(timedelta(hours=-5))
MONITOR_INTERVAL = 300  # segundos = 5 minutos
MONITOR_RUNNING = False
ALERT_LOG = []  # almacena últimas alertas

# ============================================================
# 🔁 LOOP PRINCIPAL DEL MONITOR
# ============================================================

async def live_monitor_loop():
    """Ejecuta el análisis completo cada 5 minutos y guarda las alertas recientes."""
    global MONITOR_RUNNING
    if MONITOR_RUNNING:
        return  # ya está corriendo

    MONITOR_RUNNING = True
    print("[🔄 MONITOR TESLABTC.KG] Iniciado correctamente.")

    while MONITOR_RUNNING:
        try:
            now = datetime.now(TZ_COL)
            hora_actual = now.strftime("%H:%M:%S")

            # Obtener precio actual
            precio_data = obtener_precio()
            precio = precio_data.get("precio")
            fuente = precio_data.get("fuente")

            # Verificar sesión NY
            sesion = sesion_ny_activa()

            # Obtener velas y estructuras
            velas_h4 = obtener_klines_binance(intervalo="4h", limite=200)
            velas_h1 = obtener_klines_binance(intervalo="1h", limite=200)
            velas_m15 = obtener_klines_binance(intervalo="15m", limite=200)

            estructura = {
                "H4 (macro)": evaluar_estructura(velas_h4, "H4"),
                "H1 (intradía)": evaluar_estructura(velas_h1, "H1"),
                "M15 (reacción)": evaluar_estructura(velas_m15, "M15"),
            }

            escenario = definir_escenarios(estructura, sesion)

            # Crear resumen corto
            resumen = (
                f"[{hora_actual}] {escenario['escenario']} | "
                f"Precio: {precio:,.2f} USD | "
                f"H4: {estructura['H4 (macro)']} / H1: {estructura['H1 (intradía)']} / M15: {estructura['M15 (reacción)']}"
            )

            # Guardar alerta
            ALERT_LOG.append({
                "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
                "escenario": escenario["escenario"],
                "precio": round(precio, 2) if precio else None,
                "estructura": estructura,
                "resumen": resumen,
                "fuente_precio": fuente,
            })

            # Limitar tamaño del log a las últimas 15 alertas
            if len(ALERT_LOG) > 15:
                ALERT_LOG.pop(0)

            print(f"[📈 TESLABTC MONITOR] {resumen}")

        except Exception as e:
            print(f"[❌ MONITOR ERROR] {e}")

        await asyncio.sleep(MONITOR_INTERVAL)  # espera 5 minutos antes del siguiente análisis

# ============================================================
# ⛔ DETENER EL MONITOR
# ============================================================

def stop_monitor():
    """Detiene el monitor."""
    global MONITOR_RUNNING
    MONITOR_RUNNING = False
    print("[🛑 MONITOR TESLABTC.KG] Detenido.")

# ============================================================
# 📋 CONSULTAR ALERTAS RECIENTES
# ============================================================

def get_alerts() -> dict:
    """Devuelve las últimas alertas registradas."""
    if not ALERT_LOG:
        return {"estado": "sin_alertas", "mensaje": "Aún no hay alertas generadas."}

    return {
        "estado": "🟢 activo" if MONITOR_RUNNING else "🔴 detenido",
        "ultima_alerta": ALERT_LOG[-1],
        "alertas_recientes": ALERT_LOG[-5:],  # últimas 5
        "total_registradas": len(ALERT_LOG),
    }
