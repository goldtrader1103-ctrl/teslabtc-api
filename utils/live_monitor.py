# ============================================================
# 📡 TESLABTC.KG — utils/live_monitor.py (v3.6.0)
# ============================================================
# Monitor ligero en background:
#  - Mantiene un registro circular de eventos/alertas
#  - Evita consumo alto de CPU/RAM
# ============================================================

import asyncio
from datetime import datetime, timezone, timedelta

TZ_COL = timezone(timedelta(hours=-5))
_ALERTS = []
_MONITOR_ON = True
_MAX_LOG = 200

def _log(msg):
    if len(_ALERTS) >= _MAX_LOG:
        _ALERTS.pop(0)
    _ALERTS.append({"ts": datetime.now(TZ_COL).strftime("%H:%M:%S"), "msg": msg})

async def live_monitor_loop():
    global _MONITOR_ON
    _MONITOR_ON = True
    _log("▶️ Monitor iniciado")
    while _MONITOR_ON:
        # Aquí podrías añadir chequeos reales de estructura/klines
        await asyncio.sleep(15)

def stop_monitor():
    global _MONITOR_ON
    _MONITOR_ON = False
    _log("⏹️ Monitor detenido")

def get_alerts():
    return {
        "estado": "🟢 Activo" if _MONITOR_ON else "⏹️ Detenido",
        "ultima_actualizacion": datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S"),
        "registros": len(_ALERTS),
        "logs": _ALERTS[-80:]  # últimos 80
    }
