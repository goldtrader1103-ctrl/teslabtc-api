# ============================================================
# ⚙️ UTILIDADES TESLABTC A.P. — PRECIO Y SESIÓN NY
# ============================================================

import requests
from datetime import datetime, time
import pytz

# Zona horaria Colombia (UTC-5)
TZ_COL = pytz.timezone("America/Bogota")


# ============================================================
# 💰 OBTENER PRECIO ACTUAL DESDE BINANCE
# ============================================================
def obtener_precio(simbolo: str = "BTCUSDT") -> float | None:
    """Obtiene el precio actual del símbolo desde Binance."""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo.upper()}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return float(data["price"])
    except Exception as e:
        print(f"[Error obtener_precio] {e}")
        return None


# ============================================================
# 🕓 VALIDAR SI LA SESIÓN DE NY ESTÁ ACTIVA
# ============================================================
def sesion_ny_activa(ahora: datetime | None = None) -> bool:
    """Devuelve True si la sesión NY está activa (lunes–viernes, 07:00–13:30 COL)."""
    if ahora is None:
        ahora = datetime.now(TZ_COL)

    dia = ahora.weekday()  # 0 = Lunes ... 6 = Domingo
    hora = ahora.time()
    inicio = time(7, 0)
    fin = time(13, 30)

    if dia >= 5:  # Sábado o domingo
        return False
    return inicio <= hora <= fin


# ============================================================
# 📈 OBTENER KLINES (VELAS) DE BINANCE
# ============================================================
def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "1m", limite: int = 50):
    """Obtiene datos OHLC de Binance."""
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo.upper()}&interval={intervalo}&limit={limite}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        velas = []
        for k in data:
            velas.append({
                "timestamp": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        return velas
    except Exception as e:
        print(f"[Error obtener_klines_binance] {e}")
        return None


# ============================================================
# 📊 CALCULAR PDH / PDL (Previous Day High / Low)
# ============================================================
def _pdh_pdl(simbolo: str = "BTCUSDT", intervalo: str = "1h", limite: int = 24):
    """
    Devuelve el máximo (PDH) y mínimo (PDL) del día anterior desde datos de Binance.
    intervalo: temporalidad (por defecto 1h)
    limite: cantidad de velas a analizar (24 = 1 día)
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo.upper()}&interval={intervalo}&limit={limite}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        highs = [float(k[2]) for k in data]
        lows = [float(k[3]) for k in data]
        return {"PDH": max(highs), "PDL": min(lows)}
    except Exception as e:
        print(f"[Error _pdh_pdl] {e}")
        return {"PDH": None, "PDL": None}
# ============================================================
# 🧭 DETECTAR ESTRUCTURA (BOS / TENDENCIA)
# ============================================================

def detectar_estructura(simbolo: str = "BTCUSDT", intervalo: str = "15m", limite: int = 50):
    """
    Detecta la estructura general del mercado con base en los últimos cierres.
    Retorna:
        - dirección: 'alcista', 'bajista' o 'rango'
        - BOS: True si hay ruptura estructural reciente
        - último_alto y último_bajo (niveles clave)
    """
    import requests

    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo.upper()}&interval={intervalo}&limit={limite}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        cierres = [float(k[4]) for k in data]
        altos = [float(k[2]) for k in data]
        bajos = [float(k[3]) for k in data]

        max_actual = max(altos[-5:])
        min_actual = min(bajos[-5:])
        cierre_actual = cierres[-1]

        if cierre_actual > max(altos[-10:]):
            direccion = "alcista"
            BOS = True
        elif cierre_actual < min(bajos[-10:]):
            direccion = "bajista"
            BOS = True
        else:
            direccion = "rango"
            BOS = False

        return {
            "simbolo": simbolo,
            "intervalo": intervalo,
            "direccion": direccion,
            "BOS": BOS,
            "ultimo_alto": round(max_actual, 2),
            "ultimo_bajo": round(min_actual, 2),
        }

    except Exception as e:
        print(f"[Error detectar_estructura] {e}")
        return {
            "simbolo": simbolo,
            "intervalo": intervalo,
            "direccion": "error",
            "BOS": False,
            "ultimo_alto": None,
            "ultimo_bajo": None,
        }
