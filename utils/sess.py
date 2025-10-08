from datetime import datetime
import pytz

TZ = pytz.timezone("America/Bogota")

def now_col():
    return datetime.now(TZ)

def ny_session_state():
    t = now_col()
    hour = t.hour + t.minute / 60.0
    # Sesión NY: 7:00–13:30 COL
    active = 7.0 <= hour <= 13.5
    label = "✅ Activa (7:00–13:30 COL)" if active else "❌ Fuera de sesión NY"
    return active, label
