# ============================================================
# 🔔 MONITOR EN VIVO — TESLABTC.KG (v3.6.0)
# ============================================================

import os
import asyncio
from datetime import datetime, timedelta, timezone
from utils.price_utils import obtener_precio, obtener_klines_binance
from utils.estructura_utils import evaluar_estructura, definir_escenarios

TZ_COL = timezone(timedelta(hours=-5))

# Intervalo configurable por ENV, por defecto 15 min
MONITOR_INTERVAL_SEC = int(os.getenv("MONITOR_INTERVAL_SEC", "900"))

_MONITOR_RUNNING = False
_ALERTS = []  # últimas N alertas
_MAX_ALERTS = 20

async def live_monitor_loop():
    """Ejecuta el análisis cada MONITOR_INTERVAL_SEC y guarda alertas."""
    global _MONITOR_RUNNING
    if _MONITOR_RUNNING:
        return
    _MONITOR_RUNNING = True
    print(f"[TESLABTC MONITOR] Iniciado. Intervalo: {MONITOR_INTERVAL_SEC}s")

    while _MONITOR_RUNNING:
        try:
            now = datetime.now(TZ_COL)
            precio_data = obtener_precio("BTCUSDT")
            precio = precio_data.get("precio")

            h4 = obtener_klines_binance("BTCUSDT", "4h", 100)
            h1 = obtener_klines_binance("BTCUSDT", "1h", 100)
            m15 = obtener_klines_binance("BTCUSDT", "15m", 100)

            e_h4 = evaluar_estructura(h4); e_h1 = evaluar_estructura(h1); e_m15 = evaluar_estructura(m15)
            estados = {
                "H4 (macro)": e_h4["estado"],
                "H1 (intradía)": e_h1["estado"],
                "M15 (reacción)": e_m15["estado"]
            }
            escenario = definir_escenarios(estados)

            resumen = {
                "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
                "precio": round(precio, 2) if precio else None,
                "estados": estados,
                "escenario": escenario["escenario"],
                "mensaje": escenario["mensaje"]
            }
            _ALERTS.append(resumen)
            if len(_ALERTS) > _MAX_ALERTS:
                _ALERTS.pop(0)

            print(f"[TESLABTC ALERT] {resumen}")

        except Exception as e:
            print(f"[MONITOR ERROR] {e}")

        await asyncio.sleep(MONITOR_INTERVAL_SEC)

def stop_monitor():
    global _MONITOR_RUNNING
    _MONITOR_RUNNING = False
    print("[TESLABTC MONITOR] Detenido.")

def get_alerts():
    if not _ALERTS:
        return {"estado": "sin_alertas", "mensaje": "Aún no hay alertas generadas."}
    return {
        "estado": "🟢 activo" if _MONITOR_RUNNING else "🔴 detenido",
        "ultima_alerta": _ALERTS[-1],
        "alertas_recientes": _ALERTS[-5:],
        "total": len(_ALERTS),
        "intervalo_seg": MONITOR_INTERVAL_SEC
    }
