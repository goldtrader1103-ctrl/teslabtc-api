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
from utils.setup_detector import validar_setup_tesla

# ============================================================
# Reflexiones TESLABTC
# ============================================================
REFLEXIONES = [
    "La paciencia paga más que la prisa.",
    "El mercado recompensa la disciplina, no la emoción.",
    "Cada pérdida bien gestionada es una victoria a largo plazo.",
    "Tu mente es tu mejor indicador.",
    "¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
]

# ============================================================
# Funciones auxiliares
# ============================================================
def _fmt(x):
    return f"{x:,.0f}" if isinstance(x, (int, float)) else x


def _fib_ratio(last_imp_high, last_imp_low, price):
    if last_imp_high is None or last_imp_low is None:
        return None
    if last_imp_high == last_imp_low:
        return None
    top, bot = max(last_imp_high, last_imp_low), min(last_imp_high, last_imp_low)
    return (price - bot) / (top - bot)


def _formato_tendencia(label, tendencia, bos_data):
    """Genera texto formateado para cada temporalidad"""
    icono = "🔴" if tendencia == "bajista" else ("🟢" if tendencia == "alcista" else "⚪")
    tipo = None
    precio = None

    if bos_data and bos_data.get("CHoCH") and bos_data["CHoCH"].get("precio"):
        tipo = "CHoCH"
        precio = bos_data["CHoCH"]["precio"]
    elif bos_data and bos_data.get("BOS") and bos_data["BOS"].get("precio"):
        tipo = "BOS"
        precio = bos_data["BOS"]["precio"]

    if tipo:
        return f"{label}: {icono} {tendencia.capitalize()} ({tipo} en {_fmt(precio)})"
    else:
        return f"{label}: {icono} {tendencia.capitalize()} (sin ruptura reciente)"


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def generar_analisis_premium(precio_actual: float) -> dict:
    ahora = datetime.now()
    sesion_txt = "✅ Activa (Sesión NY)" if sesion_ny_activa() else "❌ Cerrada (Fuera de NY)"

    # === 1) Datos de mercado (velas reales) ===
    h4 = obtener_klines_binance("BTCUSDT", "4h", 180)
    h1 = obtener_klines_binance("BTCUSDT", "1h", 180)
    m15 = obtener_klines_binance("BTCUSDT", "15m", 180)
    m5 = obtener_klines_binance("BTCUSDT", "5m", 300)

    # === 2) Swings + Estructura ===
    sw_h4 = detectar_swings(h4, depth=4)
    sw_h1 = detectar_swings(h1, depth=3)
    sw_m15 = detectar_swings(m15, depth=3)
    sw_m5 = detectar_swings(m5, depth=3)

    tend_h4 = tendencia_por_estructura(sw_h4)
    tend_h1 = tendencia_por_estructura(sw_h1)
    tend_m15 = tendencia_por_estructura(sw_m15)
    tend_m5 = tendencia_por_estructura(sw_m5)

    bos_h4 = detectar_bos_choch(sw_h4, tend_h4)
    bos_h1 = detectar_bos_choch(sw_h1, tend_h1)
    bos_m15 = detectar_bos_choch(sw_m15, tend_m15)
    bos_m5 = detectar_bos_choch(sw_m5, tend_m5)

    # === 3) Sesgo general TESLA ===
    sesgo_mayor = "Bajista" if tend_h4 == "bajista" else ("Alcista" if tend_h4 == "alcista" else "Rango")

    # === 4) Order Block válido H1 ===
    direccion_ob = "bajista" if sesgo_mayor == "Bajista" else "alcista"
    ob_h1 = detectar_ob_valido(h1, direccion_ob)
    poi_txt, ofe_txt, dem_txt = "—", "—", "—"

    if ob_h1:
        a, b = ob_h1["rango"]
        if ob_h1["tipo"] == "oferta":
            ofe_txt = f"{_fmt(a)} – {_fmt(b)}"
            poi_txt = f"OB H1 ({_fmt(a)} – {_fmt(b)})"
        else:
            dem_txt = f"{_fmt(a)} – {_fmt(b)}"
            poi_txt = f"OB H1 ({_fmt(a)} – {_fmt(b)})"

    # === 5) Liquidez y sesión asiática ===
    liq_horas = niveles_liquidez_horas(h1)
    asia = asian_range(m15)

    # === 6) Fibo (sobreextensión) ===
    lastH = sw_h1[-1]["price"] if sw_h1 and sw_h1[-1]["type"] == "H" else (sw_h1[-2]["price"] if len(sw_h1) >= 2 else None)
    lastL = sw_h1[-1]["price"] if sw_h1 and sw_h1[-1]["type"] == "L" else (sw_h1[-2]["price"] if len(sw_h1) >= 2 else None)
    fib_ratio = _fib_ratio(lastH, lastL, precio_actual)
    sobreextendido = (fib_ratio is not None and (fib_ratio > 0.79 or fib_ratio < 0.21))

    # === 7) Confirmaciones TESLA ===
    conf_lineas = []
    choch_h1 = bos_h1['CHoCH']['tipo'] if bos_h1 and bos_h1.get('CHoCH') else None
    choch_m15 = bos_m15['CHoCH']['tipo'] if bos_m15 and bos_m15.get('CHoCH') else None
    if choch_h1 or choch_m15:
        conf_lineas.append(f"• CHoCH: H1={choch_h1 or '—'} | M15={choch_m15 or '—'}")

    bos_h1_txt = bos_h1['BOS']['tipo'] if bos_h1 and bos_h1.get('BOS') else None
    bos_m15_txt = bos_m15['BOS']['tipo'] if bos_m15 and bos_m15.get('BOS') else None
    if bos_h1_txt or bos_m15_txt:
        conf_lineas.append(f"• BOS: H1={bos_h1_txt or '—'} | M15={bos_m15_txt or '—'}")

    conf_lineas.extend([
        f"• sesión: {'✔️ activa' if 'Activa' in sesion_txt else '❌ cerrada'}",
        f"• tendenciaH1: {'🟢 alcista' if tend_h1 == 'alcista' else '🔴 bajista' if tend_h1 == 'bajista' else '⚪ rango'}",
        f"• tendenciaM15: {'🟢 alcista' if tend_m15 == 'alcista' else '🔴 bajista' if tend_m15 == 'bajista' else '⚪ rango'}",
        "• volumen: medio",
        f"• comentario: {'OB H1 mitigado' if (ob_h1 and ob_h1.get('mitigado')) else ('OB H1 sin mitigar' if ob_h1 else 'Sin OB claro')}",
    ])
    confirmaciones_texto = "\n".join(conf_lineas)

    # === 8) Validación del setup TESLA ===
    setup = validar_setup_tesla(
        precio_actual=precio_actual,
        tend_h1=tend_h1,
        tend_m15=tend_m15,
        bos_m15=bos_m15,
        bos_m5=bos_m5,
        ob_h1=ob_h1,
        liq_horas=liq_horas,
        asia=asia,
        min_confirmaciones=3
    )

    if setup["setup_valido"]:
        conf_list = "\n".join([f"• {c}" for c in setup["confirmaciones"]])
        setup_texto = (
            f"🎯 *SETUP TESLA ACTIVO ({setup['tipo']})*\n"
            f"Entrada: {_fmt(setup['entrada']) if setup['entrada'] else '—'}\n"
            f"TP1: {_fmt(setup['tp1']) if setup['tp1'] else '—'}"
            f"{' | TP2: ' + _fmt(setup['tp2']) if setup['tp2'] else ''}"
            f"{' | TP3: ' + _fmt(setup['tp3']) if setup['tp3'] else ''}\n"
            f"SL: {_fmt(setup['sl']) if setup['sl'] else '—'}\n"
            f"Confirmaciones:\n{conf_list}"
        )
    else:
        setup_texto = "⏳ En espera de setup válido (requiere BOS M15/M5 + ≥3 confirmaciones de contexto)."

    # === 9) Escenarios de contexto ===
    if sesgo_mayor == "Bajista":
        esc1_dir, esc2_dir, esc1_prob, esc2_prob = "Corrección alcista antes de continuidad bajista", "Continuación bajista con ruptura de mínimos", "Alta", "Media"
    elif sesgo_mayor == "Alcista":
        esc1_dir, esc2_dir, esc1_prob, esc2_prob = "Corrección bajista antes de continuidad alcista", "Continuación alcista con ruptura de máximos", "Alta", "Media"
    else:
        esc1_dir, esc2_dir, esc1_prob, esc2_prob = "Rango lateral en espera de CHoCH claro", "Transición con baja direccionalidad", "Media", "Media"

    escenario_1_texto = (
        f"📈 {esc1_dir}\nZona: POI H1/M15\n"
        f"Confirmaciones: CHoCH/BOS M15 + ruptura ASIA\n"
        f"TP: {_fmt(liq_horas.get('PDH')) if sesgo_mayor == 'Bajista' else _fmt(liq_horas.get('PDL'))}\n"
        f"Probabilidad: {esc1_prob}"
    )
    escenario_2_texto = (
        f"📉 {esc2_dir}\nZona: rechazo OB H1 o ruptura M15\n"
        f"Confirmaciones: CHoCH contrario al sesgo\n"
        f"TP: {_fmt(liq_horas.get('PDL')) if sesgo_mayor == 'Bajista' else _fmt(liq_horas.get('PDH'))}\n"
        f"Probabilidad: {esc2_prob}"
    )

        # === 10) Conclusión ===
    conclusion_texto = (
        f"🧠 Escenario más probable: {'Corrección (bajista)' if sesgo_mayor == 'Bajista' else 'Corrección (alcista)' if sesgo_mayor == 'Alcista' else 'Transición'}\n"
        f"Motivo: Estructura H4 {sesgo_mayor.lower()} + OB H1 {'mitigado' if (ob_h1 and ob_h1['mitigado']) else 'activo'}.\n"
        f"🎯 Recomendación: Esperar CHoCH M15 y confirmar con volumen."
    )

    # === 10.5) Zonas relevantes TESLABTC ===
    zonas_relevantes = {}

    if poi_txt and poi_txt != "—":
        zonas_relevantes["POI H1"] = poi_txt
    if ofe_txt and ofe_txt != "—":
        zonas_relevantes["Oferta H1"] = ofe_txt
    if dem_txt and dem_txt != "—":
        zonas_relevantes["Demanda H1"] = dem_txt
    if asia and asia.get("ASIAN_LOW") and asia.get("ASIAN_HIGH"):
        zonas_relevantes["Rango Asiático"] = f"{_fmt(asia['ASIAN_LOW'])} – {_fmt(asia['ASIAN_HIGH'])}"
    if fib_ratio is not None:
        zonas_relevantes["Fibonacci Ratio"] = f"{fib_ratio:.2f}"

    # === 11) Construcción final ===
    analisis = {
        "fecha": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "nivel_usuario": "Premium",
        "activo": "BTCUSDT",
        "sesión": sesion_txt,
        "precio_actual": f"{precio_actual:,.2f} USD",
        "temporalidades": ["H4", "H1", "M15", "M5"],
        "zonas_relevantes": zonas_relevantes,
        "confirmaciones": confirmaciones_texto,
        "setup": setup_texto,
        "escenario_1": escenario_1_texto,
        "escenario_2": escenario_2_texto,
        "conclusion_texto": conclusion_texto,
        "fuente": "💱 Fuente: Binance (precio en tiempo real)",
        "liquidez": {
            "PDH": liq_horas.get("PDH"),
            "PDL": liq_horas.get("PDL"),
            "ASIAN_HIGH": asia.get("ASIAN_HIGH"),
            "ASIAN_LOW": asia.get("ASIAN_LOW"),
        },
        "reflexion": f"📘 Reflexión TESLABTC A.P.: {random.choice(REFLEXIONES)}",
        "nota": "⚠️ Ejecutar solo con CHoCH validado. BOS no confirma cambio macro.",
    }

    return analisis

