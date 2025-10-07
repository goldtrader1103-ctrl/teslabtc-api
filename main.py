# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from statistics import mean

app = FastAPI(title="TESLABTC A.P API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BINANCE = "https://api.binance.com"
SYMBOL = "BTCUSDT"

# -------------------------------
# Utilidades de datos (Binance)
# -------------------------------
def get_json(url, params=None):
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def price_now():
    # Precio spot
    data = get_json(f"{BINANCE}/api/v3/ticker/price", {"symbol": SYMBOL})
    return float(data["price"])

def stats_24h():
    d = get_json(f"{BINANCE}/api/v3/ticker/24hr", {"symbol": SYMBOL})
    return {
        "alto": float(d["highPrice"]),
        "bajo": float(d["lowPrice"]),
        "vol": float(d["volume"]),
    }

def klines(interval="15m", limit=200):
    # Devuelve OHLCV de Binance en lista de dicts
    raw = get_json(f"{BINANCE}/api/v3/klines", {"symbol": SYMBOL, "interval": interval, "limit": limit})
    out = []
    for k in raw:
        out.append({
            "open_time": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": int(k[6])
        })
    return out

def prev_day_high_low():
    # Usa velas diarias para extraer PDH/PDL (día previo)
    d = get_json(f"{BINANCE}/api/v3/klines", {"symbol": SYMBOL, "interval": "1d", "limit": 3})
    # d[-2] = día previo (penúltima)
    if len(d) < 2:
        return None, None
    pdh = float(d[-2][2])
    pdl = float(d[-2][3])
    return pdh, pdl

# -------------------------------
# Lógica TESLABTC A.P (determinística)
# -------------------------------
def in_ny_session_bogota(now_bog):
    # NY para TESLABTC A.P: 7:00–11:30 COL
    start = now_bog.replace(hour=7, minute=0, second=0, microsecond=0)
    end   = now_bog.replace(hour=11, minute=30, second=0, microsecond=0)
    return start <= now_bog <= end

def swing_points(candles, lookback=5):
    # Devuelve listas de (idx, precio) para swings confirmados
    highs = []
    lows = []
    for i in range(lookback, len(candles)-lookback):
        h = candles[i]["high"]
        l = candles[i]["low"]
        is_swing_high = all(h > candles[i-j]["high"] for j in range(1, lookback+1)) and \
                        all(h > candles[i+j]["high"] for j in range(1, lookback+1))
        is_swing_low  = all(l < candles[i-j]["low"]  for j in range(1, lookback+1)) and \
                        all(l < candles[i+j]["low"]  for j in range(1, lookback+1))
        if is_swing_high:
            highs.append((i, h))
        if is_swing_low:
            lows.append((i, l))
    return highs, lows

def detect_bos_m15(m15):
    # BOS si el último cierre rompe el último swing en esa dirección
    if len(m15) < 50:
        return {"bos": "N/A", "detalle": "Insuficientes velas"}
    highs, lows = swing_points(m15, lookback=3)
    if not highs or not lows:
        return {"bos": "N/A", "detalle": "No hay swings confirmados"}
    last_close = m15[-1]["close"]
    last_swing_high = highs[-1][1]
    last_swing_low  = lows[-1][1]
    if last_close > last_swing_high:
        return {"bos": "Alcista", "nivel": last_swing_high}
    if last_close < last_swing_low:
        return {"bos": "Bajista", "nivel": last_swing_low}
    return {"bos": "Sin ruptura", "nivel": None}

def last_ob_zone_after_bos(m15, bos_info):
    # OB simple: última vela contraria antes del rompimiento
    # Si BOS Alcista -> última vela bajista antes de la vela que rompe
    # Si BOS Bajista -> última vela alcista antes de la vela que rompe
    if bos_info.get("bos") not in ("Alcista", "Bajista"):
        return None
    last_close = m15[-1]["close"]
    # Encontrar la vela de ruptura (heurística: la última que cerró por encima/del último swing)
    highs, lows = swing_points(m15, lookback=3)
    if bos_info["bos"] == "Alcista" and highs:
        level = bos_info["nivel"] or highs[-1][1]
        # vela de ruptura ~ la primera vela reciente cuyo close cruza ese nivel
        break_idx = None
        for i in range(len(m15)-1, -1, -1):
            if m15[i]["close"] > level:
                break_idx = i
                break
        if break_idx is None:
            return None
        # Buscar última vela roja antes de break_idx
        for j in range(break_idx-1, max(0, break_idx-20), -1):
            if m15[j]["close"] < m15[j]["open"]:
                # Demanda (zona del OB): [open, low]
                return {"tipo": "Demanda", "zona": [m15[j]["open"], m15[j]["low"]], "idx": j}
    if bos_info["bos"] == "Bajista" and lows:
        level = bos_info["nivel"] or lows[-1][1]
        break_idx = None
        for i in range(len(m15)-1, -1, -1):
            if m15[i]["close"] < level:
                break_idx = i
                break
        if break_idx is None:
            return None
        # Buscar última vela verde antes de break_idx
        for j in range(break_idx-1, max(0, break_idx-20), -1):
            if m15[j]["close"] > m15[j]["open"]:
                # Oferta (zona del OB): [high, open]
                return {"tipo": "Oferta", "zona": [m15[j]["high"], m15[j]["open"]], "idx": j}
    return None

def last_fvg_zone(m15):
    # FVG bullish: high[n-1] < low[n+1]
    # FVG bearish: low[n-1] > high[n+1]
    # Tomamos la más reciente si existe
    if len(m15) < 5:
        return None
    for i in range(len(m15)-3, 1, -1):
        a = m15[i-1]; b = m15[i]; c = m15[i+1]
        # Bullish gap
        if a["high"] < c["low"]:
            return {"tipo": "Bullish", "zona": [a["high"], c["low"]], "idx": i}
        # Bearish gap
        if a["low"] > c["high"]:
            return {"tipo": "Bearish", "zona": [c["high"], a["low"]], "idx": i}
    return None

def volume_context_m15(m15):
    vols = [c["volume"] for c in m15[-30:]]
    if len(vols) < 10:
        return {"estado": "N/A", "detalle": "Sin datos"}
    avg = mean(vols[:-1])
    last = vols[-1]
    spike = last > 1.5 * avg
    return {"estado": "Spike ✅" if spike else "Normal", "ultimo": last, "promedio": avg}

def near_level(price, level, pct=0.15):
    # pct = 0.15% por defecto
    thresh = level * (pct/100.0)
    return abs(price - level) <= thresh

def suggested_scenario(direction_macro, bos_m15, ny_active):
    # TESLABTC A.P: gatillo obligatorio BOS M15 en zona de interés
    if bos_m15["bos"] == "Alcista":
        base = "Esperar retroceso hacia DEMANDA (OB/FVG) para BUY en M15"
    elif bos_m15["bos"] == "Bajista":
        base = "Esperar mitigación en OFERTA (OB/FVG) para SELL en M15"
    else:
        base = "Sin gatillo: esperar BOS en M15 dentro de zona H1/H4"
    if not ny_active:
        base += " • (Fuera de sesión NY, operar con cautela)"
    return base

def direction_macro_h1(m15, h1):
    # Regla: si hay BOS en H1 seguimos ese flujo; sino tendencia vigente (heurística simple con EMA de cierres)
    if len(h1) < 50:
        return "Indefinida"
    # BOS H1 básico
    highs, lows = swing_points(h1, lookback=3)
    if highs and h1[-1]["close"] > highs[-1][1]:
        return "Alcista 📈"
    if lows and h1[-1]["close"] < lows[-1][1]:
        return "Bajista 📉"
    # fallback: pendiente simple últimos cierres
    last5 = [c["close"] for c in h1[-5:]]
    if last5[-1] > last5[0]:
        return "Alcista 📈"
    if last5[-1] < last5[0]:
        return "Bajista 📉"
    return "Rango"

# -------------------------------
# Endpoint unificado
# -------------------------------
@app.get("/")
def root():
    return {"message": "🚀 TESLABTC A.P API online"}

@app.get("/estado_general")
def estado_general():
    now_bog = datetime.now(ZoneInfo("America/Bogota"))
    ny = in_ny_session_bogota(now_bog)

    # Datos de mercado
    spot = price_now()
    s24 = stats_24h()
    pdh, pdl = prev_day_high_low()

    # Velas
    h4 = klines("4h", 250)
    h1 = klines("1h", 250)
    m15 = klines("15m", 250)
    m5  = klines("5m",  250)

    # Dirección macro (H1 con BOS)
    macro = direction_macro_h1(m15, h1)

    # Confirmaciones TESLABTC A.P
    bos_m15 = detect_bos_m15(m15)
    ob = last_ob_zone_after_bos(m15, bos_m15)
    fvg = last_fvg_zone(m15)
    volctx = volume_context_m15(m15)

    # Confirmaciones (semáforo)
    conf = {
        "Tendencia H4": "✅" if (len(h4) >= 5 and h4[-1]["close"] > h4[-5]["close"]) else "⚠️",
        "BOS M15": "✅ Confirmado" if bos_m15.get("bos") in ("Alcista", "Bajista") else "❌ Pendiente",
        "POI/OB/FVG": "✅" if (ob or fvg) else "❌",
        "Volumen": "✅" if volctx["estado"].startswith("Spike") else "⚠️",
        "Sesión NY": "✅" if ny else "❌",
    }

    # Alertas (liquidez PDH/PDL + zonas OB/FVG)
    alertas = []
    if pdh and near_level(spot, pdh, pct=0.15):
        alertas.append(f"🟡 Precio cerca del PDH ({round(pdh,2)})")
    if pdl and near_level(spot, pdl, pct=0.15):
        alertas.append(f"🟡 Precio cerca del PDL ({round(pdl,2)})")
    if ob:
        lo, hi = (min(ob["zona"]), max(ob["zona"]))
        if lo <= spot <= hi:
            alertas.append(f"🟠 Precio dentro del OB de {ob['tipo']} {round(lo,2)}–{round(hi,2)}")
    if fvg:
        lo, hi = (min(fvg["zona"]), max(fvg["zona"]))
        if lo <= spot <= hi:
            alertas.append(f"🟠 Precio dentro del FVG {fvg['tipo']} {round(lo,2)}–{round(hi,2)}")

    estado_alerta = "ACTIVA" if alertas else "SILENCIO"
    alerta_texto = " | ".join(alertas) if alertas else "🟢 Sin alertas activas"

    # Escenario sugerido TESLABTC A.P (reglas)
    escenario = suggested_scenario(macro, bos_m15, ny)

    # Construcción del dashboard unificado
    salida = {
        "timestamp": now_bog.strftime("%Y-%m-%d %H:%M:%S"),
        "par": "BTCUSDT (Binance spot)",
        "precio_actual": round(spot, 2),
        "rango_24h": {"alto": round(s24["alto"], 2), "bajo": round(s24["bajo"], 2)},
        "PDH_PDL": {"PDH": round(pdh, 2) if pdh else None, "PDL": round(pdl, 2) if pdl else None},
        "sesion_NY": "✅ Activa (7:00–11:30 COL)" if ny else "❌ Fuera de sesión NY",
        "direccion_macro": macro,
        "confirmaciones": conf,
        "detalles_tecnicos": {
            "BOS_M15": bos_m15,
            "OB": ob,
            "FVG": fvg,
            "Volumen": volctx
        },
        "escenario_sugerido": escenario,
        "alerta": alerta_texto,
        "estado_alerta": estado_alerta,
        "gestion_trade": {
            "reglas": [
                "BOS en M15 obligatorio en zona H1/H4",
                "Ejecución M5: retroceso a OB/FVG o micro-BOS",
                "Entrada: inicio o 50% del OB/FVG",
                "SL en invalidación estructural • TP mínimo RRR 1:3",
                "BE en 1:1 • Parcial 50% en 1:2 • Dejar correr a 1:3 o próxima liquidez"
            ]
        },
        "nota_fundamental": "Revisa NFP/CPI/FED si hay evento del día. Las noticias son complementarias; la base es acción del precio.",
        "frase": "TU MENTALIDAD, DISCIPLINA Y CONSTANCIA DEFINEN TUS RESULTADOS."
    }
    return salida

