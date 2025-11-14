from main import VERSION_TESLA
# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.3 PRO REAL MARKET)
# ============================================================
# Fuente: Binance (REST) — sin simulaciones
# Estructura real multi-TF, PDH/PDL, Rango Asiático (COL), OB/POI cercanos,
# escenarios de continuidad/corrección y SETUP ACTIVO “Level Entry M5”.
# Compatible con utils/intelligent_formatter v5.3 PRO.
# ============================================================

import requests, math, random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

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
            headers=UA, timeout=6
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
            headers=UA, timeout=8
        )
        r.raise_for_status()
        data = r.json()
        out: List[Dict[str, Any]] = []
        for k in data:
            out.append({
                "open_time": datetime.utcfromtimestamp(k[0] / 1000.0),
                "open": float(k[1]),
                "high": float(k[2]),
                "low":  float(k[3]),
                "close":float(k[4]),
                "vol":  float(k[5]),
            })
        return out
    except Exception:
        return []

# ------------------------------------------------------------
# 🔹 Pivotes y tendencia (HH/HL vs LH/LL coherente)
# ------------------------------------------------------------
def _pivotes(kl: List[Dict[str, Any]], look: int = 2) -> Tuple[List[int], List[int]]:
    if not kl or len(kl) < (look * 2 + 1):
        return [], []
    hi_idx, lo_idx = [], []
    for i in range(look, len(kl) - look):
        h = kl[i]["high"]; l = kl[i]["low"]
        if all(h > kl[i-j]["high"] for j in range(1, look+1)) and all(h > kl[i+j]["high"] for j in range(1, look+1)):
            hi_idx.append(i)
        if all(l < kl[i-j]["low"]  for j in range(1, look+1)) and all(l < kl[i+j]["low"]  for j in range(1, look+1)):
            lo_idx.append(i)
    return hi_idx, lo_idx

def _detectar_tendencia(kl: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Devuelve dict con:
    - estado: 'alcista'/'bajista'/'lateral'
    - BOS: '✔️' o '—'
    - HH/LH/LL/HL: últimos pivotes (para coherencia visual)
    - pair: cuál par mostrar en UI (HH/HL si alcista, LH/LL si bajista)
    """
    if not kl or len(kl) < 15:
        return {"estado": "lateral", "BOS": "—"}

    hi_idx, lo_idx = _pivotes(kl)
    if len(hi_idx) < 2 or len(lo_idx) < 2:
        # Aún así regresamos últimos valores si existen para que la UI no quede vacía
        try:
            last_hi = kl[hi_idx[-1]]["high"] if hi_idx else None
            prev_hi = kl[hi_idx[-2]]["high"] if len(hi_idx) > 1 else None
            last_lo = kl[lo_idx[-1]]["low"]  if lo_idx else None
            prev_lo = kl[lo_idx[-2]]["low"]  if len(lo_idx) > 1 else None
        except Exception:
            last_hi = prev_hi = last_lo = prev_lo = None
        return {
            "estado": "lateral", "BOS": "—",
            "HH": last_hi, "LH": prev_hi, "LL": last_lo, "HL": prev_lo, "pair": "HH/LL"
        }

    hh = kl[hi_idx[-1]]["high"]; lh = kl[hi_idx[-2]]["high"]
    ll = kl[lo_idx[-1]]["low"];  hl = kl[lo_idx[-2]]["low"]

    if hh > lh and ll > hl:
        return {"estado": "alcista", "BOS": "✔️", "HH": hh, "LH": lh, "LL": ll, "HL": hl, "pair": "HH/HL"}
    if hh < lh and ll < hl:
        return {"estado": "bajista", "BOS": "✔️", "HH": hh, "LH": lh, "LL": ll, "HL": hl, "pair": "LH/LL"}
    return {"estado": "lateral", "BOS": "—", "HH": hh, "LH": lh, "LL": ll, "HL": hl, "pair": "HH/LL"}

# ------------------------------------------------------------
# 🔹 Rangos reales por horario Colombia (PDH/PDL & Asia)
# ------------------------------------------------------------
import pytz
def _pdh_pdl(kl_15m):
    """Día previo cerrado COL: 7PM anteayer → 7PM ayer (America/Bogota)"""
    if not kl_15m:
        return None
    tz_col = pytz.timezone("America/Bogota")
    ahora = datetime.now(tz_col)
    fin_dia = (ahora.replace(hour=19, minute=0, second=0, microsecond=0)
               if ahora.hour >= 19 else
               (ahora - timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0))
    inicio_dia = fin_dia - timedelta(hours=24)
    hi, lo = None, None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(tz_col)
        if inicio_dia <= t_col < fin_dia:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)
    if hi is None or lo is None:
        return None
    return {"PDH": round(hi, 2), "PDL": round(lo, 2)}

def _asian_range(kl_15m):
    """Sesión Asiática COL: 5PM → 2AM (America/Bogota) del ciclo operativo actual"""
    if not kl_15m:
        return None
    tz_col = pytz.timezone("America/Bogota")
    ahora = datetime.now(tz_col)
    ref_dia = (ahora - timedelta(days=1)) if ahora.hour < 2 else ahora
    inicio_asia = ref_dia.replace(hour=17, minute=0, second=0, microsecond=0)
    fin_asia = (inicio_asia + timedelta(hours=9))
    hi, lo = None, None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(tz_col)
        if inicio_asia <= t_col < fin_asia:
            h = float(k["high"]); l = float(k["low"])
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
            confs["Barrida Asia (HIGH)"] = "⚠️ Alto asiático eliminado — vigilar rechazo."
        elif precio < float(asian.get("ASIAN_LOW", 0)):
            confs["Barrida Asia (LOW)"] = "⚠️ Bajo asiático eliminado — vigilar rebote."
        else:
            confs["Rango Asia"] = "➖ Dentro del rango asiático."

    # OB válido (interpretativo simple por estado H1)
    confs["OB válido H1/H15"] = (
        "✅ En zona relevante — posible confirmación."
        if tf_h1.get("estado") in ("alcista", "bajista") else "➖ No confirmado."
    )

    return confs

# ------------------------------------------------------------
# 🔹 Escenarios + Setup
# ------------------------------------------------------------
def _probabilidad_por_confs(confs: Dict[str, str]) -> str:
    checks = sum(1 for v in confs.values() if v.startswith("✅"))
    if checks >= 4: return "Alta"
    if checks >= 2: return "Media"
    return "Baja"

def _riesgo(prob: str) -> str:
    return "Bajo" if prob == "Alta" else ("Medio" if prob == "Media" else "Alto")

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
    if t_h1 == "alcista":
        tipo_favor, tipo_contra = "Compra", "Venta"
    elif t_h1 == "bajista":
        tipo_favor, tipo_contra = "Venta", "Compra"
    else:
        tipo_favor, tipo_contra = "Neutro", "Neutro"

    contexto: List[str] = []
    if isinstance(precio, (int, float)) and pd:
        if pd.get("PDL") and precio < float(pd["PDL"]):
            contexto.append("🧲 Barrida del PDL → búsqueda de PDH.")
        if pd.get("PDH") and precio > float(pd["PDH"]):
            contexto.append("🧲 Barrida del PDH → búsqueda de PDL.")
    if isinstance(precio, (int, float)) and asian:
        if asian.get("ASIAN_LOW") and precio < float(asian["ASIAN_LOW"]):
            contexto.append("🧲 Barrida del Bajo Asiático → buscar Alto Asiático.")
        if asian.get("ASIAN_HIGH") and precio > float(asian["ASIAN_HIGH"]):
            contexto.append("🧲 Barrida del Alto Asiático → buscar Bajo Asiático.")

    if t_h1 == "alcista": contexto.append("📈 H1 alcista (sesgo comprador).")
    elif t_h1 == "bajista": contexto.append("📉 H1 bajista (sesgo vendedor).")
    else: contexto.append("➖ H1 lateral: esperar BOS/CHoCH.")

    contexto_txt = " | ".join(contexto) if contexto else "Contexto neutro."

    prob_favor = _probabilidad_por_confs(confs)
    prob_contra = "Media" if prob_favor == "Alta" else ("Baja" if prob_favor == "Media" else "Baja")

    def build_setup(prob: str, tipo: str) -> Tuple[str, Dict[str, str]]:
        tiene_setup = (prob in ("Alta", "Media")) and tipo in ("Compra", "Venta") and t_h1 in ("alcista", "bajista")
        if tiene_setup:
            return "✅ Setup candidato", {
                "zona_entrada": "Esperar BOS en M15/M5 dentro del POI.",
                "sl": "Alto/bajo anterior de la zona de entrada.",
                "tp1": "1:1 (mueva a BE y tome parciales)",
                "tp2": "1:2 (recoja sus ganancias)",
                "tp3": "1:3+ (si la estructura lo respalda)",
                "observacion": "Prioridad 1:2; TP3+ sólo con fortaleza clara.",
            }
        else:
            return "⏳ Sin setup válido. Intenta en unos minutos.", {}

    setup_estado_favor, setup_favor = build_setup(prob_favor, tipo_favor)
    setup_estado_contra, setup_contra = build_setup(prob_contra, tipo_contra)

    def texto_esc(tipo: str) -> str:
        if tipo == "Compra":
            return "Continuación: objetivos en PDH / ASIAN HIGH / HH. Entrada tras BOS alcista M15."
        if tipo == "Venta":
            return "Continuación: objetivos en PDL / ASIAN LOW / LL. Entrada tras BOS bajista M15."
        return "Neutro: esperar BOS claro en zona marcada."

    # Escenario 1: Continuidad (a favor de H1)
    escenario_1 = {
        "tipo": tipo_favor,
        "probabilidad": prob_favor,
        "riesgo": _riesgo(prob_favor),
        "contexto": contexto_txt,
        "confirmaciones": confs,
        "setup_estado": setup_estado_favor,
        "setup": setup_favor,
        "texto": texto_esc(tipo_favor),
    }
    # Escenario 2: Corrección (contra H1)
    escenario_2 = {
        "tipo": tipo_contra,
        "probabilidad": prob_contra,
        "riesgo": _riesgo(prob_contra),
        "contexto": contexto_txt,
        "confirmaciones": confs,
        "setup_estado": setup_estado_contra,
        "setup": setup_contra,
        "texto": texto_esc(tipo_contra),
    }

    conclusion = (
        "Operar sólo cuando *todas* las confirmaciones críticas se alineen (BOS + POI + Sesión NY). "
        "Si el setup no es válido, vuelve a intentar en unos minutos."
    )
    return escenario_1, escenario_2, conclusion

# ------------------------------------------------------------
# 🔹 Sesión NY + Reflexiones base (fallback)
# ------------------------------------------------------------
def _estado_sesion_ny() -> Tuple[str, bool]:
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end   = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    activa = start <= ahora <= end
    return ("✅ Activa (Sesión NY)" if activa else "❌ Cerrada (Fuera de NY)"), activa

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
def _setup_activo_m5(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    kl_m15 = _safe_get_klines(symbol, "15m", 200)
    kl_m5  = _safe_get_klines(symbol, "5m",  200)
    if not kl_m15 or not kl_m5:
        return {"activo": False}

    tf_m15 = _detectar_tendencia(kl_m15)
    tf_m5  = _detectar_tendencia(kl_m5)

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
                "contexto": f"Confirmación BOS {tipo.lower()} M15 + M5 con volumen sobre promedio.",
                "zona_entrada": f"{min(zona_a, zona_b):,.2f}–{max(zona_a, zona_b):,.2f}",
                "sl": f"{(ultimo['low'] if tipo=='Compra' else ultimo['high']):,.2f}",
                "tp1": f"{(ce*1.01 if tipo=='Compra' else ce*0.99):,.2f} (1:2)",
                "tp2": f"{(ce*1.02 if tipo=='Compra' else ce*0.98):,.2f} (1:3)",
                "comentario": f"Cumple estructura TESLABTC: BOS + Mitigación + Confirmación ({tipo})."
            }
    return {"activo": False}

# ------------------------------------------------------------
# 🔹 Zonas para mostrar (PDH/PDL, Asia, rangos TF) + OB/POI
# ------------------------------------------------------------
def _calc_range(kl: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
    if not kl:
        return None, None
    hi = max(k["high"] for k in kl)
    lo = min(k["low"]  for k in kl)
    return hi, lo

def _fmt_zonas(
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
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
        zonas["ASIAN_LOW"]  = round(float(asian.get("ASIAN_LOW")),  2)

    d_hi, d_lo = _calc_range(d_kl);   h4_hi, h4_lo = _calc_range(h4_kl);   h1_hi, h1_lo = _calc_range(h1_kl)
    if d_hi and d_lo:   zonas["D_HIGH"], zonas["D_LOW"]   = round(d_hi,2), round(d_lo,2)
    if h4_hi and h4_lo: zonas["H4_HIGH"], zonas["H4_LOW"] = round(h4_hi,2), round(h4_lo,2)
    if h1_hi and h1_lo: zonas["H1_HIGH"], zonas["H1_LOW"] = round(h1_hi,2), round(h1_lo,2)

    return zonas or {"info": "Sin zonas detectadas"}

# 💎 Integración con OB Detector (opcional)
def _detectar_ob_poi_cercanos(symbol: str = "BTCUSDT", limite=2) -> dict:
    try:
        from utils.ob_detector import detectar_ob_poi
        resultado = detectar_ob_poi(symbol, limite)
        return resultado if isinstance(resultado, dict) else {}
    except Exception as e:
        print(f"⚠️ No se pudo cargar OB Detector: {e}")
        return {}

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
    kl_h1  = _safe_get_klines(symbol, "1h", 600)
    kl_h4  = _safe_get_klines(symbol, "4h", 600)
    kl_d   = _safe_get_klines(symbol, "1d", 400)

    tf_d   = _detectar_tendencia(kl_d)
    tf_h4  = _detectar_tendencia(kl_h4)
    tf_h1  = _detectar_tendencia(kl_h1)
    tf_m15 = _detectar_tendencia(kl_15m)

    asian = _asian_range(kl_15m)
    pd    = _pdh_pdl(kl_15m)
    sesion_txt, sesion_activa = _estado_sesion_ny()

    # 🔹 Confirmaciones con contexto
    conf = _confirmaciones(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h1, sesion_activa
    )

    # 🔹 Dirección general (texto auxiliar)
    tendencia_d  = tf_d.get("estado", "—")
    tendencia_h4 = tf_h4.get("estado", "—")
    tendencia_h1 = tf_h1.get("estado", "—")
    direccion_general = (
        "🟢 Alcista" if tendencia_h4 == "alcista"
        else "🔴 Bajista" if tendencia_h4 == "bajista"
        else "⚪ Lateral"
    )
    estructura_txt = f"D: {tendencia_d.upper()} | H4: {tendencia_h4.upper()} | H1: {tendencia_h1.upper()}"

    # 🔹 Interpretación macro (para UI)
    contexto = interpretar_contexto(tf_d, tf_h4, tf_h1, conf, asian or {})

    # 🔹 Escenarios (continuidad y corrección)
    esc1, esc2, concl = _escenarios(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h4, tf_h1, conf
    )

    # 🔹 Setup activo M5
    setup_activo = _setup_activo_m5(symbol)

    # 🔹 Zonas (PDH/PDL, Asia, rangos) + OB/POI cercanos
    zonas = _fmt_zonas(asian, pd, kl_d, kl_h4, kl_h1)
    ob_poi = _detectar_ob_poi_cercanos(symbol)
    if ob_poi:
        zonas.update(ob_poi)  # Espera keys como "OB_H4", "POI_H1", etc.

    # 🔹 Reflexión (si el formatter no recibe una, él randomiza)
    reflexion = random.choice(REFLEXIONES)

    slogan = "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"

    # 🔹 Conclusión operativa (separada del bloque Setup)
    if setup_activo.get("activo"):
        conclusion_final = (
            "Estructura y volumen alineados intradía. Priorizar la ejecución del Setup activo "
            "respetando gestión 1:2 y mover a BE en 1:1 + 50%."
        )
    elif sesion_activa and tendencia_h4 == "bajista" and tendencia_h1 == "bajista":
        conclusion_final = "Estructura bajista consolidada: priorizar ventas tras retrocesos a oferta válida."
    elif sesion_activa and tendencia_h4 == "alcista" and tendencia_h1 == "alcista":
        conclusion_final = "Estructura alcista confirmada: buscar compras tras mitigación en demanda."
    else:
        conclusion_final = concl

    # 🧠 Payload final
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
        "escenario_1": esc1,
        "escenario_2": esc2,
        "setup_tesla": setup_activo,
        "conclusion_general": conclusion_final,
        "reflexion": reflexion,
        "slogan": slogan,
        "simbolo": symbol,
        "temporalidades": ["D", "H4", "H1", "M15", "M5"]
    }

    # 🔹 Formateo final (UI)
    from utils.intelligent_formatter import construir_mensaje_operativo, construir_mensaje_free
    nivel_usuario = payload.get("nivel_usuario", "Premium")
    if nivel_usuario.lower() == "premium":
        payload["mensaje_formateado"] = construir_mensaje_operativo(payload)
    else:
        payload["mensaje_formateado"] = construir_mensaje_free(payload)

    return {"🧠 TESLABTC.KG": payload}

# ============================================================
# 🔹 Interpretación contextual inteligente TESLABTC (v5.3)
# ============================================================
def interpretar_contexto(tf_d, tf_h4, tf_h1, confs, zonas):
    d = tf_d.get("estado", "—")
    h4 = tf_h4.get("estado", "—")
    h1 = tf_h1.get("estado", "—")
    bos_d = tf_d.get("BOS", "—")
    bos_h4 = tf_h4.get("BOS", "—")
    bos_h1 = tf_h1.get("BOS", "—")

    interpretacion = []

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
        interpretacion.append("Divergencia entre D y H4: fase de rango/transition.")
        if h1 == "alcista":
            interpretacion.append("H1 busca máximos menores dentro del rango.")
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

    # Rango diario textual
    if isinstance(zonas, dict) and "PDH" in zonas and "PDL" in zonas:
        interpretacion.append(f"Rango diario: {zonas['PDL']:,} → {zonas['PDH']:,}.")

    return " ".join(interpretacion)
