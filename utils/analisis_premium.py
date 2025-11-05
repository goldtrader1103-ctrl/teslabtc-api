# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium
# Archivo: utils/analisis_premium.py
# Compatible con bot TESLABOT.KG (clave de payload: "🧠 TESLABTC.KG")
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import math
import random

# ------------------------------------------------------------
# Imports con tolerancia (nombres antiguos y nuevos)
# ------------------------------------------------------------
try:
    from utils.time_utils import now_col
except Exception:
    from datetime import timezone
    def now_col() -> datetime:
        # COL ~ UTC-5 sin DST
        return datetime.utcnow() - timedelta(hours=5)

# liquidez: soporta nombres viejos y nuevos
try:
    from utils.liquidez import rango_asiatico_hilo as _asian_range_fn
except Exception:
    _asian_range_fn = None

try:
    from utils.liquidez import rango_dia_previo_hilo as _pdh_pdl_fn
except Exception:
    _pdh_pdl_fn = None

# estructura (si existe mejor; si no, usamos fallback local simple)
try:
    from utils.estructura import (
        swing_high_low_multitf as _swing_multi,
    )
except Exception:
    _swing_multi = None

# precio y klines
_price_getters: List[Tuple[str, str]] = [
    ("utils.price_utils", "obtener_precio"),  # ✅ tu función real
]
_klines_getters: List[Tuple[str, str]] = [
    ("utils.price_utils", "obtener_klines_binance"),  # ✅ tu función real
]

def _import_callable(mod: str, fn: str):
    try:
        import importlib
        m = importlib.import_module(mod)
        f = getattr(m, fn, None)
        return f if callable(f) else None
    except Exception:
        return None

def _safe_get_price(symbol: str) -> Tuple[Optional[float], str]:
    """
    Intenta múltiples proveedores. Devuelve (precio, fuente_texto).
    Compatible con dict {'precio': x, 'fuente': y}.
    """
    from datetime import datetime

    for mod, fn in _price_getters:
        f = _import_callable(mod, fn)
        if f:
            try:
                px = f(symbol)

                # ✅ Si devuelve dict {'precio': float, 'fuente': str}
                if isinstance(px, dict):
                    val = px.get("precio")
                    src = px.get("fuente", "Binance (REST)")
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Precio obtenido: {val} desde {src}")
                    return float(val) if val is not None else None, src

                # ✅ Si devuelve tuple o lista (precio, fuente)
                elif isinstance(px, (list, tuple)) and len(px) >= 1:
                    val = float(px[0])
                    src = str(px[1]) if len(px) > 1 else "Binance (REST)"
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Precio obtenido: {val} desde {src}")
                    return val, src

                # ✅ Si devuelve float directamente
                elif isinstance(px, (int, float)):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Precio directo: {px} desde Binance REST")
                    return float(px), "Binance (REST)"

            except Exception as e:
                print(f"[ERROR safe_get_price] {e}")
                pass

    # ❌ Si nada responde
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Fallback: fuente no disponible")
    return None, "Fuente no disponible"



def _safe_get_klines(symbol: str, interval: str, lookback: int = 500) -> List[Dict[str, Any]]:
    """
    Pide OHLC/klines. Normaliza a:
    [{open_time: datetime (tz-aware o naive), open, high, low, close}]
    """
    for mod, fn in _klines_getters:
        f = _import_callable(mod, fn)
        if f:
            try:
                data = f(symbol, interval=interval, limit=lookback)
                # Normalización común
                norm: List[Dict[str, Any]] = []
                for k in data or []:
                    # Admite dict o lista estilo binance
                    if isinstance(k, dict):
                        t = k.get("open_time") or k.get("t")
                        if isinstance(t, (int, float)):
                            ot = datetime.utcfromtimestamp(t/1000.0)
                        else:
                            ot = t if isinstance(t, datetime) else now_col()
                        norm.append({
                            "open_time": ot,
                            "open": float(k.get("open", k.get("o", 0.0))),
                            "high": float(k.get("high", k.get("h", 0.0))),
                            "low":  float(k.get("low",  k.get("l", 0.0))),
                            "close":float(k.get("close",k.get("c", 0.0))),
                        })
                    elif isinstance(k, (list, tuple)) and len(k) >= 5:
                        # [open_time(ms), open, high, low, close, ...]
                        ot = datetime.utcfromtimestamp(float(k[0])/1000.0)
                        norm.append({
                            "open_time": ot,
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low":  float(k[3]),
                            "close":float(k[4]),
                        })
                if norm:
                    return norm
            except Exception:
                pass
    return []

# ------------------------------------------------------------
# Utilidades locales para estructura (fallback)
# ------------------------------------------------------------
@dataclass
class Rango:
    high: Optional[float]
    low: Optional[float]

def _calc_range(kl: List[Dict[str, Any]]) -> Rango:
    hi, lo = None, None
    for k in kl:
        h = float(k["high"]); l = float(k["low"])
        hi = h if hi is None else max(hi, h)
        lo = l if lo is None else min(lo, l)
    return Rango(hi, lo)

def _swings_simple(kl: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fallback: detecta último HH/HL/LH/LL por pivotes simples.
    Es solo un respaldo si no existe la librería de estructura.
    """
    if len(kl) < 5:
        return {"estado": "lateral", "HH": None, "HL": None, "LH": None, "LL": None}

    def is_pivot_high(i):
        return kl[i]["high"] > kl[i-1]["high"] and kl[i]["high"] > kl[i+1]["high"]

    def is_pivot_low(i):
        return kl[i]["low"] < kl[i-1]["low"] and kl[i]["low"] < kl[i+1]["low"]

    piv_hi = [kl[i]["high"] for i in range(1, len(kl)-1) if is_pivot_high(i)]
    piv_lo = [kl[i]["low"]  for i in range(1, len(kl)-1) if is_pivot_low(i)]

    HH = max(piv_hi) if piv_hi else None
    LL = min(piv_lo) if piv_lo else None

    estado = "lateral"
    if HH and LL:
        # tendencia por último cierre vs medias de pivotes, muy simple
        last = kl[-1]["close"]
        if last > (HH + LL)/2:
            estado = "alcista"
        elif last < (HH + LL)/2:
            estado = "bajista"

    return {"estado": estado, "HH": HH, "LL": LL, "HL": None, "LH": None}

# ------------------------------------------------------------
# Cálculos de rangos especiales solicitados
# ------------------------------------------------------------
def _asian_range(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """
    Rango Asiático COL: 17:00 → 02:00 (día siguiente)
    """
    if _asian_range_fn:
        try:
            r = _asian_range_fn(kl_15m)
            if r:
                return {"ASIAN_HIGH": float(r.get("ASIAN_HIGH")), "ASIAN_LOW": float(r.get("ASIAN_LOW"))}
        except Exception:
            pass

    # Fallback local
    if not kl_15m:
        return None

    ref = now_col()
    start = ref.replace(hour=17, minute=0, second=0, microsecond=0)
    end = (ref + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)

    hi, lo = None, None
    for k in kl_15m:
        t = k["open_time"]
        if start <= t <= end:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)

    if hi is None or lo is None:
        return None
    return {"ASIAN_HIGH": hi, "ASIAN_LOW": lo}

def _pdh_pdl(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """
    Día previo (COL): 19:00 → 19:00
    """
    if _pdh_pdl_fn:
        try:
            r = _pdh_pdl_fn(kl_15m)
            if r:
                return {"PDH": float(r.get("PDH")), "PDL": float(r.get("PDL"))}
        except Exception:
            pass

    if not kl_15m:
        return None

    ref = now_col()
    end = ref.replace(hour=19, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)

    hi, lo = None, None
    for k in kl_15m:
        t = k["open_time"]
        if start <= t < end:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)

    if hi is None or lo is None:
        return None
    return {"PDH": hi, "PDL": lo}

# ------------------------------------------------------------
# Confirmaciones (booleans) y escenarios
# ------------------------------------------------------------
def _confirmaciones(
    precio: float,
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    tf_d: Dict[str, Any],
    tf_h4: Dict[str, Any],
    tf_h1: Dict[str, Any],
) -> Dict[str, str]:
    """
    Construye checklist de confirmaciones ✅/❌ (texto).
    Reglas simples pero coherentes con la guía de la usuaria.
    """
    checks: Dict[str, bool] = {}

    # Tendencia externa H1 y macro D
    tendencia_h1 = tf_h1.get("estado")
    tendencia_d  = tf_d.get("estado")
    checks["Tendencia macro (D)"] = (tendencia_d == "alcista" or tendencia_d == "bajista")
    checks["Tendencia intradía (H1)"] = (tendencia_h1 == "alcista" or tendencia_h1 == "bajista")

    # Barridas de liquidez Asia/PDH/PDL (interpretación contraria)
    if pd:
        pdh, pdl = pd.get("PDH"), pd.get("PDL")
        if pdh and precio > pdh:
            checks["Barrida PDH"] = True
        if pdl and precio < pdl:
            checks["Barrida PDL"] = True

    if asian:
        ah, al = asian.get("ASIAN_HIGH"), asian.get("ASIAN_LOW")
        if ah and precio > ah:
            checks["Barrida Alto Asia"] = True
        if al and precio < al:
            checks["Barrida Bajo Asia"] = True

    # OB/POI/Oferta-Demanda (placeholders: dependen de módulos específicos).
    # Los marcamos como “pendiente” para no mentir si no tenemos detector.
    # Si tienes detectores, puedes mapearlos aquí y devolver True/False real.
    checks["OB válido en H1/H15"] = False
    checks["POI alineado con tendencia"] = False
    checks["Zona de Oferta/Demanda profunda"] = False

    # Formateo ✅/❌/➖
    out: Dict[str, str] = {}
    for k, v in checks.items():
        mark = "✅" if v else "❌" if v is False else "➖"
        out[k] = mark
    return out

def _escenarios(
    precio: float,
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    tf_d: Dict[str, Any],
    tf_h4: Dict[str, Any],
    tf_h1: Dict[str, Any],
) -> Tuple[str, str, str]:
    """
    Devuelve (setup_texto, escenario1, escenario2)
    - Si hay barrida de PDL → sesgo compra (ir a extremos contrarios)
    - Si hay barrida de PDH → sesgo venta
    - Asia actúa parecido.
    SL: alto/bajo previo
    TP1=1:1, TP2=1:2; TP3 sugerencia
    """
    sesgo = None
    comentario = []

    if pd:
        pdh, pdl = pd.get("PDH"), pd.get("PDL")
        if pdl and precio < pdl:
            sesgo = "Compra"
            comentario.append("🧲 Barrida del PDL sugiere búsqueda de liquidez superior (hacia PDH).")
        if pdh and precio > pdh:
            sesgo = "Venta"
            comentario.append("🧲 Barrida del PDH sugiere búsqueda de liquidez inferior (hacia PDL).")

    if not sesgo and asian:
        ah, al = asian.get("ASIAN_HIGH"), asian.get("ASIAN_LOW")
        if al and precio < al:
            sesgo = "Compra"
            comentario.append("🧲 Barrida del Bajo Asiático sugiere desplazamiento hacia el Alto Asiático.")
        if ah and precio > ah:
            sesgo = "Venta"
            comentario.append("🧲 Barrida del Alto Asiático sugiere desplazamiento hacia el Bajo Asiático.")

    if not sesgo:
        # usa tendencia H1 como desempate
        t = tf_h1.get("estado")
        if t == "alcista":
            sesgo = "Compra"
            comentario.append("📈 Tendencia interna H1 alcista.")
        elif t == "bajista":
            sesgo = "Venta"
            comentario.append("📉 Tendencia interna H1 bajista.")
        else:
            sesgo = "Neutro"
            comentario.append("➖ Estructura H1 lateral; esperar confirmación (BOS/CHoCH).")

    # Setup y TPs (conceptuales; la entrada exacta requiere BOS)
    pe = "Zona de Entrada: esperar BOS en M15/M5 dentro del POI."
    sl = "SL: por detrás del alto/bajo anterior de la zona de entrada."
    tp1 = "TP1: 1:1 (mueva a BE y tome parciales 50%)."
    tp2 = "TP2: 1:2 (cierre recomendado)."
    tp3 = "TP3+: proyección opcional 1:3, 1:4… si la estructura respalda continuación."
    setup = f"{pe}\n{sl}\n{tp1}\n{tp2}\n{tp3}"

    # Escenario 1 (Alta prob.) vs Escenario 2 (Media) según alineación con H1 y D
    alta = []
    media = []

    if sesgo == "Compra":
        alta.append("🟢 *Compra* hacia zonas de liquidez superiores (PDH / Alto Asia / HH previos).")
        media.append("🟡 *Compra* condicionada: si hay debilidad en POI o volumen insuficiente, esperar nuevo BOS.")
    elif sesgo == "Venta":
        alta.append("🔴 *Venta* hacia zonas de liquidez inferiores (PDL / Bajo Asia / LL previos).")
        media.append("🟡 *Venta* condicionada: si falta confirmación (BOS/volumen), esperar retesteo.")
    else:
        alta.append("🟡 *Neutro*: esperar BOS claro en zona marcada para definir dirección.")
        media.append("⚪ *Lateral*: operar sólo con confluencias fuertes y gestión estricta.")

    # contexto breve
    ctx = " | ".join(comentario) if comentario else "Contexto: estructura sin sesgo claro."

    esc1 = f"{alta[0]}\n{ctx}\n\n{setup}"
    esc2 = f"{media[0]}\n{ctx}\n\n{setup}"
    conclusion = "Operar sólo si *todas* las confirmaciones críticas están alineadas (BOS + POI + Sesión NY)."

    return esc1, esc2, conclusion

# ------------------------------------------------------------
# Formato de salida Premium
# ------------------------------------------------------------
def _fmt_zonas(
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    d_rng: Rango,
    h4_rng: Rango,
    h1_rng: Rango,
) -> Dict[str, Any]:
    zonas: Dict[str, Any] = {}

    if pd:
        zonas["PDH"] = round(float(pd.get("PDH")), 2)
        zonas["PDL"] = round(float(pd.get("PDL")), 2)

    if asian:
        zonas["ASIAN_HIGH"] = round(float(asian.get("ASIAN_HIGH")), 2)
        zonas["ASIAN_LOW"]  = round(float(asian.get("ASIAN_LOW")), 2)

    if d_rng.high and d_rng.low:
        zonas["D_HIGH"] = round(d_rng.high, 2)
        zonas["D_LOW"]  = round(d_rng.low, 2)
    if h4_rng.high and h4_rng.low:
        zonas["H4_HIGH"] = round(h4_rng.high, 2)
        zonas["H4_LOW"]  = round(h4_rng.low, 2)
    if h1_rng.high and h1_rng.low:
        zonas["H1_HIGH"] = round(h1_rng.high, 2)
        zonas["H1_LOW"]  = round(h1_rng.low, 2)

    # Sitio para añadir: OB, POI, oferta/demanda profundas (si tus detectores los entregan).
    return zonas or {"info": "Sin zonas detectadas"}

# ------------------------------------------------------------
# Sesión NY (abierta/cerrada)
# ------------------------------------------------------------
def _estado_sesion_ny() -> str:
    ahora = now_col()
    # Sesión NY aprox 08:30–16:00 COL (ajústalo si usas otro horario)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end   = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    if start <= ahora <= end:
        return "🟢 Abierta (NY)"
    return "❌ Cerrada (Fuera de NY)"

# ------------------------------------------------------------
# PÚBLICA: generar_analisis_premium
# ------------------------------------------------------------
def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    """
    Genera el payload Premium con emojis y bloques:
    - fecha, sesión, precio_actual, fuente_precio
    - zonas (PDH/PDL, Asia, rangos D/H4/H1)
    - confirmaciones ✅/❌
    - setup + Escenario 1/2 + conclusión
    """
    now = now_col()
    fecha_txt = now.strftime("%d/%m/%Y %H:%M:%S")

    precio, fuente = _safe_get_price(symbol)
    precio_txt = f"{precio:,.2f} USD" if isinstance(precio, (int, float)) else "—"

    # Klines para cálculos (M15 para Asia/PD y rangos básicos multi-TF)
    kl_15m = _safe_get_klines(symbol, "15m", 600)
    kl_h1  = _safe_get_klines(symbol, "1h",  600)
    kl_h4  = _safe_get_klines(symbol, "4h",  600)
    kl_d   = _safe_get_klines(symbol, "1d",  400)

    # Rangos especiales
    asian = _asian_range(kl_15m)
    pd    = _pdh_pdl(kl_15m)

    # Rangos por TF (estructura real ≠ número fijo de velas; usamos todo el set disponible)
    d_rng  = _calc_range(kl_d)  if kl_d  else Rango(None, None)
    h4_rng = _calc_range(kl_h4) if kl_h4 else Rango(None, None)
    h1_rng = _calc_range(kl_h1) if kl_h1 else Rango(None, None)

    # Estado (alcista/bajista/lateral) por TF (fallback simple si no hay detector)
    if _swing_multi:
        try:
            tf_d  = _swing_multi(kl_d)  if kl_d  else {"estado":"lateral"}
            tf_h4 = _swing_multi(kl_h4) if kl_h4 else {"estado":"lateral"}
            tf_h1 = _swing_multi(kl_h1) if kl_h1 else {"estado":"lateral"}
        except Exception:
            tf_d  = _swings_simple(kl_d)  if kl_d  else {"estado":"lateral"}
            tf_h4 = _swings_simple(kl_h4) if kl_h4 else {"estado":"lateral"}
            tf_h1 = _swings_simple(kl_h1) if kl_h1 else {"estado":"lateral"}
    else:
        tf_d  = _swings_simple(kl_d)  if kl_d  else {"estado":"lateral"}
        tf_h4 = _swings_simple(kl_h4) if kl_h4 else {"estado":"lateral"}
        tf_h1 = _swings_simple(kl_h1) if kl_h1 else {"estado":"lateral"}

    # Confirmaciones y escenarios
    conf = _confirmaciones(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h4, tf_h1
    )
    esc1, esc2, concl = _escenarios(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h4, tf_h1
    )

    # Zonas
    zonas = _fmt_zonas(asian, pd, d_rng, h4_rng, h1_rng)

    # Mensajería de conexión/precio
    conexion = f"🦎 Fallback CoinGecko activo" if "gecko" in fuente.lower() else f"📡 {fuente} activo"

    payload = {
        "fecha": fecha_txt,
        "nivel_usuario": "Premium",
        "sesión": _estado_sesion_ny(),
        "precio_actual": precio_txt,
        "fuente_precio": fuente,
        "conexion_binance": conexion,

        # Bloques Premium
        "zonas": zonas,
        "confirmaciones": conf,
        "setup": "⏳ En espera de setup válido" if "❌" in "".join(conf.values()) else "✅ Setup candidato (revisar BOS/volumen)",
        "escenario_1": esc1,
        "escenario_2": esc2,
        "conclusion": concl,

        # Metadatos
        "simbolo": symbol,
        "temporalidades": ["D","H4","H1","M15"]
    }

    # Envoltorio de API (clave compatible con el bot)
    return {
        "🧠 TESLABTC.KG": payload
    }
