# ============================================================
# utils/analisis_premium.py — TESLABTC interpretación PA real
# ============================================================
from datetime import datetime
import random

from utils.price_utils import obtener_klines_binance, sesion_ny_activa
from utils.swings import detectar_swings
from utils.bos_choch import tendencia_por_estructura, detectar_bos_choch
from utils.ob_detector import detectar_ob_valido
from utils.liquidez import niveles_liquidez_horas, asian_range

REFLEXIONES = [
    "La paciencia paga más que la prisa.",
    "El mercado recompensa la disciplina, no la emoción.",
    "Cada pérdida bien gestionada es una victoria a largo plazo.",
    "Tu mente es tu mejor indicador.",
    "¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
]

def _fmt(x): 
    return f"{x:,.0f}" if isinstance(x, (int,float)) else x

def _fib_ratio(last_imp_high, last_imp_low, price):
    if last_imp_high is None or last_imp_low is None: 
        return None
    if last_imp_high == last_imp_low: 
        return None
    # ratio medido desde un impulso bajista (alto->bajo). Ajuste si es alcista.
    top, bot = max(last_imp_high, last_imp_low), min(last_imp_high, last_imp_low)
    return (price - bot) / (top - bot)

def generar_analisis_premium(precio_actual: float) -> dict:
    ahora = datetime.now()
    sesion_txt = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # === 1) Datos de mercado (velas reales) ===
    h4 = obtener_klines_binance("BTCUSDT", "4h", 180)
    h1 = obtener_klines_binance("BTCUSDT", "1h", 180)
    m15 = obtener_klines_binance("BTCUSDT", "15m", 180)

    # === 2) Swings + Estructura real ===
    sw_h4 = detectar_swings(h4, depth=4)
    sw_h1 = detectar_swings(h1, depth=3)
    sw_m15 = detectar_swings(m15, depth=3)

    tend_h4 = tendencia_por_estructura(sw_h4)
    tend_h1 = tendencia_por_estructura(sw_h1)
    tend_m15 = tendencia_por_estructura(sw_m15)

    bos_h1 = detectar_bos_choch(sw_h1, tend_h1)
    bos_m15 = detectar_bos_choch(sw_m15, tend_m15)

    # Determina sesgo TESLA:
    # - Si H4 bajista -> sesgo mayor bajista; correcciones internas alcistas
    # - Si H4 alcista -> inverso
    sesgo_mayor = "Bajista" if tend_h4 == "bajista" else ("Alcista" if tend_h4 == "alcista" else "Rango")

    # === 3) OB válido en H1 (zona operativa) ===
    direccion_ob = "bajista" if sesgo_mayor == "Bajista" else "alcista"
    ob_h1 = detectar_ob_valido(h1, direccion_ob)
    poi_txt = "—"
    ofe_txt = "—"; dem_txt = "—"
    if ob_h1:
        a, b = ob_h1["rango"]
        if ob_h1["tipo"] == "oferta":
            ofe_txt = f"{_fmt(a)} – {_fmt(b)}"
            poi_txt = f"OB H1 ({_fmt(a)} – {_fmt(b)})"
        else:
            dem_txt = f"{_fmt(a)} – {_fmt(b)}"
            poi_txt = f"OB H1 ({_fmt(a)} – {_fmt(b)})"

    # === 4) Liquidez (PDH/PDL + Asia) ===
    liq_horas = niveles_liquidez_horas(h1)
    asia = asian_range(m15)

    # === 5) Sobreextensión (Fibo > 0.79 desde último impulso visible en H1) ===
    lastH = sw_h1[-1]["price"] if sw_h1 and sw_h1[-1]["type"]=="H" else (sw_h1[-2]["price"] if len(sw_h1)>=2 else None)
    lastL = sw_h1[-1]["price"] if sw_h1 and sw_h1[-1]["type"]=="L" else (sw_h1[-2]["price"] if len(sw_h1)>=2 else None)
    fib_ratio = _fib_ratio(lastH, lastL, precio_actual)
    sobreextendido = (fib_ratio is not None and (fib_ratio > 0.79 or fib_ratio < 0.21))

    # === 6) Construcción narrativa TESLA ===
    direccion_general = {
        "tendencia_principal": sesgo_mayor,
        "icono": "🔴" if sesgo_mayor=="Bajista" else ("🟢" if sesgo_mayor=="Alcista" else "⚪"),
        "contexto": (
            "Macro en " + sesgo_mayor.lower() + " por estructura HH/HL/LH/LL en H4; "
            "se interpreta la reacción intradía sobre POI H1."
        ),
        "comentario": (
            "CHoCH/BOS intradía: "
            f"H1={bos_h1['BOS']['tipo'] if bos_h1['BOS'] else '—'} | "
            f"M15={bos_m15['BOS']['tipo'] if bos_m15['BOS'] else '—'}."
        ),
    }

    estructura_global = {
        "high": _fmt(max(k["high"] for k in h4[-60:])) if h4 else None,
        "low":  _fmt(min(k["low"]  for k in h4[-60:])) if h4 else None,
        "rango_actual": "Corrección dentro del impulso mayor." if sesgo_mayor in ("Bajista","Alcista") else "Rango/Transición",
    }

    zonas_relevantes = {
        "POI_principal": poi_txt,
        "orderblock_diario": "—",  # (podemos añadir OB D real más adelante)
        "FVG": "—",                # (pendiente módulo FVG si lo deseas)
        "oferta": ofe_txt,
        "demanda": dem_txt,
        "nivel_fibo": "79–88% sobreextendido" if sobreextendido else "50–61.8% zona técnica",
        "mitigado": (ob_h1["mitigado"] if ob_h1 else None),
    }

    # Confirmaciones TESLA
    confirmaciones = {
        "BOS": f"H1={bos_h1['BOS']['tipo'] if bos_h1['BOS'] else '—'} | M15={bos_m15['BOS']['tipo'] if bos_m15['BOS'] else '—'}",
        "CHoCH": f"H1={bos_h1['CHoCH']['tipo'] if bos_h1['CHoCH'] else '—'} | M15={bos_m15['CHoCH']['tipo'] if bos_m15['CHoCH'] else '—'}",
        "sesión": "✔️ activa" if "Activa" in sesion_txt else "❌ cerrada",
        "tendencia_H1": "🔴 bajista" if tend_h1=="bajista" else ("🟢 alcista" if tend_h1=="alcista" else "⚪ rango"),
        "tendencia_M15": "🔴 bajista" if tend_m15=="bajista" else ("🟢 alcista" if tend_m15=="alcista" else "⚪ rango"),
        "volumen": "medio",  # (placeholder: se puede integrar volumen real más adelante)
        "comentario": "OB H1 mitigado" if (ob_h1 and ob_h1["mitigado"]) else "OB H1 sin mitigar" if ob_h1 else "Sin OB claro",
    }

    # Escenarios TESLA (dependen de sesgo mayor)
    if sesgo_mayor == "Bajista":
        esc_cont_dir = "Alcista (retroceso antes de continuidad bajista)"
        esc_corr_dir = "Bajista (continuación del impulso mayor)"
        esc_corr_prob = "Alta"
    elif sesgo_mayor == "Alcista":
        esc_cont_dir = "Bajista (retroceso antes de continuidad alcista)"
        esc_corr_dir = "Alcista (continuación del impulso mayor)"
        esc_corr_prob = "Alta"
    else:
        esc_cont_dir = "Neutral/Correctiva condicionada"
        esc_corr_dir = "Rango a direccional tras BOS"
        esc_corr_prob = "Media"

    escenario_continuacion = {
        "dirección": esc_cont_dir,
        "zona_de_interés": "Mitigación OB H1" if ob_h1 else "Zona M15",
        "confirmaciones_esperadas": "BOS M15 + quiebre ASIA High" if sesgo_mayor=="Bajista" else "BOS M15 + quiebre ASIA Low",
        "ejecución": {
            "entrada": "Reentrada en M5 tras BOS M15",
            "TP": f"{_fmt(liq_horas.get('PDH'))}" if sesgo_mayor=="Bajista" else f"{_fmt(liq_horas.get('PDL'))}",
            "SL": f"{_fmt(ob_h1['rango'][0])}" if ob_h1 and ob_h1["tipo"]=="oferta" else f"{_fmt(ob_h1['rango'][1])}" if ob_h1 else "—",
        },
        "probabilidad": "Media",
        "comentario": "Si sostiene estructura en M15 sin devolverse con violencia.",
    }

    escenario_correccion = {
        "dirección": esc_corr_dir,
        "zona_de_interés": "Rechazo OB H1" if ob_h1 else "Ruptura micro M15",
        "confirmaciones_esperadas": "BOS M15/M5 + quiebre mínimo intradía" if sesgo_mayor=="Bajista" else "BOS M15/M5 + quiebre máximo intradía",
        "ejecución": {
            "entrada": "Tras confirmación BOS dentro de OB" if ob_h1 else "Tras BOS en M15",
            "TP": f"{_fmt(liq_horas.get('PDL'))}" if sesgo_mayor=="Bajista" else f"{_fmt(liq_horas.get('PDH'))}",
            "SL": f"{_fmt(ob_h1['rango'][1])}" if ob_h1 and ob_h1["tipo"]=="oferta" else f"{_fmt(ob_h1['rango'][0])}" if ob_h1 else "—",
        },
        "probabilidad": esc_corr_prob,
        "comentario": "Validación hacia demanda/oferta diaria y liquidez limpia.",
    }

    conclusion_detallada = {
        "escenario_más_probable": "Corrección (bajista)" if sesgo_mayor=="Bajista" else ("Corrección (alcista)" if sesgo_mayor=="Alcista" else "Transición"),
        "motivo": f"Estructura H4 {sesgo_mayor.lower()} + OB H1 {'mitigado' if (ob_h1 and ob_h1['mitigado']) else 'activo'} + señales BOS/CHoCH intradía.",
        "recomendación": "Esperar BOS M15 | entrada en rechazo H1/M15 según sesgo.",
        "confianza": "Alta" if sesgo_mayor in ("Bajista","Alcista") else "Media",
    }

    # Campos TEXT para compatibilidad con tu bot actual
    zonas_texto = (
        f"📍 POI principal: {zonas_relevantes['POI_principal']}.\n"
        f"📊 Oferta: {zonas_relevantes['oferta']} | Demanda: {zonas_relevantes['demanda']}.\n"
        f"📈 Fibo: {zonas_relevantes['nivel_fibo']}."
    )
    escenario_1_texto = (
        f"🟢 *Escenario de continuación:*\nDirección: {escenario_continuacion['dirección']}\n"
        f"Zona: {escenario_continuacion['zona_de_interés']}\n"
        f"Confirmaciones: {escenario_continuacion['confirmaciones_esperadas']}\n"
        f"TP: {escenario_continuacion['ejecución']['TP']} | SL: {escenario_continuacion['ejecución']['SL']}\n"
        f"Probabilidad: {escenario_continuacion['probabilidad']}"
    )
    escenario_2_texto = (
        f"🔴 *Escenario de corrección:*\nDirección: {escenario_correccion['dirección']}\n"
        f"Zona: {escenario_correccion['zona_de_interés']}\n"
        f"Confirmaciones: {escenario_correccion['confirmaciones_esperadas']}\n"
        f"TP: {escenario_correccion['ejecución']['TP']} | SL: {escenario_correccion['ejecución']['SL']}\n"
        f"Probabilidad: {escenario_correccion['probabilidad']}"
    )
    conclusion_texto = (
        f"🧠 Escenario más probable: {conclusion_detallada['escenario_más_probable']}\n"
        f"Motivo: {conclusion_detallada['motivo']}\n"
        f"🎯 Recomendación: {conclusion_detallada['recomendación']}"
    )

    analisis = {
        "fecha": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "nivel_usuario": "Premium",
        "activo": "BTCUSDT",
        "sesión": sesion_txt,
        "precio_actual": f"{precio_actual:,.2f} USD",
        "temporalidades": ["D", "H4", "H1", "M15"],

        # Bloques estructurados
        "dirección_general": direccion_general,
        "estructura_global": estructura_global,
        "zonas_relevantes": zonas_relevantes,
        "confirmaciones": confirmaciones,
        "escenario_continuación": escenario_continuacion,
        "escenario_corrección": escenario_correccion,
        "conclusion": conclusion_detallada,

        # Compatibilidad bot
        "zonas": zonas_texto,
        "escenario_1": escenario_1_texto,
        "escenario_2": escenario_2_texto,
        "conclusion_texto": conclusion_texto,

        # Extras
        "liquidez": {
            "PDH": liq_horas.get("PDH"),
            "PDL": liq_horas.get("PDL"),
            "ASIAN_HIGH": asia.get("ASIAN_HIGH"),
            "ASIAN_LOW": asia.get("ASIAN_LOW"),
        },
        "reflexion": f"📘 Reflexión TESLABTC A.P.: {random.choice(REFLEXIONES)}",
        "nota": "⚠️ Ejecutar solo con BOS validado. CHoCH no confirma cambio macro.",
    }

    return analisis
