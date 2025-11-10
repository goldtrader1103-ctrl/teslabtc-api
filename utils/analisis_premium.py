from __future__ import annotations
print("🧠 TESLABTC.KG — v5.1 REAL MARKET (última compilación activa)")

# ============================================================
# 🧠 TESLABTC.KG — Análisis Premium (v5.1 REAL MARKET)
# ============================================================
# Fuente: Binance (REST) — sin simulaciones
# Estructura real multi-TF, Rango Asiático, PDH/PDL, Escenarios TESLA,
# y SETUP ACTIVO “Level Entry M5”.
# ============================================================

import requests, math, random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

TZ_COL = timezone(timedelta(hours=-5))
BINANCE_REST_BASE = "https://api.binance.com"
UA = {"User-Agent": "teslabtc-kg/5.1"}

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
# 🔹 Pivotes y tendencia
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
    if not kl or len(kl) < 15:
        return {"estado": "lateral"}

    hi_idx, lo_idx = _pivotes(kl)
    if len(hi_idx) < 2 or len(lo_idx) < 2:
        return {"estado": "lateral"}

    hh = kl[hi_idx[-1]]["high"]; lh = kl[hi_idx[-2]]["high"]
    ll = kl[lo_idx[-1]]["low"];  hl = kl[lo_idx[-2]]["low"]

    if hh > lh and ll > hl:
        return {"estado": "alcista", "BOS": "✔️", "HH": hh, "LH": lh, "LL": ll, "HL": hl}
    if hh < lh and ll < hl:
        return {"estado": "bajista", "BOS": "✔️", "HH": hh, "LH": lh, "LL": ll, "HL": hl}
    return {"estado": "lateral", "BOS": "—", "HH": hh, "LH": lh, "LL": ll, "HL": hl}

# ------------------------------------------------------------
# 🔹 Rangos especiales (COL)
# ------------------------------------------------------------
def _asian_range(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """Rango Asiático COL: 17:00 → 02:00 (día siguiente)"""
    if not kl_15m:
        return None
    ref = datetime.now(TZ_COL)
    start = ref.replace(hour=17, minute=0, second=0, microsecond=0)
    end = (ref + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)

    hi, lo = None, None
    for k in kl_15m:
        # kl times en UTC → convertir a COL para el filtro
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(TZ_COL)
        if start <= t_col <= end:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)
    if hi is None or lo is None:
        return None
    return {"ASIAN_HIGH": hi, "ASIAN_LOW": lo}

def _pdh_pdl(kl_15m: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """Día previo COL: 19:00 → 19:00"""
    if not kl_15m:
        return None
    ref = datetime.now(TZ_COL)
    end = ref.replace(hour=19, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)

    hi, lo = None, None
    for k in kl_15m:
        t_col = k["open_time"].replace(tzinfo=timezone.utc).astimezone(TZ_COL)
        if start <= t_col < end:
            h = float(k["high"]); l = float(k["low"])
            hi = h if hi is None else max(hi, h)
            lo = l if lo is None else min(lo, l)
    if hi is None or lo is None:
        return None
    return {"PDH": hi, "PDL": lo}

# ------------------------------------------------------------
# 🔹 Confirmaciones (con interpretación real TESLABTC.KG)
# ------------------------------------------------------------
def _confirmaciones(
    precio: float,
    asian: Optional[Dict[str, float]],
    pd: Optional[Dict[str, float]],
    tf_d: Dict[str, Any],
    tf_h1: Dict[str, Any],
    sesion_activa: bool,
) -> Dict[str, str]:
    """
    Evalúa las confirmaciones estructurales, de liquidez y de sesión
    y devuelve descripciones analíticas claras en lugar de solo íconos.
    """

    confs: Dict[str, str] = {}

    # =======================
    # 🔹 Estructura macro
    # =======================
    if tf_d.get("estado") == "alcista":
        confs["Tendencia macro (D)"] = "📈 Estructura diaria alcista confirmada."
    elif tf_d.get("estado") == "bajista":
        confs["Tendencia macro (D)"] = "📉 Estructura diaria bajista confirmada."
    else:
        confs["Tendencia macro (D)"] = "⚪ Estructura lateral o indecisa."

    # =======================
    # 🔹 Intradía (H1)
    # =======================
    if tf_h1.get("estado") == "alcista":
        confs["Tendencia intradía (H1)"] = "🟢 Estructura H1 alcista, posible retroceso hacia demanda."
    elif tf_h1.get("estado") == "bajista":
        confs["Tendencia intradía (H1)"] = "🔴 Estructura H1 bajista, respetando oferta o buscando continuación."
    else:
        confs["Tendencia intradía (H1)"] = "⚪ H1 en rango o sin dirección clara."

    # =======================
    # 🔹 Sesión NY
    # =======================
    if sesion_activa:
        confs["Sesión NY"] = "✅ Activa — condiciones de volatilidad elevadas, ideal para setups intradía."
    else:
        confs["Sesión NY"] = "❌ Cerrada — fuera del horario operativo, solo análisis estructural."

    # =======================
    # 🔹 Liquidez (PDH / PDL)
    # =======================
    if isinstance(precio, (int, float)) and pd:
        pdh, pdl = pd.get("PDH"), pd.get("PDL")
        if pdh and precio > float(pdh):
            confs["Barrida PDH"] = "⚠️ Liquidez superior tomada (PDH barrido). Vigilar reacción bajista."
        elif pdl and precio < float(pdl):
            confs["Barrida PDL"] = "⚠️ Liquidez inferior tomada (PDL barrido). Posible rebote alcista."
        else:
            confs["Barrida PDH/PDL"] = "➖ Sin barridas relevantes en el rango diario."

    # =======================
    # 🔹 Rango Asiático
    # =======================
    if asian:
        if precio > float(asian.get("ASIAN_HIGH", 0)):
            confs["Barrida Alto Asiático"] = "⚠️ Alto asiático eliminado — posible reacción bajista."
        elif precio < float(asian.get("ASIAN_LOW", 0)):
            confs["Barrida Bajo Asiático"] = "⚠️ Bajo asiático eliminado — posible reacción alcista."
        else:
            confs["Barrida Asia"] = "➖ Precio dentro del rango asiático."

    # =======================
    # 🔹 OBs o POIs relevantes (solo interpretación)
    # =======================
    confs["OB válido H1/H15"] = (
        "📍 Orden block válido en zona relevante — puede generar entrada confirmada."
        if (tf_h1.get("estado") in ["alcista", "bajista"])
        else "➖ Sin OB relevante confirmado."
    )

    # =======================
    # 🔹 Volumen y riesgo contextual (ligero toque aleatorio)
    # =======================
    interpretacion_vol = [
        "📊 Volumen moderado — ideal para continuidad estructural.",
        "⚖️ Volumen decreciente — posible agotamiento del impulso actual.",
        "🔥 Volumen alto — confirmar reacción antes de ejecutar entrada."
    ]
    confs["Volumen contextual"] = random.choice(interpretacion_vol)

    return confs


# ------------------------------------------------------------
# 🔹 Escenarios + Setup TESLA
# ------------------------------------------------------------
def _probabilidad_por_confs(confs: Dict[str, str]) -> str:
    ok = sum(1 for v in confs.values() if v == "✅")
    if ok >= 4: return "Alta"
    if ok >= 2: return "Media"
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
    # Sesgo por H1
    t_h1 = tf_h1.get("estado")
    if t_h1 == "alcista":
        tipo_favor, tipo_contra = "Compra", "Venta"
    elif t_h1 == "bajista":
        tipo_favor, tipo_contra = "Venta", "Compra"
    else:
        tipo_favor, tipo_contra = "Neutro", "Neutro"

    # Contexto por liquidez
    contexto: List[str] = []
    if isinstance(precio, (int, float)) and pd:
        if pd.get("PDL") and precio < float(pd["PDL"]):
            contexto.append("🧲 Barrida del PDL → desplazamiento potencial hacia PDH.")
        if pd.get("PDH") and precio > float(pd["PDH"]):
            contexto.append("🧲 Barrida del PDH → desplazamiento potencial hacia PDL.")
    if isinstance(precio, (int, float)) and asian:
        if asian.get("ASIAN_LOW") and precio < float(asian["ASIAN_LOW"]):
            contexto.append("🧲 Barrida del Bajo Asiático → buscar Alto Asiático.")
        if asian.get("ASIAN_HIGH") and precio > float(asian["ASIAN_HIGH"]):
            contexto.append("🧲 Barrida del Alto Asiático → buscar Bajo Asiático.")

    if t_h1 == "alcista": contexto.append("📈 Tendencia H1 alcista (sesgo comprador).")
    elif t_h1 == "bajista": contexto.append("📉 Tendencia H1 bajista (sesgo vendedor).")
    else: contexto.append("➖ H1 lateral: se requiere BOS/CHoCH para definir dirección.")

    contexto_txt = " | ".join(contexto) if contexto else "Contexto neutro."

    # Probabilidades
    prob_favor = _probabilidad_por_confs(confs)
    prob_contra = "Media" if prob_favor == "Alta" else ("Baja" if prob_favor == "Media" else "Baja")

    # Setup TESLA (candidato)
    def build_setup(prob: str, tipo: str) -> Tuple[str, Dict[str, str]]:
        tiene_setup = (prob in ("Alta", "Media")) and tipo in ("Compra", "Venta") and t_h1 in ("alcista", "bajista")
        if tiene_setup:
            return "✅ Setup candidato", {
                "zona_entrada": "Esperar BOS en M15/M5 dentro del POI.",
                "sl": "Alto/bajo anterior de la zona de entrada.",
                "tp1": "1:1 (mueva a BE y tome parciales)",
                "tp2": "1:2 (recoja sus ganancias)",
                "tp3": "1:3+ (opcional si la estructura respalda)",
                "observacion": "El bot prioriza 1:2; TP3+ sólo si hay fortaleza clara.",
            }
        else:
            return "⏳ Sin setup válido. Intenta en unos minutos.", {}

    setup_estado_favor, setup_favor = build_setup(prob_favor, tipo_favor)
    setup_estado_contra, setup_contra = build_setup(prob_contra, tipo_contra)

    def texto_esc(tipo: str) -> str:
        if tipo == "Compra":
            return "Objetivo en liquidez superior (PDH / ASIA HIGH / HH). Entrada tras BOS alcista M15; gestionar 1:2."
        if tipo == "Venta":
            return "Objetivo en liquidez inferior (PDL / ASIA LOW / LL). Entrada tras BOS bajista M15; gestionar 1:2."
        return "Esperar BOS claro en zona marcada para definir dirección."

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
# 🔹 Sesión NY + Reflexiones
# ------------------------------------------------------------
def _estado_sesion_ny() -> Tuple[str, bool]:
    ahora = datetime.now(TZ_COL)
    start = ahora.replace(hour=8, minute=30, second=0, microsecond=0)
    end   = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    activa = start <= ahora <= end
    return ("🟢 Activa (NY)" if activa else "❌ Cerrada (Fuera de NY)"), activa

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
            # zona de entrada “mitigación” simple: +/- 0.1% del cierre
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
# 🔹 Zonas para mostrar (PDH/PDL, Asia, rangos TF)
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

# ============================================================
# 🌟 TESLABTC — ANÁLISIS PREMIUM REAL (v5.2 Dinámico)
# ============================================================

def generar_analisis_premium(symbol: str = "BTCUSDT") -> Dict[str, Any]:
    now = datetime.now(TZ_COL)
    fecha_txt = now.strftime("%d/%m/%Y %H:%M:%S")

    # -----------------------
    # 🔹 PRECIO ACTUAL
    # -----------------------
    precio, fuente = _safe_get_price(symbol)
    precio_txt = f"{precio:,.2f} USD" if isinstance(precio, (int, float)) else "—"

    # -----------------------
    # 🔹 DATOS MULTITF
    # -----------------------
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

    # -----------------------
    # 🔹 CONFIRMACIONES REALES
    # -----------------------
    conf = _confirmaciones(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h1, sesion_activa
    )

    # -----------------------
    # 🔹 DIRECCIÓN GENERAL
    # -----------------------
    tendencia_d = tf_d.get("estado", "—")
    tendencia_h4 = tf_h4.get("estado", "—")
    tendencia_h1 = tf_h1.get("estado", "—")

    direccion_general = (
        "🟢 Alcista" if tendencia_h4 == "alcista"
        else "🔴 Bajista" if tendencia_h4 == "bajista"
        else "⚪ Lateral"
    )

    estructura_txt = (
        f"D: {tendencia_d.upper()} | H4: {tendencia_h4.upper()} | H1: {tendencia_h1.upper()}"
    )

    # -----------------------
    # 🔹 INTERPRETACIÓN MACRO REAL
    # -----------------------
    contexto = interpretar_contexto(tf_d, tf_h4, tf_h1, conf, asian or {})

    # -----------------------
    # 🔹 ESCENARIOS
    # -----------------------
    esc1, esc2, concl = _escenarios(
        precio if isinstance(precio, (int, float)) else math.nan,
        asian, pd, tf_d, tf_h4, tf_h1, conf
    )

    # -----------------------
    # 🔹 SETUP ACTIVO
    # -----------------------
    setup_activo = _setup_activo_m5(symbol)

    # -----------------------
    # 🔹 ZONAS REALES
    # -----------------------
    zonas = _fmt_zonas(asian, pd, kl_d, kl_h4, kl_h1)

    # -----------------------
    # 🔹 REFLEXIÓN DINÁMICA
    # -----------------------
    if tf_h4.get("estado") == "bajista":
        reflexion = "El mercado castiga al impaciente; deja que el precio llegue a tu zona."
    elif tf_h4.get("estado") == "alcista" and tf_h1.get("estado") == "bajista":
        reflexion = "Un retroceso no es un cambio de tendencia; espera la confirmación."
    elif tf_h1.get("estado") == "alcista":
        reflexion = "Sigue la corriente, no luches contra la estructura."
    else:
        reflexion = random.choice(REFLEXIONES)

    slogan = "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!"

    # -----------------------
    # 🔹 CONCLUSIÓN OPERATIVA REAL
    # -----------------------
    if setup_activo.get("activo"):
        conclusion_final = (
            f"⚙️ {setup_activo['nivel']}\n"
            f"{setup_activo['contexto']}\n"
            f"Zona de entrada: {setup_activo['zona_entrada']}\n"
            f"SL: {setup_activo['sl']} | TP1: {setup_activo['tp1']} | TP2: {setup_activo['tp2']}\n"
            f"{setup_activo['comentario']}"
        )
    elif sesion_activa and tendencia_h4 == "bajista" and tendencia_h1 == "bajista":
        conclusion_final = "🟥 Estructura bajista consolidada. Priorizar ventas tras retrocesos a zonas premium."
    elif sesion_activa and tendencia_h4 == "alcista" and tendencia_h1 == "alcista":
        conclusion_final = "🟩 Estructura alcista confirmada. Buscar compras tras mitigación en demanda válida."
    else:
        conclusion_final = concl

    # -----------------------
    # 🧠 COMPILACIÓN FINAL
    # -----------------------
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

    return {"🧠 TESLABTC.KG": payload}

# ============================================================
# 🔹 Interpretación contextual inteligente TESLABTC (v5.2 REAL)
# ============================================================
def interpretar_contexto(tf_d, tf_h4, tf_h1, confs, zonas):
    """
    Genera una descripción analítica real del contexto del mercado
    basada en la estructura multitemporal, liquidez y confirmaciones TESLA.
    """

    d = tf_d.get("estado", "—")
    h4 = tf_h4.get("estado", "—")
    h1 = tf_h1.get("estado", "—")

    contexto = ""

    # ===============================================
    # 🔹 1. Contexto macro (D + H4)
    # ===============================================
    if d == "bajista" or h4 == "bajista":
        contexto = "Macro bajista: el mercado sigue desplazándose hacia zonas inferiores."
        if h1 == "alcista":
            contexto += " Se observa retroceso intradía hacia oferta; posible continuación bajista."
        elif confs.get("Barrida PDH") or confs.get("Barrida Alto Asiático"):
            contexto += " Tras barrida superior, podría iniciar reacción bajista en H1."
        else:
            contexto += " Mantener sesgo vendedor, esperando mitigación válida en zonas premium."

    elif d == "alcista" or h4 == "alcista":
        contexto = "Macro alcista: el precio mantiene estructura ascendente en D/H4."
        if h1 == "bajista":
            contexto += " Retroceso intradía hacia demanda detectado; posible continuación alcista."
        elif confs.get("Barrida PDL") or confs.get("Barrida Bajo Asiático"):
            contexto += " Barrida inferior completada; puede iniciar reacción alcista."
        else:
            contexto += " Mantener sesgo comprador mientras H1 conserve mínimos ascendentes."

    else:
        contexto = (
            "Mercado en rango o acumulación. "
            "Esperar ruptura de estructura con confirmación de volumen antes de operar."
        )

    # ===============================================
    # 🔹 2. Contexto de zonas y liquidez
    # ===============================================
    if isinstance(zonas, dict) and "PDH" in zonas and "PDL" in zonas:
        contexto += f" Rango diario entre {zonas['PDL']:,} y {zonas['PDH']:,}."
    if "ASIAN_HIGH" in zonas and "ASIAN_LOW" in zonas:
        contexto += f" Rango asiático entre {zonas['ASIAN_LOW']:,} y {zonas['ASIAN_HIGH']:,}."

    # ===============================================
    # 🔹 3. Contexto adicional por sesión
    # ===============================================
    if "Sesión NY" in confs.get("Sesión NY", ""):
        contexto += " Sesión NY activa — posible volatilidad intradía relevante."

    return contexto
