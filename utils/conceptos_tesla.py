# ============================================================
# 🧠 CONCEPTOS TESLA STRATEGY — Glosario educativo
# ============================================================

CONCEPTOS = {
    "estructura": {
        "titulo": "📊 Estructura del Mercado",
        "definicion": "La estructura muestra los altos (HH) y bajos (LL) que definen si el precio está en tendencia alcista, bajista o en rango.",
        "ejemplo": "Una secuencia de HH y HL confirma tendencia alcista en BTCUSDT."
    },
    "tendencia": {
        "titulo": "🧭 Tendencia",
        "definicion": "La dirección general del precio. Puede ser alcista, bajista o lateral.",
        "ejemplo": "BTC marca mínimos cada vez más altos en H4 → tendencia alcista."
    },
    "bos": {
        "titulo": "⚡ BOS — Break of Structure",
        "definicion": "Ruptura de estructura que confirma la continuación de la tendencia principal.",
        "ejemplo": "BTC rompe el último alto de H1, confirmando continuación alcista."
    },
    "choch": {
        "titulo": "🔄 CHoCH — Change of Character",
        "definicion": "Cambio de carácter que indica posible cambio de tendencia en el corto plazo.",
        "ejemplo": "Tras BOS alcista, un CHoCH bajista puede marcar inicio de reversión."
    },
    "poi": {
        "titulo": "🎯 POI — Point of Interest",
        "definicion": "Zona relevante donde el precio puede reaccionar. Suele ser un OB, FVG o nivel psicológico.",
        "ejemplo": "El precio reacciona en el POI H1 tras liquidar liquidez asiática."
    },
    "ob": {
        "titulo": "🏛️ Order Block",
        "definicion": "Última vela opuesta antes de un movimiento fuerte institucional.",
        "ejemplo": "El OB bajista en H1 generó la caída principal de BTC."
    },
    "fvg": {
        "titulo": "🌀 FVG — Fair Value Gap",
        "definicion": "Brecha de valor justo donde el precio no negoció, usada para detectar desequilibrios.",
        "ejemplo": "BTC retorna a mitigar un FVG en M15 antes de continuar su impulso."
    },
    "barrida": {
        "titulo": "💦 Barrida de Liquidez",
        "definicion": "Movimiento rápido que limpia órdenes por encima o debajo de niveles clave.",
        "ejemplo": "El precio barre los máximos de Londres antes de caer en NY."
    },
    "rango_asia": {
        "titulo": "🌏 Rango Asiático",
        "definicion": "Movimiento del precio durante la sesión asiática (acumulación/distribución).",
        "ejemplo": "Durante Asia, BTC consolida; NY ejecuta la ruptura del rango."
    },
    "killzone": {
        "titulo": "🕒 Killzones — Horarios Institucionales",
        "definicion": "Ventanas horarias donde suele entrar volumen institucional (2 am, 8 am y 2 pm NY).",
        "ejemplo": "La entrada se ejecuta en la killzone de Nueva York tras CHoCH M15."
    },
    "volumen": {
        "titulo": "📊 Volumen Institucional",
        "definicion": "Mide la participación de dinero institucional. Se busca confirmación de volumen en rupturas.",
        "ejemplo": "El BOS en M15 fue válido porque se acompañó de incremento de volumen."
    },
    "rrr": {
        "titulo": "💰 RRR — Riesgo / Recompensa",
        "definicion": "Relación entre el riesgo asumido (SL) y el beneficio potencial (TP).",
        "ejemplo": "Una operación con SL 100 USD y TP 300 USD tiene un RRR 1:3."
    },
    "mentalidad": {
        "titulo": "🧘‍♀️ Mentalidad",
        "definicion": "La base del rendimiento constante. Sin mentalidad disciplinada, ninguna estrategia funciona.",
        "ejemplo": "Esperar confirmación en vez de anticipar movimiento es mentalidad profesional."
    },
    "paciencia": {
        "titulo": "⏳ Paciencia",
        "definicion": "Capacidad de esperar zonas y confirmaciones sin impulsividad.",
        "ejemplo": "Esperar el BOS M15 dentro del POI H1 aumenta la probabilidad de éxito."
    }
}


def obtener_concepto(nombre: str):
    """Devuelve el concepto solicitado o un mensaje por defecto."""
    if not isinstance(nombre, str):
        return {
            "titulo": "❌ Entrada inválida",
            "definicion": "El parámetro 'nombre' debe ser texto.",
            "ejemplo": "Ejemplo: /concepto?nombre=bos"
        }

    return CONCEPTOS.get(nombre.lower(), {
        "titulo": "❌ Concepto no encontrado",
        "definicion": "El término solicitado no existe en el glosario Tesla Strategy.",
        "ejemplo": "Usa /educativo para ver todos los conceptos disponibles."
    })
