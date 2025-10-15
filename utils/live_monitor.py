# ============================================================
# ⏱️ MONITOR EN VIVO — TESLABTC.KG
# ============================================================

import asyncio

_alerts = []

async def live_monitor_loop():
    """Simula monitoreo continuo (placeholder)."""
    while True:
        await asyncio.sleep(10)

def stop_monitor():
    _alerts.clear()

def get_alerts():
    return {"estado": "🟢 Activo", "alertas": _alerts}
