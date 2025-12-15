from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3 PRO REAL MARKET)
# ============================================================
# Fuente: Binance (REST) — sin simulaciones
# Estructura real multi-TF, PDH/PDL, Rango Asiático (COL),
# OB/POI cercanos, escenarios de continuidad/corrección
# y SETUP ACTIVO “Level Entry M5”.
# Compatible con utils/intelligent_formatter v5.5 PRO.
# ============================================================

import requests
import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import pytz

# ------------------------------
# 🌎 Config base
# ------------------------------
TZ_COL = timezone(timedelta(hours=-5))
BINANCE_REST_BASE = "https://api.binance.com"
UA = {"User-Agent": "teslabtc-kg/5.2"}


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


def _safe_get_klines(
    symbol: str,
    interval: str = "15m",
    limit: int = 500,
) -> List[Dict[str, Any]]:
    try:
        r = requests.get(
            f"{BINANCE_REST_BASE}/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            headers=UA,
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        out: List[Dict[str, Any]] = []
        for k in data:
            out.append(
                {
                    "open_time": datetime.utcfromtimestamp(k[0] / 1000.0),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "vol": float(k[5]),
                }
            )
        return out
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
    (Versión clásica TESLABTC, ya no es la principal pero se mantiene
    por compatibilidad si la necesitas en el futuro).
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
# 🔹 Confirmaciones (con contexto)
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


# ------------------------------------------------------------
# 🔹 Escenarios + Setup
# ------------------------------------------------------------
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


def _escenarios(
    precio: float,
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    tf_d: Dict[str, Any],
    tf_h4: Dict[str, Any],
    tf_h1: Dict[str, Any],
    confs: Dict[str, str],
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    t_h1 = tf_h1.get("estado")

    # Dirección de referencia para CONTINUACIÓN: H1
    if t_h1 == "alcista":
        tipo_favor, tipo_contra = "Compra", "Venta"
    elif t_h1 == "bajista":
        tipo_favor, tipo_contra = "Venta", "Compra"
    else:
        tipo_favor, tipo_contra = "Neutro", "Neutro"

    contexto: List[str] = []

    # Contexto por barridas diarias
    if isinstance(precio, (int, float)) and pd:
        if pd.get("PDL") and precio < float(pd["PDL"]):
            contexto.append("🧲 Barrida del PDL → búsqueda de PDH.")
        if pd.get("PDH") and precio > float(pd["PDH"]):
            contexto.append("🧲 Barrida del PDH → búsqueda de PDL.")

    # Contexto por rango asiático
    if isinstance(precio, (int, float)) and asian:
        if asian.get("ASIAN_LOW") and precio < float(asian["ASIAN_LOW"]):
            contexto.append("🧲 Barrida del Bajo Asiático → buscar Alto Asiático.")
        if asian.get("ASIAN_HIGH") and precio > float(asian["ASIAN_HIGH"]):
            contexto.append("🧲 Barrida del Alto Asiático → buscar Bajo Asiático.")

    # Sesgo de H1
    if t_h1 == "alcista":
        contexto.append("📈 H1 alcista (sesgo comprador).")
    elif t_h1 == "bajista":
        contexto.append("📉 H1 bajista (sesgo vendedor).")
    else:
        contexto.append("➖ H1 lateral: esperar BOS/CHoCH.")

    contexto_txt = " | ".join(contexto) if contexto else "Contexto neutro."

    # Probabilidades según confirmaciones
    prob_favor = _probabilidad_por_confs(confs)
    prob_contra = (
        "Media" if prob_favor == "Alta" else ("Baja" if prob_favor == "Media" else "Baja")
    )

    # Separar confirmaciones a favor / pendientes
    confs_favor, confs_pendientes = _separar_confs(confs)

    def build_setup(prob: str, tipo: str) -> Tuple[str, Dict[str, str]]:
        """
        Aquí sólo marcamos si hay setup candidato o no.
        El SETUP ACTIVO REAL (con precios exactos) lo da _setup_activo_m5.
        """
        tiene_setup = (
            prob in ("Alta", "Media")
            and tipo in ("Compra", "Venta")
            and t_h1 in ("alcista", "bajista")
        )
        if tiene_setup:
            return "✅ Setup candidato", {
                "zona_entrada": "Esperar BOS en M15/M5 dentro del POI.",
                "sl": "Alto/bajo anterior de la zona de entrada.",
                "tp1": "1:1 (mover a BE y tomar parcial)",
                "tp2": "1:2 (recoger ganancias principales)",
                "tp3": "1:3+ (sólo si la estructura se mantiene fuerte)",
                "observacion": "Prioridad 1:2; TP3+ sólo con fortaleza clara.",
            }
        else:
            return "⏳ Sin setup válido. Intenta en unos minutos.", {}

    setup_estado_favor, setup_favor = build_setup(prob_favor, tipo_favor)
    setup_estado_contra, setup_contra = build_setup(prob_contra, tipo_contra)

    def texto_continuacion(tipo: str) -> str:
        if tipo == "Compra":
            return (
                "Escenario de CONTINUACIÓN ALCISTA: buscar compras a favor de la "
                "tendencia intradía, idealmente desde demanda/POI profundo."
            )
        if tipo == "Venta":
            return (
                "Escenario de CONTINUACIÓN BAJISTA: buscar ventas a favor de la "
                "tendencia intradía, idealmente desde oferta/POI profundo."
            )
        return "Escenario neutro: sin dirección clara, mejor esperar."

    def texto_correccion(tipo: str) -> str:
        if tipo == "Compra":
            return (
                "Escenario de CORRECCIÓN ALCISTA (contra tendencia principal): "
                "operar retrocesos con prudencia, sabiendo que el ciclo mayor "
                "sigue bajista."
            )
        if tipo == "Venta":
            return (
                "Escenario de CORRECCIÓN BAJISTA (contra tendencia principal): "
                "operar retrocesos con prudencia dentro de un contexto alcista."
            )
        return "Escenario de corrección neutro: sin ventaja direccional clara."

    # Escenario 1: Continuidad (a favor de H1)
    escenario_1 = {
        "tipo": tipo_favor,
        "probabilidad": prob_favor,
        "riesgo": _riesgo(prob_favor) if tipo_favor in ("Compra", "Venta") else "Alto",
        "contexto": contexto_txt,
        "confirmaciones": confs,
        "confs_favor": confs_favor,
        "confs_pendientes": confs_pendientes,
        "setup_estado": setup_estado_favor,
        "setup": setup_favor,
        "texto": texto_continuacion(tipo_favor),
    }

    # Escenario 2: Corrección (contra H1) → siempre de ALTO RIESGO si hay tendencia
    riesgo_contra = "Alto" if tipo_contra in ("Compra", "Venta") else "Alto"
    escenario_2 = {
        "tipo": tipo_contra,
        "probabilidad": prob_contra,
        "riesgo": riesgo_contra,
        "contexto": contexto_txt,
        "confirmaciones": confs,
        "confs_favor": confs_favor,
        "confs_pendientes": confs_pendientes,
        "setup_estado": setup_estado_contra,
        "setup": setup_contra,
        "texto": texto_correccion(tipo_contra),
    }

    conclusion = (
        "Operar sólo cuando *todas* las confirmaciones críticas se alineen "
        "(BOS + POI + Sesión NY). Si el setup no es válido, vuelve a intentar en unos minutos."
    )

    return escenario_1, escenario_2, conclusion


# ------------------------------------------------------------
# 🔹 Sesión NY + Reflexiones base (fallback)
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


# ------------------------------------------------------------
# 🔹 SETUP ACTIVO – Level Entry M5
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


def _setup_activo_m5(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    kl_m15 = _safe_get_klines(symbol, "15m", 200)
    kl_m5 = _safe_get_klines(symbol, "5m", 200)
    if not kl_m15 or not kl_m5:
        return {"activo": False}

    tf_m15 = _detectar_tendencia_zigzag(kl_m15, depth=12, deviation=5.0, backstep=2)
    tf_m5 = _detectar_tendencia_zigzag(kl_m5, depth=12, deviation=5.0, backstep=2)

    if tf_m15["estado"] == tf_m5["estado"] and tf_m5["estado"] in ("alcista", "bajista"):
        ultimo = kl_m5[-1]
        vol_prom = sum(x["vol"] for x in kl_m5[-40:]) / max(1, len(kl_m5[-40:]))

        if ultimo["vol"] > vol_prom * 1.25:
            tipo = "Compra" if tf_m5["estado"] == "alcista" else "Venta"
            ce = ultimo["close"]
            zona_a = ce * (1 - 0.001) if tipo == "Compra" else ce * (1 + 0.001)
            zona_b = ce * (1 + 0.001) if tipo == "Compra" else ce * (1 - 0.001)

            return {
                "activo": True,
                "nivel": f"SETUP ACTIVO – M5 Level Entry ({tipo})",
                "contexto": (
                    "Confirmación BOS "
                    f"{tipo.lower()} M15 + M5 con volumen sobre promedio."
                ),
                "zona_entrada": f"{min(zona_a, zona_b):,.2f}–{max(zona_a, zona_b):,.2f}",
                "sl": f"{(ultimo['low'] if tipo == 'Compra' else ultimo['high']):,.2f}",
                "tp1": f"{(ce * 1.01 if tipo == 'Compra' else ce * 0.99):,.2f} (1:2)",
                "tp2": f"{(ce * 1.02 if tipo == 'Compra' else ce * 0.98):,.2f} (1:3)",
                "comentario": (
                    "Cumple estructura TESLABTC: BOS + Mitigación + Confirmación "
                    f"({tipo})."
                ),
            }
    return {"activo": False}


# ------------------------------------------------------------
# 🔹 Zonas para mostrar (PDH/PDL, Asia, rangos TF) + OB/POI
# ------------------------------------------------------------
def _calc_range_last_closed_candle(
    kl: List[Dict[str, Any]],
) -> Tuple[Optional[float], Optional[float]]:
    """High/Low de la última vela CERRADA del TF."""
    if not kl or len(kl) < 2:
        return None, None
    last_closed = kl[-2]
    return last_closed["high"], last_closed["low"]


def _calc_range_last_closed_daily_col(
    kl_15m: List[Dict[str, Any]],
) -> Tuple[Optional[float], Optional[float]]:
    """Rango diario real según día operativo COL (7PM–7PM) usando 15m."""
    if not kl_15m:
        return None, None

    from utils.time_utils import last_closed_daily_window_col, TZ_COL as TZ_COL_UTIL

    start, end = last_closed_daily_window_col()

    hi: Optional[float] = None
    lo: Optional[float] = None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(TZ_COL_UTIL)
        if start <= t_col < end:
            h, l = float(k["high"]), float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)
    return hi, lo


def _calc_range_last_impulse_zigzag(
    kl: List[Dict[str, Any]],
    depth: int = 12,
    deviation: float = 5.0,
    backstep: int = 2,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Devuelve el rango del ÚLTIMO IMPULSO *operativo* del ZigZag.
    """
    piv = _zigzag_pivots(kl, depth=depth, deviation=deviation, backstep=backstep)
    if not kl or len(piv) < 2:
        return None, None

    precio_actual = float(kl[-1]["close"])

    idx_seg: Optional[int] = None
    for i in range(len(piv) - 2, -1, -1):
        _, _, p1 = piv[i]
        _, _, p2 = piv[i + 1]
        lo, hi = min(p1, p2), max(p1, p2)
        if lo <= precio_actual <= hi:
            idx_seg = i
            break

    if idx_seg is None:
        _, _, p_prev = piv[-2]
        _, _, p_last = piv[-1]
    else:
        _, _, p_prev = piv[idx_seg]
        _, _, p_last = piv[idx_seg + 1]

    hi = max(p_prev, p_last)
    lo = min(p_prev, p_last)
    return hi, lo


def _fmt_zonas(
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    kl_15m: List[Dict[str, Any]],
    d_kl: List[Dict[str, Any]],
    h4_kl: List[Dict[str, Any]],
    h1_kl: List[Dict[str, Any]],
) -> Dict[str, Any]:
    zonas: Dict[str, Any] = {}

    if pd:
        zonas["PDH"] = round(float(pd.get("PDH")), 2)
        zonas["PDL"] = round(float(pd.get("PDL")), 2)
    if asian:
        zonas["ASIAN_HIGH"] = round(float(asian.get("ASIAN_HIGH")), 2)
        zonas["ASIAN_LOW"] = round(float(asian.get("ASIAN_LOW")), 2)

    d_hi, d_lo = _calc_range_last_impulse_zigzag(
        d_kl, depth=12, deviation=5.0, backstep=2
    )
    h4_hi, h4_lo = _calc_range_last_impulse_zigzag(
        h4_kl, depth=12, deviation=5.0, backstep=2
    )
    h1_hi, h1_lo = _calc_range_last_impulse_zigzag(
        h1_kl, depth=12, deviation=5.0, backstep=2
    )

    if d_hi is not None and d_lo is not None:
        zonas["D_HIGH"], zonas["D_LOW"] = round(d_hi, 2), round(d_lo, 2)
    if h4_hi is not None and h4_lo is not None:
        zonas["H4_HIGH"], zonas["H4_LOW"] = round(h4_hi, 2), round(h4_lo, 2)
    if h1_hi is not None and h1_lo is not None:
        zonas["H1_HIGH"], zonas["H1_LOW"] = round(h1_hi, 2), round(h1_lo, 2)

    return zonas or {"info": "Sin zonas detectadas"}


def _ob_en_rango(
    ob_txt: Optional[str],
    hi: Optional[float],
    lo: Optional[float],
) -> Optional[str]:
    """
    ob_txt viene como 'low–high'. Se valida contra [lo, hi].
    Si no cae dentro, se elimina.
    """
    if not ob_txt or hi is None or lo is None:
        return ob_txt

    try:
        # Normalizar guiones raros
        ob_norm = (
            ob_txt.replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
        )
        nums = [float(x.strip()) for x in ob_norm.split("-") if x.strip()]
        if len(nums) < 2:
            return ob_txt
        ob_lo, ob_hi = min(nums), max(nums)

        # Si el OB está totalmente fuera del rango swing, lo descartamos
        if ob_hi < lo or ob_lo > hi:
            return None

        # Si hay intersección con el rango swing, lo aceptamos (texto original)
        return ob_txt
    except Exception:
        return ob_txt


# ============================================================
# 🔹 FIBONACCI H1 (retroceso del último impulso operativo)
# ============================================================
def _fib_retracement_h1(
    precio: float,
    tf_h1: Dict[str, Any],
    zonas: Dict[str, Any],
) -> Tuple[Optional[float], Optional[str]]:
    """
    Calcula el nivel de retroceso Fibonacci del precio actual dentro del
    último impulso operativo H1 (ZigZag → H1_HIGH / H1_LOW).
    """
    if not isinstance(precio, (int, float)):
        return None, None

    estado = tf_h1.get("estado")
    hi = zonas.get("H1_HIGH")
    lo = zonas.get("H1_LOW")

    if hi is None or lo is None or hi == lo:
        return None, None

    hi = float(hi)
    lo = float(lo)

    if estado == "alcista":
        ratio = (precio - lo) / (hi - lo)
    elif estado == "bajista":
        ratio = (hi - precio) / (hi - lo)
    else:
        return None, None

    if ratio < 0 or ratio > 1.2:
        return None, None

    if ratio < 0.382:
        texto = "➖ Retroceso Fibonacci H1 poco profundo (< 38.2%) — descuento limitado."
    elif ratio < 0.618:
        texto = "➖ Retroceso Fibonacci H1 medio (38.2–61.8%) — aún agresivo."
    elif ratio < 0.786:
        texto = (
            "✅ Retroceso Fibonacci H1 óptimo (61.8–78.6%) — zona ideal de descuento TESLABTC."
        )
    elif ratio <= 0.886:
        texto = (
            "✅ Retroceso Fibonacci H1 profundo (78.6–88.6%) — banda TESLABTC de alta probabilidad."
        )
    else:
        texto = "⚠️ Retroceso Fibonacci H1 extremo (> 88.6%) — riesgo de cambio de ciclo."

    return ratio, texto


# ============================================================
# 🔹 POI TESLABTC por banda Fibo 61.8–88.6
#     - H4: respecto a TENDENCIA PRINCIPAL (D si no es lateral;
#            si D es lateral, se usa H4).
#     - H1: respecto a la tendencia PROPIA de H1 (corrección).
# ============================================================
def _poi_fibo_band(
    estado: Optional[str],
    hi: Optional[float],
    lo: Optional[float],
) -> Optional[Tuple[float, float]]:
    """
    Devuelve un POI [low, high] que encierra la banda 61.8–88.6 del impulso.
    """
    if hi is None or lo is None or hi == lo:
        return None

    hi = float(hi)
    lo = float(lo)

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
# ------------------------------------------------------------
# 🔹 Detector institucional — OB, FVG y POI cercanos TESLABTC
# ------------------------------------------------------------
def _detectar_ob_poi_cercanos(
    kl_h4: List[Dict[str, Any]],
    kl_h1: List[Dict[str, Any]],
    tf_h4: Dict[str, Any],
    tf_h1: Dict[str, Any],
) -> Dict[str, str]:
    zonas: Dict[str, str] = {}

    try:
        # -------------------------------
        # 🔸 ORDER BLOCK H4
        # -------------------------------
        if len(kl_h4) >= 3:
            ult = kl_h4[-1]
            ant = kl_h4[-2]
            estado = tf_h4.get("estado")

            if estado == "alcista" and ult["low"] > ant["low"]:
                zonas["OB_H4"] = f"{ant['low']:.2f}–{ult['low']:.2f}"
                zonas["OB_H4_TIPO"] = "Demanda"
            elif estado == "bajista" and ult["high"] < ant["high"]:
                zonas["OB_H4"] = f"{ult['high']:.2f}–{ant['high']:.2f}"
                zonas["OB_H4_TIPO"] = "Oferta"

        # -------------------------------
        # 🔹 ORDER BLOCK H1
        # -------------------------------
        if len(kl_h1) >= 3:
            ult = kl_h1[-1]
            ant = kl_h1[-2]
            estado = tf_h1.get("estado")

            if estado == "alcista" and ult["low"] > ant["low"]:
                zonas["OB_H1"] = f"{ant['low']:.2f}–{ult['low']:.2f}"
                zonas["OB_H1_TIPO"] = "Demanda"
            elif estado == "bajista" and ult["high"] < ant["high"]:
                zonas["OB_H1"] = f"{ult['high']:.2f}–{ant['high']:.2f}"
                zonas["OB_H1_TIPO"] = "Oferta"

        # -------------------------------
        # ⚙️ FAIR VALUE GAP H1 (últimas 3 velas)
        # -------------------------------
        if len(kl_h1) >= 3:
            v1, v2, v3 = kl_h1[-3], kl_h1[-2], kl_h1[-1]
            if v2["low"] > v1["high"]:
                zonas["FVG_H1"] = f"{v1['high']:.2f}–{v2['low']:.2f}"
            elif v2["high"] < v1["low"]:
                zonas["FVG_H1"] = f"{v2['high']:.2f}–{v1['low']:.2f}"

        # -------------------------------
        # ⚙️ POI por retroceso Fibo profundo (61.8–88.6)
        # -------------------------------
        def _fibo_band(low, high, estado):
            if not low or not high or low == high:
                return None
            hi, lo = float(high), float(low)
            if estado == "alcista":
                base, tope = lo, hi
            elif estado == "bajista":
                base, tope = hi, lo
            else:
                return None
            amp = tope - base
            lvl_618 = base + 0.618 * amp
            lvl_886 = base + 0.886 * amp
            return round(min(lvl_618, lvl_886), 2), round(max(lvl_618, lvl_886), 2)

        if tf_h4.get("estado") in ("alcista", "bajista"):
            h4_hi, h4_lo = tf_h4.get("HH") or tf_h4.get("RANGO_HIGH"), tf_h4.get("LL") or tf_h4.get("RANGO_LOW")
            poi_h4 = _fibo_band(h4_lo, h4_hi, tf_h4["estado"])
            if poi_h4:
                zonas["POI_H4"] = f"{poi_h4[0]}–{poi_h4[1]}"

        if tf_h1.get("estado") in ("alcista", "bajista"):
            h1_hi, h1_lo = tf_h1.get("HH") or tf_h1.get("RANGO_HIGH"), tf_h1.get("LL") or tf_h1.get("RANGO_LOW")
            poi_h1 = _fibo_band(h1_lo, h1_hi, tf_h1["estado"])
            if poi_h1:
                zonas["POI_H1"] = f"{poi_h1[0]}–{poi_h1[1]}"

    except Exception as e:
        print(f"⚠️ Error en _detectar_ob_poi_cercanos: {e}")

    return zonas


# ============================================================
# 🌟 TESLABTC — ANÁLISIS PREMIUM REAL (v5.3)
# ============================================================
def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    now = datetime.now(TZ_COL)
    fecha_txt = now.strftime("%d/%m/%Y %H:%M:%S")

    # 🔹 Precio
    precio, fuente = _safe_get_price(symbol)
    precio_txt = f"{precio:,.2f} USD" if isinstance(precio, (int, float)) else "—"

    # 🔹 Datos Multi-TF
    kl_15m = _safe_get_klines(symbol, "15m", 600)
    kl_h1 = _safe_get_klines(symbol, "1h", 600)
    kl_h4 = _safe_get_klines(symbol, "4h", 600)
    kl_d = _safe_get_klines(symbol, "1d", 400)

    # 🧭 Tendencias TESLABTC usando ZigZag estructural
    tf_d = _detectar_tendencia_zigzag(kl_d, depth=12, deviation=5.0, backstep=2)
    tf_h4 = _detectar_tendencia_zigzag(kl_h4, depth=12, deviation=5.0, backstep=2)
    tf_h1 = _detectar_tendencia_zigzag(kl_h1, depth=12, deviation=5.0, backstep=2)
    tf_m15 = _detectar_tendencia_zigzag(kl_15m, depth=12, deviation=5.0, backstep=2)

    asian = _asian_range(kl_15m)
    pd = _pdh_pdl(kl_15m)
    sesion_txt, sesion_activa = _estado_sesion_ny()

    # 🔹 Zonas (PDH/PDL, Asia, rangos) base
    zonas = _fmt_zonas(asian, pd, kl_15m, kl_d, kl_h4, kl_h1)

    # 🔹 POI TESLABTC por Fibo 61.8–88.6
    # H4: respecto a tendencia PRINCIPAL (D si no es lateral; si no, H4).
    estado_principal = (
        tf_d.get("estado")
        if tf_d.get("estado") in ("alcista", "bajista")
        else tf_h4.get("estado")
    )
    poi_h4 = _poi_fibo_band(
        estado_principal,
        zonas.get("H4_HIGH"),
        zonas.get("H4_LOW"),
    )
    if poi_h4:
        zonas["POI_H4"] = f"{poi_h4[0]:.2f}–{poi_h4[1]:.2f}"

    # H1: respecto a la propia tendencia de H1 (corrección).
    poi_h1 = _poi_fibo_band(
        tf_h1.get("estado"),
        zonas.get("H1_HIGH"),
        zonas.get("H1_LOW"),
    )
    if poi_h1:
        zonas["POI_H1"] = f"{poi_h1[0]:.2f}–{poi_h1[1]:.2f}"

    # Inyectar rangos a cada temporalidad para el formatter
    tf_d["RANGO_HIGH"] = zonas.get("D_HIGH")
    tf_d["RANGO_LOW"] = zonas.get("D_LOW")
    tf_h4["RANGO_HIGH"] = zonas.get("H4_HIGH")
    tf_h4["RANGO_LOW"] = zonas.get("H4_LOW")
    tf_h1["RANGO_HIGH"] = zonas.get("H1_HIGH")
    tf_h1["RANGO_LOW"] = zonas.get("H1_LOW")

    # 🛠️ Fallback: si algún rango viene vacío, usar high/low promedio de las últimas velas
    def _fallback_range(kl: List[Dict[str, Any]], n: int = 40) -> Tuple[float, float]:
        try:
            data = kl[-n:]
            highs = [float(k["high"]) for k in data]
            lows = [float(k["low"]) for k in data]
            return round(max(highs), 2), round(min(lows), 2)
        except Exception:
            return None, None

    if tf_d.get("RANGO_HIGH") is None or tf_d.get("RANGO_LOW") is None:
        hi, lo = _fallback_range(kl_d, 60)
        tf_d["RANGO_HIGH"], tf_d["RANGO_LOW"] = hi, lo

    if tf_h4.get("RANGO_HIGH") is None or tf_h4.get("RANGO_LOW") is None:
        hi, lo = _fallback_range(kl_h4, 40)
        tf_h4["RANGO_HIGH"], tf_h4["RANGO_LOW"] = hi, lo

    if tf_h1.get("RANGO_HIGH") is None or tf_h1.get("RANGO_LOW") is None:
        hi, lo = _fallback_range(kl_h1, 40)
        tf_h1["RANGO_HIGH"], tf_h1["RANGO_LOW"] = hi, lo
    # 🧩 Fallback si zonas vino vacío — usar los rangos detectados manualmente
    if not zonas or len(zonas) < 3:
        zonas.update({
            "D_HIGH": tf_d.get("RANGO_HIGH"),
            "D_LOW": tf_d.get("RANGO_LOW"),
            "H4_HIGH": tf_h4.get("RANGO_HIGH"),
            "H4_LOW": tf_h4.get("RANGO_LOW"),
            "H1_HIGH": tf_h1.get("RANGO_HIGH"),
            "H1_LOW": tf_h1.get("RANGO_LOW"),
        })

    # 🔹 OB/POI por detector clásico + filtro por rango swing
    ob_poi = _detectar_ob_poi_cercanos(kl_h4, kl_h1, tf_h4, tf_h1)
    if ob_poi:
        zonas.update(ob_poi)

    zonas["OB_H4"] = _ob_en_rango(
        zonas.get("OB_H4"),
        zonas.get("H4_HIGH"),
        zonas.get("H4_LOW"),
    )
    zonas["OB_H1"] = _ob_en_rango(
        zonas.get("OB_H1"),
        zonas.get("H1_HIGH"),
        zonas.get("H1_LOW"),
    )

    if zonas.get("OB_H4") is None:
        zonas.pop("OB_H4", None)
    if zonas.get("OB_H1") is None:
        zonas.pop("OB_H1", None)

    # 🔹 Confirmaciones con contexto
    conf = _confirmaciones(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian,
        pd,
        tf_d,
        tf_h1,
        sesion_activa,
    )

    # Añadir confirmación Fibo H1 (61.8–88.6)
    _, fib_txt = _fib_retracement_h1(
        precio if isinstance(precio, (int, float)) else math.nan,
        tf_h1,
        zonas,
    )
    if fib_txt:
        conf["Fibo H1 (61.8–88.6)"] = fib_txt

    # 🔹 Dirección general (texto auxiliar)
    tendencia_d = tf_d.get("estado", "—")
    tendencia_h4 = tf_h4.get("estado", "—")
    tendencia_h1 = tf_h1.get("estado", "—")
    direccion_general = (
        "🟢 Alcista"
        if tendencia_h4 == "alcista"
        else "🔴 Bajista"
        if tendencia_h4 == "bajista"
        else "⚪ Lateral"
    )
    estructura_txt = (
        f"D: {tendencia_d.upper()} | H4: {tendencia_h4.upper()} | H1: {tendencia_h1.upper()}"
    )

    # 🔹 Interpretación macro (para UI)
    contexto = interpretar_contexto(tf_d, tf_h4, tf_h1, conf, zonas)

    # 🔹 Escenarios (continuidad y corrección)
    esc1, esc2, concl = _escenarios(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian,
        pd,
        tf_d,
        tf_h4,
        tf_h1,
        conf,
    )
    # ============================================================
    # 🔹 Enriquecer escenarios TESLABTC antes del retorno
    # ============================================================
    def _enriquecer_escenario(e, tipo_default, riesgo_default):
        if not isinstance(e, dict):
            e = {}

        return {
            "tipo": e.get("tipo", tipo_default),
            "riesgo": e.get("riesgo", riesgo_default),
            "contexto": e.get("contexto", "Transición estructural TESLABTC."),
            "setup_estado": e.get("setup_estado", "⏳ Sin setup válido — esperando confirmaciones."),
            "setup": e.get("setup", {
                "zona_entrada": zonas.get("POI_H1", "—"),
                "tp1": zonas.get("PDL", "—"),
                "tp2": zonas.get("ASIAN_LOW", "—"),
                "tp3": zonas.get("ASIAN_HIGH", "—"),
                "sl": zonas.get("PDH", "—"),
                "observacion": "Esperar ruptura BOS M5 antes de ejecutar entrada institucional."
            }),
            "confs_favor": e.get("confs_favor", list(conf.keys())[:2] if conf else []),
            "confs_pendientes": e.get("confs_pendientes", list(conf.keys())[2:4] if conf else []),
            "texto": e.get("texto", f"Escenario de {tipo_default}: precio en fase de {'retroceso' if tipo_default == 'Venta' else 'transición'}, "
                                     "esperar confirmación estructural en M15/M5.")
        }

    esc1 = _enriquecer_escenario(esc1, "Venta", "Medio")
    esc2 = _enriquecer_escenario(esc2, "Compra", "Alto")

    # 🔹 Setup activo M5 (BOS + volumen)
    setup_activo = _setup_activo_m5(symbol)

    # Ajuste: sólo mantenemos setup ACTIVO si el precio está dentro del POI H1
    if setup_activo.get("activo") and zonas.get("POI_H1") and isinstance(
        precio, (int, float)
    ):
        try:
            lo_poi, hi_poi = [
                float(x.strip())
                for x in str(zonas["POI_H1"]).replace("–", "-").split("-")
            ]
            lo_poi, hi_poi = min(lo_poi, hi_poi), max(lo_poi, hi_poi)
            if not (lo_poi <= float(precio) <= hi_poi):
                setup_activo = {"activo": False}
        except Exception:
            setup_activo = {"activo": False}
    else:
        setup_activo = {"activo": False}

    # 🔹 Reflexión
    reflexion = random.choice(REFLEXIONES)
    slogan = "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"

    # 🔹 Conclusión operativa
    if setup_activo.get("activo"):
        conclusion_final = (
            "Estructura y volumen alineados intradía en POI H1. "
            "Priorizar la ejecución del Setup activo respetando gestión 1:2 "
            "y mover a BE en 1:1 + 50%."
        )
    elif sesion_activa and tendencia_h4 == "bajista" and tendencia_h1 == "bajista":
        conclusion_final = (
            "Estructura bajista consolidada: priorizar ventas tras retrocesos a oferta válida."
        )
    elif sesion_activa and tendencia_h4 == "alcista" and tendencia_h1 == "alcista":
        conclusion_final = (
            "Estructura alcista confirmada: buscar compras tras mitigación en demanda."
        )
    else:
        conclusion_final = concl

        
    # ============================================================
    # 🔁 Verificación de retorno válido
    # ============================================================
    if not locals().get("resultado") and not locals().get("analisis"):
        return {"🧠 TESLABTC.KG": {
            "error": "sin_datos",
            "detalle": "No se obtuvo respuesta de estructura o conexión fallida."
        }}

    # ============================================================
    # 🔹 Reforzar escenarios antes del payload final
    # ============================================================

    if not isinstance(esc1, dict):
        esc1 = {}
    if not isinstance(esc2, dict):
        esc2 = {}

    # Si algún campo viene vacío, asignar valores por defecto
    def _normalize_escenario(e, tipo, riesgo):
        return {
            "tipo": e.get("tipo", tipo),
            "riesgo": e.get("riesgo", riesgo),
            "contexto": e.get("contexto", contexto or "Estructura neutral."),
            "setup_estado": e.get("setup_estado", "⏳ Sin setup válido — esperando confirmaciones."),
            "setup": e.get("setup", {
                "zona_entrada": zonas.get("POI_H1", "—"),
                "tp1": zonas.get("PDL", "—"),
                "tp2": zonas.get("ASIAN_LOW", "—"),
                "tp3": zonas.get("ASIAN_HIGH", "—"),
                "sl": zonas.get("PDH", "—"),
                "observacion": "Esperar ruptura BOS M5 antes de ejecutar entrada institucional."
            }),
            "confs_favor": e.get("confs_favor", list(conf.keys())[:2] if conf else []),
            "confs_pendientes": e.get("confs_pendientes", list(conf.keys())[2:4] if conf else []),
            "texto": e.get("texto", f"Escenario de {tipo}: precio en fase operativa, esperar confirmación estructural en M15/M5."),
        }

    esc1 = _normalize_escenario(esc1, "Venta", "Medio")
    esc2 = _normalize_escenario(esc2, "Compra", "Alto")

    # ============================================================
    # 🧠 Payload final enriquecido
    # ============================================================
    payload = {
        "fecha": fecha_txt,
        "nivel_usuario": "Premium",
        "sesión": sesion_txt,
        "activo": symbol,
        "precio_actual": precio_txt,
        "fuente_precio": fuente,
        "estructura_detectada": {"D": tf_d, "H4": tf_h4, "H1": tf_h1, "M15": tf_m15},
        "direccion_general": direccion_general,
        "estructura_resumen": estructura_txt,
        "contexto_general": contexto,
        "zonas_detectadas": zonas,
        "confirmaciones": conf,
        "escenario_1": esc1,  # 🔹 ahora con datos completos
        "escenario_2": esc2,  # 🔹 ahora con datos completos
        "setup_tesla": setup_activo,
        "conclusion_general": conclusion_final,
        "reflexion": reflexion,
        "slogan": slogan,
        "simbolo": symbol,
        "temporalidades": ["D", "H4", "H1", "M15", "M5"],
    }

    # 🧩 Fallback si zonas vino vacío — asegurar que el payload tenga rangos válidos
    if not zonas or len(zonas) < 3:
        zonas.update({
            "D_HIGH": tf_d.get("RANGO_HIGH"),
            "D_LOW": tf_d.get("RANGO_LOW"),
            "H4_HIGH": tf_h4.get("RANGO_HIGH"),
            "H4_LOW": tf_h4.get("RANGO_LOW"),
            "H1_HIGH": tf_h1.get("RANGO_HIGH"),
            "H1_LOW": tf_h1.get("RANGO_LOW"),
        })
        payload["zonas_detectadas"] = zonas

    # 🔹 Formateo final (UI)
    from utils.intelligent_formatter import (
        construir_mensaje_operativo,
        construir_mensaje_free,
    )

    nivel_usuario = payload.get("nivel_usuario", "Premium")
    if nivel_usuario.lower() == "premium":
        payload["mensaje_formateado"] = construir_mensaje_operativo(payload)
    else:
        payload["mensaje_formateado"] = construir_mensaje_free(payload)

    # ============================================================
    # 🔁 Verificación de retorno válido (ubicación correcta)
    # ============================================================
    if not payload or "estructura_detectada" not in payload:
        return {"🧠 TESLABTC.KG": {
            "error": "sin_datos",
            "detalle": "No se obtuvo respuesta de estructura o conexión fallida (payload vacío)."
        }}

    return {"🧠 TESLABTC.KG": payload}

# ============================================================
# 🔹 Interpretación contextual inteligente TESLABTC (v5.3)
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

    # Liquidez
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
