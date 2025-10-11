from datetime import datetime, time
import pytz

# Zona horaria Colombia (UTC-5)
TZ_COL = pytz.timezone("America/Bogota")

def sesion_ny_activa(ahora: datetime = None) -> bool:
    """
    Determina si la sesión de Nueva York está activa.
    Horario oficial TESLABTC A.P.: 07:00–13:30 COL (lunes a viernes)
    """
    if ahora is None:
        ahora = datetime.now(TZ_COL)

    dia_semana = ahora.weekday()  # 0 = lunes, 6 = domingo
    hora_actual = ahora.time()

    inicio = time(7, 0)
    fin = time(13, 30)

    # Si es sábado (5) o domingo (6), sesión cerrada
    if dia_semana >= 5:
        return False

    # Si está dentro del rango horario, sesión activa
    return inicio <= hora_actual <= fin

