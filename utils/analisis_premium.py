from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3.1 PRO REAL MARKET)
# ============================================================
# Versión simplificada TESLABTC:
#   - Swing: estructura H4/H1 con zona premium H4 (61.8–88.6)
#   - Scalping: M5 en sesión NY, a favor y contra tendencia H1
#   - Sin zonas de liquidez antiguas, sólo acción del precio
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
    """
    Pivotes tipo ZigZag:
    - depth: pivote confirmado con 'depth' velas a cada lado
    - deviation: % mínimo de cambio desde el último pivote
    - backstep: si aparece pivote del mismo tipo muy cerca, se reemplaza por el más extremo
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
    """
    Tendencia estructural TESLABTC usando ZigZag:
    - Usa los últimos 2 HIGH y 2 LOW del zigzag.
    """
    piv = _zigzag_pivots(kl, depth=depth, deviation=deviation, backstep=backstep)
    if not kl or len(piv) < 3:
        return {"estado": "lateral", "BOS": "—"}

    highs = [(i, p) for (i, t, p) in piv if t == "H"]
    lows = [(i, p) for (i, t, p) in piv if t == "L"]

    # Pocos pivotes: inferimos sólo por el último tramo
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
    """
    Banda POI 61.8–88.6 del último impulso (H4):
    - En alcista: se mide desde el LOW al HIGH
    - En bajista: desde el HIGH al LOW
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
# 🔹 Sesiones (Asia, Londres, NY) + ventana SCALPING
# ------------------------------------------------------------
def _estado_sesiones() -> Tuple[str, Dict[str, bool]]:
    """
    Devuelve:
      - Texto de la sesión actual (NY, Londres, Asia o combinadas)
      - Flags booleanos por sesión: {"asia": bool, "londres": bool, "ny": bool}

    Horario de referencia Colombia:
      • ASIA:    17:00 – 02:00
      • LONDRES: 02:00 – 11:00
      • NY:      07:00 – 15:00

    🔵 MODO 24/7:
      - Si no cae en ninguna ventana exacta, se asigna por defecto a NY
        para mantener los análisis activos todo el tiempo.
    """
    ahora = datetime.now(TZ_COL)
    m = ahora.hour * 60 + ahora.minute  # minutos desde medianoche

    # Ventanas estándar
    asia = (m >= 17 * 60) or (m < 2 * 60)
    londres = 2 * 60 <= m < 11 * 60
    ny = 7 * 60 <= m < 15 * 60

    # Texto según combinaciones
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
        # 🔵 MODO BACKTEST 24/7:
        # Si no está en ninguna ventana exacta (p.ej. 15:00–17:00),
        # lo consideramos como sesión NY para efectos del análisis.
        sesion_txt = "Sesión NY (07:00–15:00 COL)"
        ny = True

    return sesion_txt, {"asia": asia, "londres": londres, "ny": ny}


def _ventana_scalping_ny() -> bool:
    """
    Ventana operativa original de SCALPING NY (primeras 2 horas).
    La dejamos disponible por si más adelante quieres limitarla otra vez.
    """
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
    """
    TP genérico: entrada ± (riesgo * RR).
    Se dejó por si en el futuro quieres reusarlo para variantes.
    """
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
      - Usa estructura H4/H1 para SWING
      - Usa M5 para señales SCALPING ligadas a H1
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

    # Estructura con ZigZag (dirección general)
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
    poi_h4 = _poi_fibo_band(dir_h4, h4_high, h4_low)
    poi_txt = "—"
    in_premium = False
    if poi_h4:
        p_lo, p_hi = sorted([float(poi_h4[0]), float(poi_h4[1])])
        poi_txt = f"{p_lo:,.2f}–{p_hi:,.2f} USD"
        if precio_num is not None and p_lo <= precio_num <= p_hi:
            in_premium = True

    # Sesiones globales (Asia / Londres / NY)
    sesion_txt, sesiones_flags = _estado_sesiones()
    ny_activa = bool(sesiones_flags.get("ny", False))

    # 🔵 MODO BACKTEST:
    # SCALPING activo durante toda la sesión NY
    ventana_scalping = ny_activa

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
        "contexto": "Fuera de ventana o sin dirección clara en H1.",
    }
    scalping_corr = dict(scalping_cont)

    if kl_m5 and ventana_scalping and dir_h1 in ("alcista", "bajista"):
        # Usamos el último HIGH/LOW operativos de M5 (ventana reciente)
        highs_m5 = [k["high"] for k in kl_m5[-30:]]
        lows_m5 = [k["low"] for k in kl_m5[-30:]]
        if len(highs_m5) >= 2 and len(lows_m5) >= 2:
            prev_high = max(highs_m5[:-1])
            prev_low = min(lows_m5[:-1])

            if dir_h1 == "alcista":
                # ✅ CONTINUACIÓN ALCISTA (a favor de H1)
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
                        "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                        "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                        "tp1_rr": (
                            f"{tp1_cont:,.2f} (1:1 • 50% + BE)"
                            if r_cont > 0
                            else "1:1 (50% + BE)"
                        ),
                        "tp2_rr": (
                            f"{tp2_cont:,.2f} (1:2 • 50%)"
                            if r_cont > 0
                            else "1:2 (50%)"
                        ),
                        "contexto": "Entrada SCALPING a favor de la estructura intradía H1.",
                    }
                )

                # 🔻 CORRECCIÓN BAJISTA (contra H1)
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
                        "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                        "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                        "tp1_rr": (
                            f"{tp1_corr:,.2f} (1:1 • 50% + BE)"
                            if r_corr > 0
                            else "1:1 (50% + BE)"
                        ),
                        "tp2_rr": (
                            f"{tp2_corr:,.2f} (1:2 • 50%)"
                            if r_corr > 0
                            else "1:2 (50%)"
                        ),
                        "contexto": "Entrada SCALPING de corrección intradía contra H1.",
                    }
                )
            else:
                # ✅ CONTINUACIÓN BAJISTA (a favor de H1)
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
                        "zona_reaccion": f"Ruptura del LOW M5 ≈ {prev_low:,.2f} USD",
                        "sl": f"HIGH M5 previo ≈ {prev_high:,.2f} USD",
                        "tp1_rr": (
                            f"{tp1_cont:,.2f} (1:1 • 50% + BE)"
                            if r_cont > 0
                            else "1:1 (50% + BE)"
                        ),
                        "tp2_rr": (
                            f"{tp2_cont:,.2f} (1:2 • 50%)"
                            if r_cont > 0
                            else "1:2 (50%)"
                        ),
                        "contexto": "Entrada SCALPING a favor de la estructura intradía H1.",
                    }
                )

                # 🔺 CORRECCIÓN ALCISTA (contra H1)
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
                        "zona_reaccion": f"Ruptura del HIGH M5 ≈ {prev_high:,.2f} USD",
                        "sl": f"LOW M5 previo ≈ {prev_low:,.2f} USD",
                        "tp1_rr": (
                            f"{tp1_corr:,.2f} (1:1 • 50% + BE)"
                            if r_corr > 0
                            else "1:1 (50% + BE)"
                        ),
                        "tp2_rr": (
                            f"{tp2_corr:,.2f} (1:2 • 50%)"
                            if r_corr > 0
                            else "1:2 (50%)"
                        ),
                        "contexto": "Entrada SCALPING de corrección intradía contra H1.",
                    }
                )

    # ============================
    # 🕰️ SWING (H4 + H1)
    # ============================
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
        "contexto": "Esperando alineación H4/H1 y BOS H1 en zona premium.",
    }

    # Condición mínima para mostrar escenario SWING:
    #   - H4 con tendencia clara
    #   - H1 a favor de H4
    #   - Precio dentro de la zona premium H4 (61.8–88.6)
    if kl_h1 and dir_h4 in ("alcista", "bajista") and dir_h1 == dir_h4 and precio_num is not None and in_premium:
        # Intentamos detectar si YA hubo BOS en H1 en la dirección de H4
        bos_h1 = detectar_bos(kl_h1)
        bos_ok = bos_h1.get("bos") and (
            (bos_h1.get("tipo") == "alcista" and dir_h4 == "alcista")
            or (bos_h1.get("tipo") == "bajista" and dir_h4 == "bajista")
        )

        highs_h1 = [k["high"] for k in kl_h1[-40:]]
        lows_h1 = [k["low"] for k in kl_h1[-40:]]

        if len(highs_h1) >= 2 and len(lows_h1) >= 2:
            prev_high_h1 = max(highs_h1[:-1])
            prev_low_h1 = min(lows_h1[:-1])

            # Definimos entrada / SL / objetivo H4 según dirección
            if dir_h4 == "alcista":
                entry = prev_high_h1           # nivel a quebrar y cerrar
                sl_val = prev_low_h1           # SL bajo el mínimo previo
                tp3_val = h4_high
                direccion_txt = "ALCISTA (a favor de H4)"
                # Cálculo de RR numérico
                r = abs(entry - sl_val)
                if r > 0:
                    tp1_val = entry + r
                    tp2_val = entry + 2 * r
                else:
                    tp1_val = tp2_val = entry
            else:  # dir_h4 == "bajista"
                entry = prev_low_h1           # nivel a quebrar y cerrar
                sl_val = prev_high_h1         # SL sobre el máximo previo
                tp3_val = h4_low
                direccion_txt = "BAJISTA (a favor de H4)"
                r = abs(entry - sl_val)
                if r > 0:
                    tp1_val = entry - r
                    tp2_val = entry - 2 * r
                else:
                    tp1_val = tp2_val = entry

            # Formateo de textos
            if r > 0:
                tp1_txt = f"{tp1_val:,.2f} (1:1 • BE)"
                tp2_txt = f"{tp2_val:,.2f} (1:2 • 50%)"
            else:
                tp1_txt = "1:1 (BE)"
                tp2_txt = "1:2 (50%)"

            zona_reac = f"Quiebre y cierre de {entry:,.2f} USD"
            sl_txt = f"{sl_val:,.2f} USD"
            tp3_txt = f"{tp3_val:,.2f} USD" if tp3_val is not None else "Alto/Bajo H4"

            # Si YA hubo BOS en H1 → ACTIVO, si no → EN ESPERA
            swing.update(
                {
                    "activo": bool(bos_ok),
                    "direccion": direccion_txt,
                    "riesgo": "Medio" if bos_ok else "Alto",
                    "premium_zone": poi_txt,
                    "zona_reaccion": zona_reac,
                    "sl": sl_txt,
                    "tp1_rr": tp1_txt,
                    "tp2_rr": tp2_txt,
                    "tp3_objetivo": tp3_txt,
                    "contexto": (
                        "Operación SWING siguiendo estructura H4: "
                        "BOS H1 ya confirmado en zona premium."
                        if bos_ok
                        else "Escenario SWING en zona premium H4: esperando quiebre y cierre de H1 en esa dirección."
                    ),
                }
            )

    # Reflexión
    reflexion = random.choice(REFLEXIONES)

    # Estructura / zonas mínimas (para compatibilidad con formatter)
    estructura_detectada = {
        "H4": dir_h4,
        "H1": dir_h1,
        "sesion_ny_activa": ny_activa,
        "ventana_scalping_ny": bool(ventana_scalping),
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
