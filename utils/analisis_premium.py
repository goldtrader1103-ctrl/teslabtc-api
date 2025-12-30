from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3.1 PRO REAL MARKET)
# ============================================================
# Versión simplificada y coherente con el formatter v5.8:
#   - Swing: estructura H4/H1 con zona premium H4 (61.8–88.6)
#   - Scalping: M5 a favor / contra H1 (24/7, modo backtest)
#   - Estructura H4/H1 con rangos para contexto
#   - Sin PDH/PDL/Asia aquí; solo acción del precio y premium
# ============================================================

import requests
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import pytz  # por compatibilidad, aunque no se use directamente

from utils.estructura_utils import detectar_bos

# ------------------------------
# 🌎 Config base
# ------------------------------
TZ_COL = timezone(timedelta(hours=-5))
BINANCE_REST_BASE = "https://api.binance.com"
UA = {"User-Agent": "teslabtc-kg/5.3.1"}

# ============================================================
# 🧠 Reflexiones TESLABTC
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
        bos = "✔️"
    elif h2 < h1 and l2 < l1:
        estado = "bajista"
        bos = "✔️"
    else:
        estado = "lateral"
        bos = "—"

    _, _, price_last = piv[-1]

    return {
        "estado": estado,
        "BOS": bos,
        "HH": h2,
        "LH": h1,
        "LL": l2,
        "HL": l1,
        "ultimo_pivote": price_last,
        "pivotes": piv[-6:],
    }

def _poi_fibo_band(
    estado: Optional[str],
    hi: Optional[float],
    lo: Optional[float],
) -> Optional[Tuple[float, float]]:
    """
    Devuelve la banda 61.8–88.6 % del último impulso H4.

    Regla TESLABTC:
      - Estructura ALCISTA  👉 Fibo de izquierda a derecha, del BAJO al ALTO.
      - Estructura BAJISTA 👉 Fibo de izquierda a derecha, del ALTO al BAJO.
      - En rango usamos low→high por defecto.
    """
    if hi is None or lo is None or hi == lo:
        return None

    hi = float(hi)
    lo = float(lo)

    estado_norm = (estado or "").strip().lower()

    if estado_norm == "alcista":
        # impulso de low → high
        base, tope = lo, hi
    elif estado_norm == "bajista":
        # impulso de high → low
        base, tope = hi, lo
    else:
        # lateral / sin_datos: tomamos low → high
        base, tope = lo, hi

    amp = tope - base
    if amp <= 0:
        return None

    # banda 61.8–88.6 % del impulso
    lvl_618 = base + 0.618 * amp
    lvl_886 = base + 0.886 * amp

    banda_low = min(lvl_618, lvl_886)
    banda_high = max(lvl_618, lvl_886)
    return round(banda_low, 2), round(banda_high, 2)

# ------------------------------------------------------------
# 🔹 Sesiones (Asia, Londres, NY)
# ------------------------------------------------------------
def _estado_sesiones() -> Tuple[str, Dict[str, bool]]:
    """
    Devuelve:
      - Texto de la sesión actual
      - Flags booleanos: {"asia": bool, "londres": bool, "ny": bool}
    Horario Colombia:
      • ASIA:    17:00 – 02:00
      • LONDRES: 02:00 – 11:00
      • NY:      07:00 – 15:00
    """
    ahora = datetime.now(TZ_COL)
    m = ahora.hour * 60 + ahora.minute  # minutos desde medianoche

    asia = (m >= 17 * 60) or (m < 2 * 60)
    londres = 2 * 60 <= m < 11 * 60
    ny = 7 * 60 <= m < 15 * 60

    if ny and londres:
        sesion_txt = "Sesión NY-LONDRES (NY 07:00–15:00 | LONDRES 02:00–11:00 COL)"
    elif londres and asia:
        sesion_txt = "Sesión ASIA-LONDRES (ASIA 17:00–02:00 | LONDRES 02:00–11:00 COL)"
    elif ny:
        sesion_txt = "Sesión NY (07:00–15:00 COL)"
    elif londres:
        sesion_txt = "Sesión LONDRES (02:00–11:00 COL)"
    elif asia:
        sesion_txt = "Sesión ASIA (17:00–02:00 COL)"
    else:
        # Lo interpretamos como extensión de NY
        sesion_txt = "Sesión NY (horario extendido fuera de cash RTH)."

    return sesion_txt, {"asia": asia, "londres": londres, "ny": ny}


# ============================================================
# 🌟 TESLABTC — ANÁLISIS PREMIUM REAL (v5.3 simplificado)
# ============================================================
def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """
    - Usa estructura H4/H1 para SWING
    - Usa M5 para señales SCALPING (a favor/contra H1)
    - Análisis 24/7 (modo backtest); no se apaga por sesión.
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

    # Estructura con ZigZag (dirección general)
    tf_h4 = _detectar_tendencia_zigzag(kl_h4, depth=12, deviation=5.0, backstep=2)
    tf_h1 = _detectar_tendencia_zigzag(kl_h1, depth=10, deviation=4.0, backstep=2)
    dir_h4 = tf_h4.get("estado", "lateral")
    dir_h1 = tf_h1.get("estado", "lateral")

    # Rango H4 para contexto y TP3 swing
    if kl_h4:
        h4_high = max(k["high"] for k in kl_h4[-60:])
        h4_low = min(k["low"] for k in kl_h4[-60:])
    else:
        h4_high = None
        h4_low = None

    # Rango H1 para contexto
    if kl_h1:
        h1_high = max(k["high"] for k in kl_h1[-60:])
        h1_low = min(k["low"] for k in kl_h1[-60:])
    else:
        h1_high = None
        h1_low = None

    # POI H4 61.8–88.6 para swing (zona premium)
    poi_h4 = _poi_fibo_band(dir_h4, h4_high, h4_low)
    poi_txt = "—"
    in_premium = False
    p_lo = p_hi = None
    if poi_h4:
        p_lo, p_hi = sorted([float(poi_h4[0]), float(poi_h4[1])])
        poi_txt = f"{p_lo:,.2f}–{p_hi:,.2f}"
        if precio_num is not None and p_lo <= precio_num <= p_hi:
            in_premium = True

    # Sesión actual
    sesion_txt, ses_flags = _estado_sesiones()

    # Modo backtest: scalping siempre permitido
    ventana_scalping = True

    # ============================
    # 📊 SCALPING (M5)
    # ============================
    scalping_cont: Dict[str, Any] = {
        "activo": False,
        "direccion": "—",
        "riesgo": "N/A",
        "zona_reaccion": "—",
        "sl": "—",
        "tp1_rr": "—",
        "tp2_rr": "—",
        "contexto": "Sin dirección clara en H1.",
    }
    scalping_corr: Dict[str, Any] = dict(scalping_cont)

    # Siempre calculamos niveles de scalping si hay datos de M5.
    if kl_m5 and ventana_scalping:
        highs_m5 = [k["high"] for k in kl_m5[-30:]]
        lows_m5 = [k["low"] for k in kl_m5[-30:]]
        if len(highs_m5) >= 2 and len(lows_m5) >= 2:
            prev_high = max(highs_m5[:-1])
            prev_low = min(lows_m5[:-1])

            if dir_h1 == "alcista":
                # ✅ CONTINUACIÓN ALCISTA
                entry_cont = prev_high
                sl_cont = prev_low
                r_cont = max(entry_cont - sl_cont, 0)
                tp1_cont = entry_cont + r_cont
                tp2_cont = entry_cont + 2 * r_cont

                scalping_cont.update(
                    {
                        "activo": True,
                        "direccion": "ALCISTA (a favor de H1)",
                        "riesgo": "Bajo",
                        "zona_reaccion": f"{entry_cont:,.2f}",
                        "sl": f"{sl_cont:,.2f}",
                        "tp1_rr": f"{tp1_cont:,.2f}" if r_cont > 0 else "—",
                        "tp2_rr": f"{tp2_cont:,.2f}" if r_cont > 0 else "—",
                        "contexto": (
                            "SCALPING a favor de H1: entrada por ruptura del HIGH M5, "
                            "SL en el LOW M5 previo, TP1 1:1 (mover a BE) y TP2 1:2 con 50% restante."
                        ),
                    }
                )

                # 🔻 CORRECCIÓN BAJISTA
                entry_corr = prev_low
                sl_corr = prev_high
                r_corr = max(sl_corr - entry_corr, 0)
                tp1_corr = entry_corr - r_corr
                tp2_corr = entry_corr - 2 * r_corr

                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (contra H1)",
                        "riesgo": "Alto",
                        "zona_reaccion": f"{entry_corr:,.2f}",
                        "sl": f"{sl_corr:,.2f}",
                        "tp1_rr": f"{tp1_corr:,.2f}" if r_corr > 0 else "—",
                        "tp2_rr": f"{tp2_corr:,.2f}" if r_corr > 0 else "—",
                        "contexto": (
                            "SCALPING de corrección contra H1: entrada por ruptura del LOW M5, "
                            "SL en el HIGH M5 previo, TP1 1:1 (mover a BE) y TP2 1:2 con 50% restante."
                        ),
                    }
                )

            elif dir_h1 == "bajista":
                # ✅ CONTINUACIÓN BAJISTA
                entry_cont = prev_low
                sl_cont = prev_high
                r_cont = max(sl_cont - entry_cont, 0)
                tp1_cont = entry_cont - r_cont
                tp2_cont = entry_cont - 2 * r_cont

                scalping_cont.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (a favor de H1)",
                        "riesgo": "Bajo",
                        "zona_reaccion": f"{entry_cont:,.2f}",
                        "sl": f"{sl_cont:,.2f}",
                        "tp1_rr": f"{tp1_cont:,.2f}" if r_cont > 0 else "—",
                        "tp2_rr": f"{tp2_cont:,.2f}" if r_cont > 0 else "—",
                        "contexto": (
                            "SCALPING a favor de H1: entrada por ruptura del LOW M5, "
                            "SL en el HIGH M5 previo, TP1 1:1 (mover a BE) y TP2 1:2 con 50% restante."
                        ),
                    }
                )

                # 🔺 CORRECCIÓN ALCISTA
                entry_corr = prev_high
                sl_corr = prev_low
                r_corr = max(entry_corr - sl_corr, 0)
                tp1_corr = entry_corr + r_corr
                tp2_corr = entry_corr + 2 * r_corr

                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "ALCISTA (contra H1)",
                        "riesgo": "Alto",
                        "zona_reaccion": f"{entry_corr:,.2f}",
                        "sl": f"{sl_corr:,.2f}",
                        "tp1_rr": f"{tp1_corr:,.2f}" if r_corr > 0 else "—",
                        "tp2_rr": f"{tp2_corr:,.2f}" if r_corr > 0 else "—",
                        "contexto": (
                            "SCALPING de corrección contra H1: entrada por ruptura del HIGH M5, "
                            "SL en el LOW M5 previo, TP1 1:1 (mover a BE) y TP2 1:2 con 50% restante."
                        ),
                    }
                )
            else:
                # 🔁 H1 en rango: seguimos etiquetando por tipo de escenario
                entry_long = prev_high
                sl_long = prev_low
                r_long = max(entry_long - sl_long, 0)
                tp1_long = entry_long + r_long
                tp2_long = entry_long + 2 * r_long

                scalping_cont.update(
                    {
                        "activo": True,
                        "direccion": "ALCISTA (H1 en rango, breakout M5)",
                        "riesgo": "Bajo",   # continuacion => riesgo bajo
                        "zona_reaccion": f"{entry_long:,.2f}",
                        "sl": f"{sl_long:,.2f}",
                        "tp1_rr": f"{tp1_long:,.2f}" if r_long > 0 else "—",
                        "tp2_rr": f"{tp2_long:,.2f}" if r_long > 0 else "—",
                        "contexto": (
                            "SCALPING en rango: ruptura del HIGH M5 dentro del rango de H1; "
                            "se trabaja como oportunidad táctica con gestión conservadora."
                        ),
                    }
                )

                entry_short = prev_low
                sl_short = prev_high
                r_short = max(sl_short - entry_short, 0)
                tp1_short = entry_short - r_short
                tp2_short = entry_short - 2 * r_short

                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (H1 en rango, breakout M5)",
                        "riesgo": "Alto",   # corrección => riesgo alto
                        "zona_reaccion": f"{entry_short:,.2f}",
                        "sl": f"{sl_short:,.2f}",
                        "tp1_rr": f"{tp1_short:,.2f}" if r_short > 0 else "—",
                        "tp2_rr": f"{tp2_short:,.2f}" if r_short > 0 else "—",
                        "contexto": (
                            "SCALPING en rango: ruptura del LOW M5 dentro del rango de H1; "
                            "se trabaja el breakout bajista con tamaño controlado."
                        ),
                    }
                )
                
                entry_short = prev_low
                sl_short = prev_high
                r_short = max(sl_short - entry_short, 0)
                tp1_short = entry_short - r_short
                tp2_short = entry_short - 2 * r_short

                scalping_corr.update(
                    {
                        "activo": True,
                        "direccion": "BAJISTA (H1 en rango, breakout M5)",
                        "riesgo": "Medio",
                        "zona_reaccion": f"{entry_short:,.2f}",
                        "sl": f"{sl_short:,.2f}",
                        "tp1_rr": f"{tp1_short:,.2f}" if r_short > 0 else "—",
                        "tp2_rr": f"{tp2_short:,.2f}" if r_short > 0 else "—",
                        "contexto": (
                            "SCALPING en rango: ruptura del LOW M5 dentro del rango de H1; "
                            "se trabaja el breakout bajista con tamaño controlado."
                        ),
                    }
                )

    # ============================
    # 🕰️ SWING (H4 + H1)
    # ============================
    swing: Dict[str, Any] = {
        "activo": False,
        "direccion": "—",
        "riesgo": "N/A",
        "premium_zone": poi_txt,   # texto low–high 61.8–88.6
        "zona_reaccion": "—",      # punto o rango mostrado en señales
        "sl": "—",
        "tp1_rr": "—",
        "tp2_rr": "—",
        "tp3_objetivo": "—",
        "contexto": "Esperando que el precio trabaje la zona premium H4 y un BOS claro en H1.",
    }

    if poi_h4 and p_lo is not None and p_hi is not None and kl_h1:
        # Dirección base del swing (aunque H4 esté en rango)
        if dir_h4 == "alcista":
            base_dir = "ALCISTA"
        elif dir_h4 == "bajista":
            base_dir = "BAJISTA"
        else:
            base_dir = "RANGO"

        # Caso 1: precio aún fuera de la zona premium H4
        if not in_premium:
            swing.update(
                {
                    "activo": False,
                    "direccion": base_dir,
                    "riesgo": "Medio" if base_dir != "RANGO" else "N/A",
                    "premium_zone": poi_txt,
                    "zona_reaccion": poi_txt,  # se muestra como zona de reacción en el panel
                    "sl": "—",
                    "tp1_rr": "—",
                    "tp2_rr": "—",
                    "tp3_objetivo": "—",
                    "contexto": (
                        "Precio fuera de la zona premium H4 (61.8–88.6). "
                        "Se espera que el precio ENTRE en esa banda para luego pedir "
                        "BOS + cierre de H1 a favor de la dirección superior."
                    ),
                }
            )
        else:
            # Caso 2: precio dentro de la zona premium H4
            highs_h1 = [k["high"] for k in kl_h1[-40:]]
            lows_h1 = [k["low"] for k in kl_h1[-40:]]
            if len(highs_h1) >= 2 and len(lows_h1) >= 2:
                prev_high_h1 = max(highs_h1[:-1])
                prev_low_h1 = min(lows_h1[:-1])

                if dir_h4 == "alcista":
                    entry = prev_high_h1
                    sl_val = prev_low_h1
                    tp3_val = h4_high
                    direccion_txt = "ALCISTA"
                elif dir_h4 == "bajista":
                    entry = prev_low_h1
                    sl_val = prev_high_h1
                    tp3_val = h4_low
                    direccion_txt = "BAJISTA"
                else:
                    # Si H4 está en rango, usamos la dirección de H1 como referencia
                    if dir_h1 == "alcista":
                        entry = prev_high_h1
                        sl_val = prev_low_h1
                        tp3_val = h4_high
                        direccion_txt = "ALCISTA"
                    elif dir_h1 == "bajista":
                        entry = prev_low_h1
                        sl_val = prev_high_h1
                        tp3_val = h4_low
                        direccion_txt = "BAJISTA"
                    else:
                        entry = prev_high_h1
                        sl_val = prev_low_h1
                        tp3_val = h4_high
                        direccion_txt = "RANGO"

                r = abs(entry - sl_val)
                if r > 0 and direccion_txt in ("ALCISTA", "BAJISTA"):
                    if direccion_txt == "ALCISTA":
                        tp1_val = entry + r
                        tp2_val = entry + 2 * r
                    else:
                        tp1_val = entry - r
                        tp2_val = entry - 2 * r
                    tp1_txt = f"{tp1_val:,.2f}"
                    tp2_txt = f"{tp2_val:,.2f}"
                else:
                    tp1_txt = "—"
                    tp2_txt = "—"

                zona_reac = f"{entry:,.2f}"
                sl_txt = f"{sl_val:,.2f}"
                tp3_txt = f"{tp3_val:,.2f}" if tp3_val is not None else "—"

                # BOS H1 en dirección de H4 para marcar ACTIVO
                bos_ok = False
                try:
                    bos_h1 = detectar_bos(kl_h1)
                    if dir_h4 in ("alcista", "bajista"):
                        bos_ok = bos_h1.get("bos") and (
                            (bos_h1.get("tipo") == "alcista" and dir_h4 == "alcista")
                            or (bos_h1.get("tipo") == "bajista" and dir_h4 == "bajista")
                        )
                except Exception:
                    bos_ok = False

                activo = bool(bos_ok and in_premium)

                if activo:
                    contexto_txt = (
                        "SWING ACTIVO: precio en zona premium H4 (61.8–88.6) y BOS de H1 "
                        "confirmado a favor de la dirección superior. TP1 1:1 (BE), "
                        "TP2 1:2 y TP3 en el alto/bajo operativo de H4."
                    )
                else:
                    contexto_txt = (
                        "Precio dentro de la zona premium H4, pero el swing sigue EN ESPERA "
                        "hasta que se confirme un BOS claro en H1 a favor de la estructura "
                        "de H4. Gestión propuesta: TP1 1:1 (BE), TP2 1:2 y TP3 en el "
                        "alto/bajo de H4."
                    )

                swing.update(
                    {
                        "activo": activo,
                        "direccion": direccion_txt,
                        "riesgo": "Medio" if direccion_txt != "RANGO" else "N/A",
                        "premium_zone": poi_txt,
                        "zona_reaccion": zona_reac,
                        "sl": sl_txt,
                        "tp1_rr": tp1_txt,
                        "tp2_rr": tp2_txt,
                        "tp3_objetivo": tp3_txt,
                        "contexto": contexto_txt,
                    }
                )

    # =========================================================
    # 🧭 ESTRUCTURA DETECTADA (para contexto detallado)
    # =========================================================
    estructura_detectada: Dict[str, Any] = {
        "H4": {
            "estado": dir_h4,  # "alcista" / "bajista" / "lateral"
            "RANGO_HIGH": round(h4_high, 2) if h4_high is not None else None,
            "RANGO_LOW": round(h4_low, 2) if h4_low is not None else None,
        },
        "H1": {
            "estado": dir_h1,
            "RANGO_HIGH": round(h1_high, 2) if h1_high is not None else None,
            "RANGO_LOW": round(h1_low, 2) if h1_low is not None else None,
        },
        "sesiones": ses_flags,
        "ventana_scalping_activa": bool(ventana_scalping),
    }

    # Aquí no usamos PDH/PDL/ASIA; solo marcamos la banda premium y flag
    zonas_detectadas: Dict[str, Any] = {
        "POI_H4": poi_txt,
        "EN_ZONA_PREMIUM": in_premium,
    }

    # Reflexión
    reflexion = random.choice(REFLEXIONES)

    # =========================================================
    # 📦 PAYLOAD FINAL TESLABTC.KG
    # =========================================================
    payload: Dict[str, Any] = {
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
