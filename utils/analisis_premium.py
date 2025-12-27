from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3.1 PRO REAL MARKET)
# ============================================================
# Versión simplificada:
#   - Swing: estructura H4/H1 con zona premium H4 (61.8–88.6)
#   - Scalping: M5 en sesión NY, a favor y contra tendencia H1
#   - Sin zonas de liquidez ni escenarios antiguos, sólo acción del precio
# ============================================================

import requests
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


def _safe_get_klines(
    symbol: str, interval: str = "15m", limit: int = 500
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
# 🔹 Pivotes ZigZag y tendencia
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


def _zigzag_pivots(
    kl: List[Dict[str, Any]],
    depth: int = 12,
    deviation: float = 5.0,
    backstep: int = 2,
) -> List[Tuple[int, str, float]]:
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

        # pivote opuesto con desviación mínima
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

    _, h1 = highs[-2]
    _, h2 = highs[-1]
    _, l1 = lows[-2]
    _, l2 = lows[-1]

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

    _, _, price_last = piv[-1]

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


def _poi_fibo_band(
    estado: Optional[str],
    hi: Optional[float],
    lo: Optional[float],
) -> Optional[Tuple[float, float]]:
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
# 🔹 Sesión NY + ventana de scalping
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


def _ventana_scalping_ny() -> bool:
    """Ventana operativa para SCALPING en NY: primeras 2 horas."""
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end = start + timedelta(hours=2)
    return start <= ahora <= end


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
# 🔹 Cálculo de TP numérico
# ------------------------------------------------------------
def _calcular_tp(entrada: float, sl: float, rr: float) -> float:
    try:
        entrada = float(entrada)
        sl = float(sl)
        rr = float(rr)
    except Exception:
        return float(entrada)

    if entrada == sl:
        return float(entrada)

    riesgo = abs(entrada - sl)
    if entrada > sl:
        return entrada + riesgo * rr
    return entrada - riesgo * rr


# ============================================================
# 🌟 TESLABTC — ANÁLISIS PREMIUM REAL (v5.3, versión simplificada)
# ============================================================
def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """
    Versión simplificada TESLABTC:
    - SCALPING: M5 en ventana de apertura NY (primeras 2 horas), a favor y contra H1.
    - SWING: H4 + H1, con TP3 en HIGH/LOW de H4.
    - No mostramos zonas de liquidez; sólo acción del precio.
    """
    now = datetime.now(TZ_COL)
    fecha_txt = now.strftime("%d/%m/%Y %H:%M:%S")

    # 🔹 Precio actual
    precio, fuente = _safe_get_price(symbol)
    precio_num = float(precio) if isinstance(precio, (int, float)) else None
    precio_txt = f"{precio_num:,.2f} USD" if precio_num is not None else "—"

    # 🔹 Datos por temporalidad
    kl_h4 = _safe_get_klines(symbol, "4h", 400)
    kl_h1 = _safe_get_klines(symbol, "1h", 400)
    kl_m5 = _safe_get_klines(symbol, "5m", 300)

    # 🧭 Estructura con ZigZag (sólo para dirección general)
    tf_h4 = _detectar_tendencia_zigzag(kl_h4, depth=12, deviation=5.0, backstep=2) if kl_h4 else {"estado": "lateral"}
    tf_h1 = _detectar_tendencia_zigzag(kl_h1, depth=10, deviation=4.0, backstep=2) if kl_h1 else {"estado": "lateral"}

    dir_h4 = tf_h4.get("estado", "lateral")
    dir_h1 = tf_h1.get("estado", "lateral")

    # 🔹 Rango H4 aproximado (para TP3 swing)
    if kl_h4:
        h4_high = max(k["high"] for k in kl_h4[-60:])
        h4_low = min(k["low"] for k in kl_h4[-60:])
    else:
        h4_high = None
        h4_low = None

    # 🔹 POI H4 61.8–88.6 para swing (zona premium)
    poi_h4 = _poi_fibo_band(dir_h4, h4_high, h4_low)
    poi_txt = "—"
    in_premium = False
    if poi_h4:
        p_lo, p_hi = sorted([float(poi_h4[0]), float(poi_h4[1])])
        poi_txt = f"{p_lo:,.2f}–{p_hi:,.2f} USD"
        if precio_num is not None and p_lo <= precio_num <= p_hi:
            in_premium = True

    # 🕒 Sesión NY y ventana SCALPING
    sesion_txt, ny_activa = _estado_sesion_ny()
    ventana_scalping = _ventana_scalping_ny()

    # ============================
    # 📊 SCALPING (M5)
    # ============================
    scalping_cont: Dict[str, Any] = {
        "activo": False,
        "direccion": "—",
        "riesgo": "N/A",
        "zona_reaccion": "—",
        "sl": "—",
        "tp1_rr": "1:1 (50% + BE)",
        "tp2_rr": "1:2 (50%)",
        "contexto": "Fuera de ventana o sin dirección clara en H1.",
    }
    scalping_corr: Dict[str, Any] = dict(scalping_cont)  # copia base

    if kl_m5 and ny_activa and ventana_scalping and dir_h1 in ("alcista", "bajista"):
        highs_m5 = [k["high"] for k in kl_m5[-30:]]
        lows_m5 = [k["low"] for k in kl_m5[-30:]]
        if len(highs_m5) >= 2 and len(lows_m5) >= 2:
            prev_high = max(highs_m5[:-1])
            prev_low = min(lows_m5[:-1])

            if dir_h1 == "alcista":
                # Continuación: compras
                scalping_cont.update(
                    {
                        "activo": True,
                        "direccion": "ALCISTA (a favor de H1)",
                        "riesgo": "Bajo",
                        "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                        "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                        "contexto": "Entrada SCALPING a favor de la estructura intradía H1.",
                    }
                )
                # Corrección: ventas
                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (contra H1)",
                        "riesgo": "Alto",
                        "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                        "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                        "contexto": "Entrada SCALPING de corrección intradía contra H1.",
                    }
                )
            else:
                # dir_h1 == "bajista"
                # Continuación: ventas
                scalping_cont.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (a favor de H1)",
                        "riesgo": "Bajo",
                        "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                        "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                        "contexto": "Entrada SCALPING a favor de la estructura intradía H1.",
                    }
                )
                # Corrección: compras
                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "ALCISTA (contra H1)",
                        "riesgo": "Alto",
                        "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                        "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                        "contexto": "Entrada SCALPING de corrección intradía contra H1.",
                    }
                )

    # ============================
    # 🕰️ SWING (H4 + H1)
    # ============================
    swing: Dict[str, Any] = {
        "activo": False,
        "direccion": "—",
        "riesgo": "N/A",
        "premium_zone": poi_txt,
        "zona_reaccion": "—",
        "sl": "—",
        "tp1_rr": "1:1 (BE)",
        "tp2_rr": "1:2 (50%)",
        "tp3_objetivo": "—",
        "contexto": "Esperando alineación H4/H1 y BOS H1 en zona premium.",
    }

    # High/Low de referencia en H1 para construir el mensaje
    prev_high_h1 = prev_low_h1 = None
    if kl_h1:
        highs_h1 = [k["high"] for k in kl_h1[-40:]]
        lows_h1 = [k["low"] for k in kl_h1[-40:]]
        if len(highs_h1) >= 2 and len(lows_h1) >= 2:
            prev_high_h1 = max(highs_h1[:-1])
            prev_low_h1 = min(lows_h1[:-1])

    # Dirección base del swing:
    # 1) Preferimos H4 si tiene tendencia clara.
    # 2) Si H4 está lateral pero H1 tiene dirección, usamos H1.
    swing_dir = None
    if dir_h4 in ("alcista", "bajista"):
        swing_dir = dir_h4
    elif dir_h1 in ("alcista", "bajista"):
        swing_dir = dir_h1

    # Siempre que tengamos dirección y referencias H1, construimos mensaje de "esperando ruptura"
    if swing_dir in ("alcista", "bajista") and prev_high_h1 is not None and prev_low_h1 is not None:
        if swing_dir == "alcista":
            direccion_txt = (
                "ALCISTA (buscando continuación del ciclo mayor: H4/H1)"
                if dir_h4 == "alcista"
                else "ALCISTA (basado en H1; H4 en rango)"
            )
            zona_reac_txt = (
                f"Esperando quiebre y cierre del HIGH H1 ≈ {prev_high_h1:,.2f} USD "
                f"a favor de la estructura superior."
            )
            sl_txt = f"LOW H1 previo ≈ {prev_low_h1:,.2f} USD"
            if h4_high is not None:
                tp3_txt = f"HIGH H4 ≈ {h4_high:,.2f} USD"
            else:
                tp3_txt = "Extensión alcista del último impulso H4/H1"
        else:
            direccion_txt = (
                "BAJISTA (buscando continuación del ciclo mayor: H4/H1)"
                if dir_h4 == "bajista"
                else "BAJISTA (basado en H1; H4 en rango)"
            )
            zona_reac_txt = (
                f"Esperando quiebre y cierre del LOW H1 ≈ {prev_low_h1:,.2f} USD "
                f"a favor de la estructura superior."
            )
            sl_txt = f"HIGH H1 previo ≈ {prev_high_h1:,.2f} USD"
            if h4_low is not None:
                tp3_txt = f"LOW H4 ≈ {h4_low:,.2f} USD"
            else:
                tp3_txt = "Extensión bajista del último impulso H4/H1"

        contexto_base = []

        if dir_h4 not in ("alcista", "bajista"):
            contexto_base.append("H4 en rango: la dirección principal se toma de H1.")
        if not in_premium:
            contexto_base.append(
                "El precio aún no ha entrado en la zona premium H4 (61.8–88.6)."
            )
        if dir_h1 != swing_dir:
            contexto_base.append(
                "H1 todavía no está totalmente alineado con la dirección de swing."
            )

        contexto_base.append(
            "Se requiere quiebre y cierre de H1 en la dirección del swing para activar la entrada."
        )

        swing.update(
            {
                "activo": False,
                "direccion": direccion_txt,
                "riesgo": "Medio" if dir_h1 == swing_dir else "Alto",
                "zona_reaccion": zona_reac_txt,
                "sl": sl_txt,
                "tp3_objetivo": tp3_txt,
                "contexto": " ".join(contexto_base),
            }
        )

    # ✔️ Condición TESLABTC para marcar el SWING como ACTIVO
    if (
        kl_h1
        and dir_h4 in ("alcista", "bajista")
        and dir_h1 == dir_h4
        and precio_num is not None
        and in_premium
    ):
        bos_h1 = detectar_bos(kl_h1)
        bos_ok = bos_h1.get("bos") and (
            (bos_h1.get("tipo") == "alcista" and dir_h4 == "alcista")
            or (bos_h1.get("tipo") == "bajista" and dir_h4 == "bajista")
        )

        if bos_ok and prev_high_h1 is not None and prev_low_h1 is not None:
            if dir_h4 == "alcista":
                zona_reac = (
                    f"Quiebre y cierre sobre el HIGH H1 ≈ {prev_high_h1:,.2f} USD "
                    f"en zona premium H4."
                )
                sl_txt = f"LOW H1 previo ≈ {prev_low_h1:,.2f} USD"
                tp3_txt = (
                    f"HIGH H4 ≈ {h4_high:,.2f} USD"
                    if h4_high is not None
                    else "HIGH H4"
                )
                direccion_txt = "ALCISTA (H1 a favor de H4)"
            else:
                zona_reac = (
                    f"Quiebre y cierre bajo el LOW H1 ≈ {prev_low_h1:,.2f} USD "
                    f"en zona premium H4."
                )
                sl_txt = f"HIGH H1 previo ≈ {prev_high_h1:,.2f} USD"
                tp3_txt = (
                    f"LOW H4 ≈ {h4_low:,.2f} USD"
                    if h4_low is not None
                    else "LOW H4"
                )
                direccion_txt = "BAJISTA (H1 a favor de H4)"

            swing.update(
                {
                    "activo": True,
                    "direccion": direccion_txt,
                    "riesgo": "Medio",
                    "zona_reaccion": zona_reac,
                    "sl": sl_txt,
                    "tp3_objetivo": tp3_txt,
                    "contexto": "Operación SWING siguiendo estructura H4, con BOS H1 confirmado en zona premium.",
                }
            )

    # ✨ Reflexión
    reflexion = random.choice(REFLEXIONES)

    # Estructura mínima para compatibilidad
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
