# utils/time_utils.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ_COL = ZoneInfo("America/Bogota")  # Colombia sin DST

def now_col():
    return datetime.now(TZ_COL)

def col_dt(y, m, d, hh, mm=0, ss=0):
    return datetime(y, m, d, hh, mm, ss, tzinfo=TZ_COL)

def window_inclusive(start_dt, end_dt, dt):
    """True si dt está dentro del [start_dt, end_dt) considerando cruce de día."""
    if end_dt <= start_dt:
        # ventana cruza medianoche
        return dt >= start_dt or dt < end_dt
    return start_dt <= dt < end_dt
