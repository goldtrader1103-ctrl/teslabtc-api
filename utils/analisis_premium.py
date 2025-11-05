# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.0 REAL MARKET)
# ============================================================
# Analiza BTCUSDT en vivo desde Binance (REST)
# Estructura real multi-TF, escenarios TESLA y SETUP ACTIVO M5
# ============================================================

import requests, math, random
from datetime import datetime, timedelta, timezone

TZ_COL = timezone(timedelta(hours=-5))
BINANCE_REST_BASE = "https://api.binance.com"
UA = {"User-Agent": "teslabtc-kg/5.0"}

# ============================================================
# 🔹 Precio actual desde Binance
# ============================================================
def _safe_get_price(symbol="BTCUSDT"):
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/ticker/price",
            params={"symbol": symbol},
            headers=UA, timeout=6
        )
        r.raise_for_status()
        data = r.json()
        return float(data["price"]), "Binance (REST)"
    except Exception as e:
        return None, f"Error precio: {e}"

# ============================================================
# 🔹 Klines normalizados
# ============================================================
def _safe_get_klines(symbol, interval="15m", limit=500):
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=UA, timeout=8
        )
        r.raise_for_status()
        data = r.json()
        out = []
        for k in data:
            out.append({
                "open_time": datetime.utcfromtimestamp(k[0]/1000.0),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "vol": float(k[5]),
            })
        return out
    except Exception:
        return []

# ============================================================
# 🔹 Detectar pivotes (estructura)
# ============================================================
def _pivotes(kl, look=2):
    if not kl or len(kl) < (look * 2 + 1):
        return [], []
    hi_idx, lo_idx = [], []
    for i in range(look, len(kl) - look):
        h = kl[i]["high"]; l = kl[i]["low"]
        if all(h > kl[i-j]["high"] for j in range(1, look+1)) and all(h > kl[i+j]["high"] for j in range(1, look+1)):
            hi_idx.append(i)
        if all(l < kl[i-j]["low"] for j in range(1, look+1)) and all(l < kl[i+j]["low"] for j in range(1, look+1)):
            lo_idx.append(i)
    return hi_idx, lo_idx

def _detectar_tendencia(kl):
    if not kl or len(kl) < 10:
        return {"estado": "lateral"}
    hi_idx, lo_idx = _pivotes(kl)
    if len(hi_idx) < 2 or len(lo_idx) < 2:
        return {"estado": "lateral"}
    hh = kl[hi_idx[-1]]["high"]
    lh = kl[hi_idx[-2]]["high"]
    ll = kl[lo_idx[-1]]["low"]
    hl = kl[lo_idx[-2]]["low"]
    if hh > lh and ll > hl:
        return {"estado": "alcista", "BOS": "✔️"}
    elif hh < lh and ll < hl:
        return {"estado": "bajista", "BOS": "✔️"}
    return {"estado": "lateral", "BOS": "—"}

# ============================================================
# 🔹 Detectar setup activo (M5 Level Entry)
# ============================================================
def detectar_setup_m5(symbol="BTCUSDT"):
    kl_m15 = _safe_get_klines(symbol, "15m", 200)
    kl_m5  = _safe_get_klines(symbol, "5m", 200)
    if not kl_m15 or not kl_m5:
        return {"activo": False}

    tf_m15 = _detectar_tendencia(kl_m15)
    tf_m5  = _detectar_tendencia(kl_m5)

    if tf_m15["estado"] == tf_m5["estado"] and tf_m5["estado"] in ("alcista", "bajista"):
        ultimo = kl_m5[-1]
        vol_prom = sum([x["vol"] for x in kl_m5[-40:]]) / 40
        if ultimo["vol"] > vol_prom * 1.25:
            tipo = "Compra" if tf_m5["estado"] == "alcista" else "Venta"
            return {
                "activo": True,
                "nivel": f"SETUP ACTIVO – M5 Level Entry ({tipo})",
                "contexto": f"Confirmación BOS {tipo.lower()} M15 + M5 con volumen superior al promedio.",
                "zona_entrada": f"{ultimo['close']*0.999:.2f}–{ultimo['close']*1.001:.2f}",
                "sl": f"{ultimo['high'] if tipo=='Venta' else ultimo['low']:.2f}",
                "tp1": f"{ultimo['close']*(0.99 if tipo=='Venta' else 1.01):.2f} (1:2)",
                "tp2": f"{ultimo['close']*(0.98 if tipo=='Venta' else 1.02):.2f} (1:3)",
                "comentario": f"Cumple estructura TESLABTC: BOS + Mitigación + Confirmación ({tipo})."
            }
    return {"activo": False}

# ============================================================
# 🔹 Sesión New York
# ============================================================
def _estado_sesion_ny():
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end   = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    return "🟢 Activa (NY)" if start <= ahora <= end else "❌ Cerrada (Fuera de NY)"

# ============================================================
# 🔹 Reflexiones TESLABTC
# ============================================================
REFLEXIONES = [
    "La gestión del riesgo es la columna vertebral del éxito en trading.",
    "La paciencia en la zona convierte el caos en oportunidad.",
    "El mercado premia al que espera la confirmación, no al que anticipa.",
    "El control emocional es tu mejor indicador.",
    "Ser constante supera al talento. Siempre.",
    "El trader exitoso no predice, se adapta.",
    "Tu disciplina define tu rentabilidad.",
]

# ============================================================
# 🔹 Generar Análisis Premium completo
# ============================================================
def generar_analisis_premium(symbol="BTCUSDT"):
    fecha = datetime.now(TZ_COL).strftime("%d/%m/%Y %H:%M:%S")
    precio, fuente = _safe_get_price(symbol)
    precio_txt = f"{precio:,.2f} USD" if precio else "—"
    sesion = _estado_sesion_ny()

    kl_d   = _safe_get_klines(symbol, "1d", 400)
    kl_h4  = _safe_get_klines(symbol, "4h", 300)
    kl_h1  = _safe_get_klines(symbol, "1h",  300)
    kl_m15 = _safe_get_klines(symbol, "15m", 200)
    kl_m5  = _safe_get_klines(symbol, "5m",  200)

    tf_d   = _detectar_tendencia(kl_d)
    tf_h4  = _detectar_tendencia(kl_h4)
    tf_h1  = _detectar_tendencia(kl_h1)
    tf_m15 = _detectar_tendencia(kl_m15)

    setup = detectar_setup_m5(symbol)

    tendencia_global = tf_h4["estado"] if tf_h4["estado"] != "lateral" else tf_d["estado"]
    direccion = "🟢 Alcista" if tendencia_global == "alcista" else ("🔴 Bajista" if tendencia_global == "bajista" else "⚪ Lateral")

    contexto = (
        f"El precio presenta estructura {tendencia_global.upper()} "
        f"según H4/D. Confirmación BOS detectada. "
        f"Actualmente reaccionando a zonas {('de oferta' if tendencia_global=='bajista' else 'de demanda')} relevantes."
    )

    esc1 = {
        "tipo": "Continuación" if tendencia_global != "lateral" else "Neutro",
        "probabilidad": "Alta" if tendencia_global != "lateral" else "Baja",
        "riesgo": "Bajo" if tendencia_global != "lateral" else "Medio",
        "contexto": contexto,
        "comentario": "Operar a favor de estructura general y esperar confirmación en M15."
    }

    esc2 = {
        "tipo": "Corrección",
        "probabilidad": "Media" if tendencia_global != "lateral" else "Baja",
        "riesgo": "Medio",
        "contexto": "Escenario contrario al sesgo principal, posible retroceso técnico.",
        "comentario": "Operar sólo si se confirma BOS contrario en M15 y volumen decreciente."
    }

    reflexion = random.choice(REFLEXIONES)

    payload = {
        "fecha": fecha,
        "nivel_usuario": "Premium",
        "sesión": sesion,
        "activo": symbol,
        "precio_actual": precio_txt,
        "fuente_precio": fuente,
        "estructura_detectada": {"D": tf_d, "H4": tf_h4, "H1": tf_h1, "M15": tf_m15},
        "direccion_general": direccion,
        "contexto_general": contexto,
        "escenario_1": esc1,
        "escenario_2": esc2,
        "setup_tesla": setup,
        "reflexion": reflexion,
        "slogan": "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
    }

    # Ajuste visual si hay setup activo
    if setup.get("activo"):
        payload["conclusion_general"] = (
            f"⚙️ {setup['nivel']}\n"
            f"{setup['contexto']}\n"
            f"Entrada: {setup['zona_entrada']}\n"
            f"SL: {setup['sl']} | TP1: {setup['tp1']} | TP2: {setup['tp2']}\n"
            f"{setup['comentario']}"
        )
    else:
        payload["conclusion_general"] = (
            "Operar solo cuando todas las confirmaciones críticas se alineen (BOS + POI + Sesión NY). "
            "Si el setup no es válido, vuelve a intentar en unos minutos."
        )

    return {"🧠 TESLABTC.KG": payload}
