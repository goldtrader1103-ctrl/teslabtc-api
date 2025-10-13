# ============================================================
# ⚙️ UTILIDADES DE PRECIO – TESLABTC.KG
# ============================================================

import requests
from datetime import datetime, timedelta, timezone

# Zona horaria Colombia (UTC-5)
TZ_COL = timezone(timedelta(hours=-5))


# ============================================================
# 💰 OBTENER PRECIO ACTUAL DE BINANCE
# ============================================================

def obtener_precio(simbolo: str = "BTCUSDT") -> float | None:
    """
    Obtiene el precio actual del símbolo desde Binance con tolerancia a errores.
    Retorna None si no se puede conectar o hay error de respuesta.
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("price"))
        else:
            print(f"[obtener_precio] Error {response.status_code} al consultar Binance.")
            return None
    except requests.exceptions.Timeout:
        print("[obtener_precio] Tiempo de espera agotado al conectar con Binance.")
        return None
    except Exception as e:
        print(f"[obtener_precio] Error inesperado: {e}")
        return None


# ============================================================
# 🕐 SESIÓN NEW YORK ACTIVA
# ============================================================

def sesion_ny_activa() -> bool:
    """
    Determina si la sesión de Nueva York está activa.
    Horario NY: 07:00 - 13:30 (hora Colombia)
    """
    hora_actual = datetime.now(TZ_COL)
    return 7 <= hora_actual.hour < 13 or (hora_actual.hour == 13 and hora_actual.minute <= 30)


# ============================================================
# 📊 OBTENER KLINES DE BINANCE
# ============================================================

def obtener_klines_binance(simbolo: str = "BTCUSDT", intervalo: str = "5m", limite: int = 200):
    """
    Obtiene datos de velas (klines) desde Binance.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval={intervalo}&limit={limite}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        velas = [
            {
                "open_time": datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in data
        ]
        return velas
    except Exception as e:
        print(f"[obtener_klines_binance] Error: {e}")
        return None


# ============================================================
# 📈 DETECTAR ESTRUCTURA (Simplificado)
# ============================================================

def detectar_estructura(velas: list) -> str:
    """
    Analiza velas recientes y detecta estructura básica (BOS alcista/bajista).
    """
    if not velas or len(velas) < 5:
        return "⚙️ Sin datos suficientes"

    highs = [v["high"] for v in velas[-5:]]
    lows = [v["low"] for v in velas[-5:]]

    if highs[-1] > max(highs[:-1]):
        return "📈 BOS Alcista"
    elif lows[-1] < min(lows[:-1]):
        return "📉 BOS Bajista"
    else:
        return "⚙️ Estructura lateral"


# ============================================================
# 📊 CALCULAR PDH / PDL (Previous Day High / Low)
# ============================================================

def _pdh_pdl(simbolo: str = "BTCUSDT"):
    """
    Devuelve el máximo (PDH) y mínimo (PDL) del día anterior.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=1h&limit=48"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # Filtrar solo las últimas 24 horas
        cutoff = datetime.now(TZ_COL) - timedelta(hours=24)
        data_filtrada = [k for k in data if datetime.fromtimestamp(k[0] / 1000, tz=TZ_COL) > cutoff]

        highs = [float(k[2]) for k in data_filtrada]
        lows = [float(k[3]) for k in data_filtrada]

        return {"PDH": max(highs), "PDL": min(lows)}
    except Exception as e:
        print(f"[pdh_pdl] Error: {e}")
        return {"PDH": None, "PDL": None}
