# ==============================================
# ⏰ TESLABTC.KG — utils/time_utils.py
# Horarios Colombia para día operativo y sesión Asia
# ==============================================
from __future__ import annotations
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo

TZ_COL = ZoneInfo("America/Bogota")

def now_col() -> datetime:
    return datetime.now(TZ_COL)

def last_closed_daily_window_col(now: datetime | None = None) -> tuple[datetime, datetime]:
    """
    Día operativo cerrado inmediatamente anterior (7:00 PM COL → 7:00 PM COL).
    Devuelve (inicio, fin) ambos en tz COL.
    Ej.: Si ahora es Lun 16:00, devuelve Dom 19:00 → Lun 19:00 (cerró a las 19:00 de hoy).
    """
    now = now or now_col()
    # Último boundary 19:00 COL <= now
    boundary_today = now.replace(hour=19, minute=0, second=0, microsecond=0)
    if now < boundary_today:
        boundary = boundary_today - timedelta(days=1)
    else:
        boundary = boundary_today
    start = boundary - timedelta(hours=24)
    end = boundary
    return start, end

def last_closed_asian_window_col(now: datetime | None = None) -> tuple[datetime, datetime]:
    """
    Última sesión asiática COMPLETA 5:00 PM → 2:00 AM COL (9 horas).
    Devuelve (inicio, fin) ambos en tz COL y cerrados antes de 'now'.
    """
    now = now or now_col()
    today = now.date()
    # Candidatos: [ayer 17:00 → hoy 02:00] y [hoy 17:00 → mañana 02:00]
    start_yday = datetime.combine(today - timedelta(days=1), time(17, 0), tzinfo=TZ_COL)
    end_today_2am = datetime.combine(today, time(2, 0), tzinfo=TZ_COL)
    if now >= end_today_2am:
        # La última completa es la que terminó hoy 02:00
        return start_yday, end_today_2am
    else:
        # Aún no llegó 02:00 de hoy; usar la que terminó ayer 02:00
        start_2y = datetime.combine(today - timedelta(days=2), time(17, 0), tzinfo=TZ_COL)
        end_yday_2am = datetime.combine(today - timedelta(days=1), time(2, 0), tzinfo=TZ_COL)
        return start_2y, end_yday_2am

def col_to_ms(dt_col: datetime) -> int:
    """Epoch ms desde datetime COL."""
    return int(dt_col.timestamp() * 1000)
