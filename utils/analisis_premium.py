from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3.1 PRO REAL MARKET)
# ============================================================
# Fuente: Binance (REST) — Multi-TF (H4, H1, M5)
# - Estructura H4/H1 para SWING
# - Confirmaciones y setups SCALPING en M5
# - SCALPING solo en ventana de sesión NY (primeras 2h)
# - SWING 24/7 (se actualiza cada vela de H1)
# - Totalmente compatible con utils/intelligent_formatter v5.8 PRO
# ============================================================

import requests
import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import pytz

from utils.estructura_utils import detectar_bos

# ------------------------------
# 🌎 Config base
# ------------------------------
TZ_COL = timezone(timedelta(hours=-5))
BINANCE_REST_BASE = "https://api.binance.com"
UA = {"User-Agent": "teslabtc-kg/5.3.1"}

# ------------------------------------------------------------
# 🔹 Utilidades base (precio + klines)
# ------------------------------------------------------------
def _safe_get_price(symbol: str = "BTCUSDT") -> Tuple[Optional[float], str]:
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/ticker/price",
            params={"symbol": symbol},
            headers=UA,
            timeout=6,
        )
        r.raise_for_status()
        data = r.json()
        return float(data["price"]), "Binance (REST)"
    except Exception as e:
        return None, f"Error precio: {e}"


def _safe_get_klines(symbol: str, interval: str = "15m", limit: int = 500) -> List[Dict[str, Any]]:
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=UA,
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return [
            {
                "open_time": datetime.utcfromtimestamp(k[0] / 1000.0),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "vol": float(k[5]),
            }
            for k in data
        ]
    except Exception:
        return []


# ------------------------------------------------------------
# 🔹 Pivotes y tendencia (HH/HL vs LH/LL coherente)
# ------------------------------------------------------------
def _pivotes(kl: List[Dict[str, Any]], look: int = 2) -> Tuple[List[int], List[int]]:
    if not kl or len(kl) < (look * 2 + 1):
        return [], []
    hi_idx: List[int] = []
    lo_idx: List[int] = []
    for i in range(look, len(kl) - look):
        h = kl[i]["high"]
        l = kl[i]["low"]
        if all(h > kl[i - j]["high"] for j in range(1, look + 1)) and all(
            h > kl[i + j]["high"] for j in range(1, look + 1)
        ):
            hi_idx.append(i)
        if all(l < kl[i - j]["low"] for j in range(1, look + 1)) and all(
            l < kl[i + j]["low"] for j in range(1, look + 1)
        ):
            lo_idx.append(i)
    return hi_idx, lo_idx


def _detectar_tendencia(kl: List[Dict[str, Any]], look: int = 12) -> Dict[str, Any]:
    """
    (Versión clásica TESLABTC, se deja por compatibilidad si la necesitas).
    """
    if not kl or len(kl) < (look * 2 + 3):
        return {"estado": "lateral", "BOS": "—"}

    hi_idx, lo_idx = _pivotes(kl, look=look)

    if len(hi_idx) < 2 or len(lo_idx) < 2:
        try:
            last_hi = kl[hi_idx[-1]]["high"] if hi_idx else None
            prev_hi = kl[hi_idx[-2]]["high"] if len(hi_idx) > 1 else None
            last_lo = kl[lo_idx[-1]]["low"] if lo_idx else None
            prev_lo = kl[lo_idx[-2]]["low"] if len(lo_idx) > 1 else None
        except Exception:
            last_hi = prev_hi = last_lo = prev_lo = None
        return {
            "estado": "lateral",
            "BOS": "—",
            "HH": last_hi,
            "LH": prev_hi,
            "LL": last_lo,
            "HL": prev_lo,
            "pair": "HH/LL",
        }

    hh = kl[hi_idx[-1]]["high"]
    lh = kl[hi_idx[-2]]["high"]
    ll = kl[lo_idx[-1]]["low"]
    hl = kl[lo_idx[-2]]["low"]

    if hh > lh and ll > hl:
        return {
            "estado": "alcista",
            "BOS": "✔️",
            "HH": hh,
            "LH": lh,
            "LL": ll,
            "HL": hl,
            "pair": "HH/HL",
        }
    if hh < lh and ll < hl:
        return {
            "estado": "bajista",
            "BOS": "✔️",
            "HH": hh,
            "LH": lh,
            "LL": ll,
            "HL": hl,
            "pair": "LH/LL",
        }

    return {
        "estado": "lateral",
        "BOS": "—",
        "HH": hh,
        "LH": lh,
        "LL": ll,
        "HL": hl,
        "pair": "HH/LL",
    }


# ------------------------------------------------------------
# 🔹 Rangos reales por horario Colombia (PDH/PDL & Asia)
# (Se dejan helpers por compatibilidad, aunque en esta lógica
#  nueva no mostramos esas zonas en el mensaje principal)
# ------------------------------------------------------------
def _pdh_pdl(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """Día previo cerrado COL: 7PM anteayer → 7PM ayer (America/Bogota)."""
    if not kl_15m:
        return None
    tz_col = pytz.timezone("America/Bogota")
    ahora = datetime.now(tz_col)
    fin_dia = (
        ahora.replace(hour=19, minute=0, second=0, microsecond=0)
        if ahora.hour >= 19
        else (ahora - timedelta(days=1)).replace(
            hour=19, minute=0, second=0, microsecond=0
        )
    )
    inicio_dia = fin_dia - timedelta(hours=24)
    hi: Optional[float] = None
    lo: Optional[float] = None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(tz_col)
        if inicio_dia <= t_col < fin_dia:
            h = float(k["high"])
            l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)
    if hi is None or lo is None:
        return None
    return {"PDH": round(hi, 2), "PDL": round(lo, 2)}


def _asian_range(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """Última sesión asiática CERRADA COL: 5PM → 2AM usando 15m."""
    if not kl_15m:
        return None

    from utils.time_utils import last_closed_asian_window_col, TZ_COL as TZ_COL_UTIL

    start, end = last_closed_asian_window_col()

    hi: Optional[float] = None
    lo: Optional[float] = None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(TZ_COL_UTIL)
        if start <= t_col < end:
            h = float(k["high"])
            l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)

    if hi is None or lo is None:
        return None
    return {"ASIAN_HIGH": round(hi, 2), "ASIAN_LOW": round(lo, 2)}


# ------------------------------------------------------------
# 🔹 Confirmaciones (con contexto) — helpers legacy
# ------------------------------------------------------------
def _confirmaciones(
    precio: float,
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    tf_d: Dict[str, Any],
    tf_h1: Dict[str, Any],
    sesion_activa: bool,
) -> Dict[str, str]:
    confs: Dict[str, str] = {}

    # Macro (D)
    if tf_d.get("estado") == "alcista":
        confs["Macro (D)"] = "✅ Alcista — HH/HL confirmados."
    elif tf_d.get("estado") == "bajista":
        confs["Macro (D)"] = "✅ Bajista — LH/LL confirmados."
    else:
        confs["Macro (D)"] = "➖ Lateral — esperar definición."

    # Intradía (H1)
    if tf_h1.get("estado") == "alcista":
        confs["Intradía (H1)"] = "✅ Alcista — buscar demanda válida."
    elif tf_h1.get("estado") == "bajista":
        confs["Intradía (H1)"] = "✅ Bajista — respetando oferta."
    else:
        confs["Intradía (H1)"] = "➖ Rango — se requiere BOS/CHoCH."

    # Sesión NY
    confs["Sesión NY"] = "✅ Activa" if sesion_activa else "❌ Cerrada"

    # PDH/PDL (barridas)
    if isinstance(precio, (int, float)) and pd:
        pdh, pdl = pd.get("PDH"), pd.get("PDL")
        if pdh and precio > float(pdh):
            confs["Barrida PDH"] = "⚠️ Superior tomada — posible reacción bajista."
        elif pdl and precio < float(pdl):
            confs["Barrida PDL"] = "⚠️ Inferior tomada — posible reacción alcista."
        else:
            confs["Barridas Diarias"] = "➖ Sin barridas PDH/PDL."

    # Asia
    if asian:
        if precio > float(asian.get("ASIAN_HIGH", 0)):
            confs["Barrida Asia (HIGH)"] = (
                "⚠️ Alto asiático eliminado — vigilar rechazo."
            )
        elif precio < float(asian.get("ASIAN_LOW", 0)):
            confs["Barrida Asia (LOW)"] = "⚠️ Bajo asiático eliminado — vigilar rebote."
        else:
            confs["Rango Asia"] = "➖ Dentro del rango asiático."

    # OB válido (interpretativo simple por estado H1)
    confs["OB válido H1/H15"] = (
        "✅ En zona relevante — posible confirmación."
        if tf_h1.get("estado") in ("alcista", "bajista")
        else "➖ No confirmado."
    )

    return confs


def _probabilidad_por_confs(confs: Dict[str, str]) -> str:
    checks = sum(1 for v in confs.values() if v.startswith("✅"))
    if checks >= 4:
        return "Alta"
    if checks >= 2:
        return "Media"
    return "Baja"


def _riesgo(prob: str) -> str:
    return "Bajo" if prob == "Alta" else ("Medio" if prob == "Media" else "Alto")


def _separar_confs(confs: Dict[str, str]) -> Tuple[List[str], List[str]]:
    """
    Separa nombres de confirmaciones:
    - a_favor: las que empiezan por '✅'
    - pendientes: el resto
    """
    a_favor: List[str] = []
    pendientes: List[str] = []
    for nombre, texto in confs.items():
        if texto.startswith("✅"):
            a_favor.append(nombre)
        else:
            pendientes.append(nombre)
    return a_favor, pendientes


# ------------------------------------------------------------
# 🔹 Sesión NY + Reflexiones base
# ------------------------------------------------------------
def _estado_sesion_ny() -> Tuple[str, bool]:
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    activa = start <= ahora <= end
    return (
        "✅ Activa (Sesión NY)" if activa else "❌ Cerrada (Fuera de NY)",
        activa,
    )


REFLEXIONES = [
    "La gestión del riesgo es la columna vertebral del éxito en trading.",
    "La paciencia en la zona convierte el caos en oportunidad.",
    "El mercado premia al que espera la confirmación, no al que anticipa.",
    "El control emocional es tu mejor indicador.",
    "Ser constante supera al talento. Siempre.",
    "El trader exitoso no predice, se adapta.",
    "Tu disciplina define tu rentabilidad.",
]


def _ventana_scalping_ny() -> bool:
    """Ventana operativa para SCALPING en NY: solo primeras 2 horas."""
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end = start + timedelta(hours=2)
    return start <= ahora <= end


# ------------------------------------------------------------
# 🔹 ZigZag estructural (legacy, para contexto si lo requieres)
# ------------------------------------------------------------
def _zigzag_pivots(
    kl: List[Dict[str, Any]],
    depth: int = 12,
    deviation: float = 5.0,
    backstep: int = 2,
) -> List[Tuple[int, str, float]]:
    """
    Replica ZigZag++ básico:
    - depth: pivote confirmado con depth velas a cada lado
    - deviation: % mínimo de cambio desde el último pivote
    - backstep: si aparece pivote del mismo tipo muy cerca, reemplaza por el más extremo
    Devuelve lista de pivotes [(idx, 'H'/'L', price), ...] ordenados por tiempo.
    """
    if not kl or len(kl) < (depth * 2 + 5):
        return []

    hi_idx, lo_idx = _pivotes(kl, look=depth)

    cands: List[Tuple[int, str, float]] = []
    for i in hi_idx:
        cands.append((i, "H", float(kl[i]["high"])))
    for i in lo_idx:
        cands.append((i, "L", float(kl[i]["low"])))

    cands.sort(key=lambda x: x[0])

    pivots: List[Tuple[int, str, float]] = []
    for i, t, p in cands:
        if not pivots:
            pivots.append((i, t, p))
            continue

        li, lt, lp = pivots[-1]

        # mismo tipo de pivote
        if t == lt:
            if (i - li) <= backstep:
                if (t == "H" and p > lp) or (t == "L" and p < lp):
                    pivots[-1] = (i, t, p)
            else:
                if (t == "H" and p > lp) or (t == "L" and p < lp):
                    pivots[-1] = (i, t, p)
            continue

        # pivote opuesto → validar deviation mínima
        if lp != 0:
            move_pct = abs((p - lp) / lp) * 100.0
        else:
            move_pct = 999.0

        if move_pct >= deviation:
            pivots.append((i, t, p))

    return pivots


def _detectar_tendencia_zigzag(
    kl: List[Dict[str, Any]],
    depth: int = 12,
    deviation: float = 5.0,
    backstep: int = 2,
) -> Dict[str, Any]:
    """
    Tendencia estructural TESLABTC usando ZigZag:
    - Usa los últimos 2 HIGH y 2 LOW del zigzag.
    - Si el último HIGH > HIGH previo y el último LOW > LOW previo → ALCISTA.
    - Si el último HIGH < HIGH previo y el último LOW < LOW previo → BAJISTA.
    - Si no, LATERAL / transición.
    """
    piv = _zigzag_pivots(kl, depth=depth, deviation=deviation, backstep=backstep)
    if not kl or len(piv) < 3:
        return {"estado": "lateral", "BOS": "—"}

    highs = [(i, p) for (i, t, p) in piv if t == "H"]
    lows = [(i, p) for (i, t, p) in piv if t == "L"]

    if len(highs) < 2 or len(lows) < 2:
        idx_prev, tipo_prev, price_prev = piv[-2]
        idx_last, tipo_last, price_last = piv[-1]

        if tipo_prev == "L" and tipo_last == "H":
            estado = "alcista"
        elif tipo_prev == "H" and tipo_last == "L":
            estado = "bajista"
        else:
            estado = "lateral"

        return {
            "estado": estado,
            "BOS": "—",
            "ultimo_pivote": price_last,
            "pivotes": [
                (idx_prev, tipo_prev, price_prev),
                (idx_last, tipo_last, price_last),
            ],
        }

    idx_h1, h1 = highs[-2]
    idx_h2, h2 = highs[-1]
    idx_l1, l1 = lows[-2]
    idx_l2, l2 = lows[-1]

    if h2 > h1 and l2 > l1:
        estado = "alcista"
        pair = "HH/HL"
        bos = "✔️"
    elif h2 < h1 and l2 < l1:
        estado = "bajista"
        pair = "LH/LL"
        bos = "✔️"
    else:
        estado = "lateral"
        pair = "HH/LL"
        bos = "—"

    idx_last, tipo_last, price_last = piv[-1]

    return {
        "estado": estado,
        "BOS": bos,
        "HH": h2,
        "LH": h1,
        "LL": l2,
        "HL": l1,
        "pair": pair,
        "ultimo_pivote": price_last,
        "pivotes": piv[-6:],
    }


# ============================================================
# 🔹 Helper para TPs en 1:1 y 1:2
# ============================================================
def _calcular_tp(precio_entrada: float, sl: float, rr: float = 1.0) -> float:
    """
    Calcula el TP como múltiplo de riesgo (RR) usando distancia |entrada - SL|.
    Funciona tanto para largos como para cortos.
    """
    distancia = abs(precio_entrada - sl)
    if precio_entrada > sl:
        # LARGO
        return round(precio_entrada + distancia * rr, 2)
    else:
        # CORTO
        return round(precio_entrada - distancia * rr, 2)


# ============================================================
# 🌟 TESLABTC — ANÁLISIS PREMIUM REAL (v5.3)
# ============================================================
def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """
    Versión simplificada TESLABTC:
    - Usa estructura H4/H1 para SWING
    - Usa M5 para señales SCALPING en NY (primeras 2h)
    - No muestra zonas de liquidez; sólo acción del precio
    """
    now = datetime.now(TZ_COL)
    fecha_txt = now.strftime("%d/%m/%Y %H:%M:%S")

    # Precio actual
    precio, fuente = _safe_get_price(symbol)
    precio_num = float(precio) if isinstance(precio, (int, float)) else None
    precio_txt = f"{precio_num:,.2f} USD" if precio_num is not None else "—"

    # Datos por temporalidad
    kl_h4 = _safe_get_klines(symbol, "4h", 400)
    kl_h1 = _safe_get_klines(symbol, "1h", 400)
    kl_m5 = _safe_get_klines(symbol, "5m", 300)

    # Estructura con ZigZag pero sólo para dirección general
    tf_h4 = _detectar_tendencia_zigzag(kl_h4, depth=12, deviation=5.0, backstep=2)
    tf_h1 = _detectar_tendencia_zigzag(kl_h1, depth=10, deviation=4.0, backstep=2)
    dir_h4 = tf_h4.get("estado", "lateral")
    dir_h1 = tf_h1.get("estado", "lateral")

    # Rango H4 aproximado (para TP3 swing)
    if kl_h4:
        h4_high = max(k["high"] for k in kl_h4[-60:])
        h4_low = min(k["low"] for k in kl_h4[-60:])
    else:
        h4_high = None
        h4_low = None

    # POI H4 61.8–88.6 para swing (zona premium)
    def _poi_fibo_band(estado: Optional[str], hi: Optional[float], lo: Optional[float]):
        if hi is None or lo is None or hi == lo:
            return None
        hi = float(hi); lo = float(lo)
        if estado == "alcista":
            base, tope = lo, hi
        elif estado == "bajista":
            base, tope = hi, lo
        else:
            return None
        amp = tope - base
        if amp <= 0:
            return None
        lvl_618 = base + 0.618 * amp
        lvl_886 = base + 0.886 * amp
        banda_low = min(lvl_618, lvl_886)
        banda_high = max(lvl_618, lvl_886)
        return round(banda_low, 2), round(banda_high, 2)

    poi_h4 = _poi_fibo_band(dir_h4, h4_high, h4_low)
    poi_txt = "—"
    in_premium = False
    if poi_h4:
        p_lo, p_hi = sorted([float(poi_h4[0]), float(poi_h4[1])])
        poi_txt = f"{p_lo:,.2f}–{p_hi:,.2f} USD"
        if precio_num is not None and p_lo <= precio_num <= p_hi:
            in_premium = True

    # Sesión NY
    sesion_txt, ny_activa = _estado_sesion_ny()
    ventana_scalping = _ventana_scalping_ny()

    # ============================
    # 📊 SCALPING (M5)
    # ============================
# ============================
# 📊 SCALPING (M5)
# ============================
scalping_cont = {
    "activo": False,
    "direccion": "—",
    "riesgo": "N/A",
    "zona_reaccion": "—",
    "sl": "—",
    "tp1_rr": "1:1 (50% + BE)",
    "tp2_rr": "1:2 (50%)",
    "contexto": "Sin dirección clara en H1 o sin datos suficientes."
}
scalping_corr = scalping_cont.copy()

# 🔑 Para probar bien, NO usamos aún ventana_scalping aquí
# Para que el SCALPING funcione mientras la sesión NY esté activa
# (sin limitarlo solo a las 2 primeras horas mientras probamos)
if kl_m5 and ny_activa and dir_h1 in ("alcista", "bajista"):
    highs_m5 = [k["high"] for k in kl_m5[-30:]]
    lows_m5 = [k["low"] for k in kl_m5[-30:]]
    if len(highs_m5) >= 2 and len(lows_m5) >= 2:
        prev_high = max(highs_m5[:-1])
        prev_low = min(lows_m5[:-1])

        if dir_h1 == "alcista":
            # A FAVOR (LONG)
            entrada_fav = prev_high
            sl_fav = prev_low
            tp1_fav = _calcular_tp(entrada_fav, sl_fav, 1.0)
            tp2_fav = _calcular_tp(entrada_fav, sl_fav, 2.0)

            scalping_cont = {
                "activo": True,
                "direccion": "ALCISTA (a favor de H1)",
                "riesgo": "Bajo",
                "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                "tp1_rr": f"{tp1_fav:,.2f} (1:1 • 50% + BE)",
                "tp2_rr": f"{tp2_fav:,.2f} (1:2 • 50%)",
                "contexto": "Entrada SCALPING a favor de la estructura intradía H1."
            }

            # CONTRA (SHORT)
            entrada_contra = prev_low
            sl_contra = prev_high
            tp1_contra = _calcular_tp(entrada_contra, sl_contra, 1.0)
            tp2_contra = _calcular_tp(entrada_contra, sl_contra, 2.0)

            scalping_corr = {
                "activo": True,
                "direccion": "BAJISTA (contra H1)",
                "riesgo": "Alto",
                "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                "tp1_rr": f"{tp1_contra:,.2f} (1:1 • 50% + BE)",
                "tp2_rr": f"{tp2_contra:,.2f} (1:2 • 50%)",
                "contexto": "Entrada SCALPING de corrección intradía contra H1."
            }

        else:  # dir_h1 == "bajista"
            # A FAVOR (SHORT)
            entrada_fav = prev_low
            sl_fav = prev_high
            tp1_fav = _calcular_tp(entrada_fav, sl_fav, 1.0)
            tp2_fav = _calcular_tp(entrada_fav, sl_fav, 2.0)

            scalping_cont = {
                "activo": True,
                "direccion": "BAJISTA (a favor de H1)",
                "riesgo": "Bajo",
                "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                "tp1_rr": f"{tp1_fav:,.2f} (1:1 • 50% + BE)",
                "tp2_rr": f"{tp2_fav:,.2f} (1:2 • 50%)",
                "contexto": "Entrada SCALPING a favor de la estructura intradía H1."
            }

            # CONTRA (LONG)
            entrada_contra = prev_high
            sl_contra = prev_low
            tp1_contra = _calcular_tp(entrada_contra, sl_contra, 1.0)
            tp2_contra = _calcular_tp(entrada_contra, sl_contra, 2.0)

            scalping_corr = {
                "activo": True,
                "direccion": "ALCISTA (contra H1)",
                "riesgo": "Alto",
                "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                "tp1_rr": f"{tp1_contra:,.2f} (1:1 • 50% + BE)",
                "tp2_rr": f"{tp2_contra:,.2f} (1:2 • 50%)",
                "contexto": "Entrada SCALPING de corrección intradía contra H1."
            }

    scalping_corr = scalping_cont.copy()

    if kl_m5 and ny_activa and ventana_scalping and dir_h1 in ("alcista", "bajista"):
        highs_m5 = [k["high"] for k in kl_m5[-30:]]
        lows_m5 = [k["low"] for k in kl_m5[-30:]]
        if len(highs_m5) >= 2 and len(lows_m5) >= 2:
            prev_high = max(highs_m5[:-1])
            prev_low = min(lows_m5[:-1])

            # Continuación: en dirección de H1
            if dir_h1 == "alcista":
                # A FAVOR (LONG)
                entrada_fav = prev_high
                sl_fav = prev_low
                tp1_fav = _calcular_tp(entrada_fav, sl_fav, 1.0)
                tp2_fav = _calcular_tp(entrada_fav, sl_fav, 2.0)

                scalping_cont = {
                    "activo": True,
                    "direccion": "ALCISTA (a favor de H1)",
                    "riesgo": "Bajo",
                    "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                    "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                    "tp1_rr": f"{tp1_fav:,.2f} (1:1 • 50% + BE)",
                    "tp2_rr": f"{tp2_fav:,.2f} (1:2 • 50%)",
                    "contexto": "Entrada SCALPING a favor de la estructura intradía H1."
                }

                # CONTRA (SHORT)
                entrada_contra = prev_low
                sl_contra = prev_high
                tp1_contra = _calcular_tp(entrada_contra, sl_contra, 1.0)
                tp2_contra = _calcular_tp(entrada_contra, sl_contra, 2.0)

                scalping_corr = {
                    "activo": True,
                    "direccion": "BAJISTA (contra H1)",
                    "riesgo": "Alto",
                    "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                    "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                    "tp1_rr": f"{tp1_contra:,.2f} (1:1 • 50% + BE)",
                    "tp2_rr": f"{tp2_contra:,.2f} (1:2 • 50%)",
                    "contexto": "Entrada SCALPING de corrección intradía contra H1."
                }

            else:  # dir_h1 == "bajista"
                # A FAVOR (SHORT)
                entrada_fav = prev_low
                sl_fav = prev_high
                tp1_fav = _calcular_tp(entrada_fav, sl_fav, 1.0)
                tp2_fav = _calcular_tp(entrada_fav, sl_fav, 2.0)

                scalping_cont = {
                    "activo": True,
                    "direccion": "BAJISTA (a favor de H1)",
                    "riesgo": "Bajo",
                    "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                    "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                    "tp1_rr": f"{tp1_fav:,.2f} (1:1 • 50% + BE)",
                    "tp2_rr": f"{tp2_fav:,.2f} (1:2 • 50%)",
                    "contexto": "Entrada SCALPING a favor de la estructura intradía H1."
                }

                # CONTRA (LONG)
                entrada_contra = prev_high
                sl_contra = prev_low
                tp1_contra = _calcular_tp(entrada_contra, sl_contra, 1.0)
                tp2_contra = _calcular_tp(entrada_contra, sl_contra, 2.0)

                scalping_corr = {
                    "activo": True,
                    "direccion": "ALCISTA (contra H1)",
                    "riesgo": "Alto",
                    "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                    "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                    "tp1_rr": f"{tp1_contra:,.2f} (1:1 • 50% + BE)",
                    "tp2_rr": f"{tp2_contra:,.2f} (1:2 • 50%)",
                    "contexto": "Entrada SCALPING de corrección intradía contra H1."
                }

    # ============================
    # 🕰️ SWING (H4 + H1)
    # ============================
    swing = {
        "activo": False,
        "direccion": "—",
        "riesgo": "N/A",
        "premium_zone": poi_txt,
        "zona_reaccion": "—",
        "sl": "—",
        "tp1_rr": "1:1 (BE)",
        "tp2_rr": "1:2 (50%)",
        "tp3_objetivo": "—",
        "contexto": "Esperando alineación H4/H1 y BOS H1 en zona premium."
    }

    if (
        kl_h1
        and dir_h4 in ("alcista", "bajista")
        and dir_h1 == dir_h4
        and precio_num is not None
        and in_premium
    ):
        # BOS H1 en dirección de H4
        bos_h1 = detectar_bos(kl_h1)
        bos_ok = bos_h1.get("bos") and (
            (bos_h1.get("tipo") == "alcista" and dir_h4 == "alcista") or
            (bos_h1.get("tipo") == "bajista" and dir_h4 == "bajista")
        )

        if bos_ok:
            highs_h1 = [k["high"] for k in kl_h1[-40:]]
            lows_h1 = [k["low"] for k in kl_h1[-40:]]
            if len(highs_h1) >= 2 and len(lows_h1) >= 2:
                prev_high_h1 = max(highs_h1[:-1])
                prev_low_h1 = min(lows_h1[:-1])

                if dir_h4 == "alcista":
                    entrada = prev_high_h1
                    sl_val = prev_low_h1
                    zona_reac = (
                        f"Quebrar y cerrar sobre el HIGH H1 ≈ {prev_high_h1:,.2f} USD "
                        f"(en zona premium H4)."
                    )
                    sl_txt = f"LOW H1 previo ≈ {prev_low_h1:,.2f} USD"
                    tp3_txt = f"HIGH H4 ≈ {h4_high:,.2f} USD" if h4_high is not None else "HIGH H4"
                    direccion_txt = "ALCISTA (H1 a favor de H4)"
                else:
                    entrada = prev_low_h1
                    sl_val = prev_high_h1
                    zona_reac = (
                        f"Quebrar y cerrar bajo el LOW H1 ≈ {prev_low_h1:,.2f} USD "
                        f"(en zona premium H4)."
                    )
                    sl_txt = f"HIGH H1 previo ≈ {prev_high_h1:,.2f} USD"
                    tp3_txt = f"LOW H4 ≈ {h4_low:,.2f} USD" if h4_low is not None else "LOW H4"
                    direccion_txt = "BAJISTA (H1 a favor de H4)"

                tp1_swing = _calcular_tp(entrada, sl_val, 1.0)
                tp2_swing = _calcular_tp(entrada, sl_val, 2.0)

                swing = {
                    "activo": True,
                    "direccion": direccion_txt,
                    "riesgo": "Medio",
                    "premium_zone": poi_txt,
                    "zona_reaccion": zona_reac,
                    "sl": sl_txt,
                    "tp1_rr": f"{tp1_swing:,.2f} (1:1 • BE)",
                    "tp2_rr": f"{tp2_swing:,.2f} (1:2 • 50%)",
                    "tp3_objetivo": tp3_txt,
                    "contexto": "Operación SWING siguiendo estructura H4, con BOS H1 confirmado en zona premium."
                }

    # Reflexión
    reflexion = random.choice(REFLEXIONES)

    # Estructura / zonas mínimas (para compatibilidad con formatter)
    estructura_detectada = {
        "H4": dir_h4,
        "H1": dir_h1,
        "sesion_ny_activa": ny_activa,
        "ventana_scalping_ny": ventana_scalping,
    }
    zonas_detectadas = {
        "H4_HIGH": h4_high,
        "H4_LOW": h4_low,
        "POI_H4": poi_txt,
    }

    payload = {
        "version": VERSION_TESLA,
        "fecha": fecha_txt,
        "activo": symbol,
        "precio_actual": precio_txt,
        "sesión": sesion_txt,
        "fuente_precio": fuente,
        "estructura_detectada": estructura_detectada,
        "zonas_detectadas": zonas_detectadas,
        "scalping": {
            "continuacion": scalping_cont,
            "correccion": scalping_corr,
        },
        "swing": swing,
        "reflexion": reflexion,
        "slogan": "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
    }

    return payload


# ============================================================
# 🔹 Interpretación contextual inteligente TESLABTC (legacy)
# ============================================================
def interpretar_contexto(
    tf_d: Dict[str, Any],
    tf_h4: Dict[str, Any],
    tf_h1: Dict[str, Any],
    confs: Dict[str, str],
    zonas: Dict[str, Any],
) -> str:
    d = tf_d.get("estado", "—")
    h4 = tf_h4.get("estado", "—")
    h1 = tf_h1.get("estado", "—")
    bos_d = tf_d.get("BOS", "—")
    bos_h4 = tf_h4.get("BOS", "—")
    bos_h1 = tf_h1.get("BOS", "—")

    interpretacion: List[str] = []

    # Coherencia entre temporalidades
    if d == "bajista" and h4 == "bajista":
        interpretacion.append("Estructura macro bajista en D y H4.")
        if h1 == "alcista":
            interpretacion.append("H1 en retroceso hacia oferta H4.")
        elif h1 == "bajista":
            interpretacion.append("H1 confirma continuación bajista.")
        else:
            interpretacion.append("H1 lateral dentro del impulso bajista.")
    elif d == "alcista" and h4 == "alcista":
        interpretacion.append("Estructura macro alcista en D y H4.")
        if h1 == "bajista":
            interpretacion.append("H1 en corrección hacia demanda H4.")
        elif h1 == "alcista":
            interpretacion.append("H1 continúa la estructura ascendente.")
        else:
            interpretacion.append("H1 en pausa estructural.")
    else:
        interpretacion.append("Divergencia entre D y H4: fase de rango/transición.")
        if h1 == "alcista":
            interpretacion.append("H1 busca máximos dentro del rango.")
        elif h1 == "bajista":
            interpretacion.append("H1 busca barrer mínimos dentro del rango.")

    # BOS
    if bos_h4 == "✔️" and bos_h1 == "✔️":
        interpretacion.append("BOS validado en H4 y H1.")
    elif bos_h1 == "✔️" and bos_h4 != "✔️":
        interpretacion.append("BOS temprano en H1 (posible cambio por confirmar en H4).")
    elif bos_d == "✔️":
        interpretacion.append("BOS Diario señala cambio de ciclo relevante.")

    # Liquidez (helpers de confirmaciones)
    if confs.get("Barrida PDH") or confs.get("Barrida Asia (HIGH)"):
        interpretacion.append("Liquidez superior tomada: riesgo de distribución.")
    if confs.get("Barrida PDL") or confs.get("Barrida Asia (LOW)"):
        interpretacion.append("Liquidez inferior tomada: posible reacumulación.")
    if confs.get("Sesión NY", "").startswith("✅"):
        interpretacion.append("Sesión NY activa: volatilidad elevada.")

    # Rango D real (último impulso ZigZag)
    if isinstance(zonas, dict) and "D_HIGH" in zonas and "D_LOW" in zonas:
        interpretacion.append(
            f"Rango D (último impulso): {zonas['D_LOW']:,} → {zonas['D_HIGH']:,}."
        )

    return " ".join(interpretacion)
