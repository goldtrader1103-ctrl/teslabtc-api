# ============================================================
# 📘 TESLABTC.KG — GLOSARIO TESLA STRATEGY (Versión educativa)
# ============================================================

CONCEPTOS = [

# ============================================================
# 🧩 ESTRUCTURA DE MERCADO
# ============================================================
{
    "nombre": "Estructura",
    "titulo": "📊 Estructura de Mercado",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Es la forma en la que el precio se mueve, formando altos (H) y bajos (L). Esta secuencia muestra si el mercado está subiendo, bajando o moviéndose de lado.",
    "ejemplo": "Si el precio hace nuevos altos y retrocesos suaves, está en estructura alcista (HH y HL)."
},
{
    "nombre": "Tendencia",
    "titulo": "🧭 Tendencia",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Es la dirección general del precio: puede ser alcista (sube), bajista (baja) o lateral (se mantiene igual).",
    "ejemplo": "Si el precio hace cada vez máximos y mínimos más altos, la tendencia es alcista."
},
{
    "nombre": "Impulso",
    "titulo": "🚀 Impulso",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Movimiento fuerte y rápido del precio en una dirección, mostrando fuerza de los compradores o vendedores.",
    "ejemplo": "Una serie de velas grandes hacia arriba después de romper una resistencia es un impulso alcista."
},
{
    "nombre": "Retroceso",
    "titulo": "↩️ Retroceso",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Movimiento temporal en contra de la dirección principal del mercado. Sirve para 'descansar' antes de continuar.",
    "ejemplo": "Después de un impulso alcista, el precio baja un poco antes de seguir subiendo: ese es un retroceso."
},
{
    "nombre": "BOS",
    "titulo": "⚡ BOS — Break of Structure",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Significa 'ruptura de estructura'. Ocurre cuando el precio rompe un alto o bajo importante, mostrando cambio o continuación de tendencia.",
    "ejemplo": "Si el precio rompe el último alto y lo supera, hay un BOS alcista (confirmando fuerza compradora)."
},
{
    "nombre": "CHoCH",
    "titulo": "🔄 CHoCH — Change of Character",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Significa 'cambio de carácter'. Es la primera señal de que la tendencia puede estar cambiando.",
    "ejemplo": "Si el mercado subía y rompe un bajo importante, hace un CHoCH bajista (posible reversión)."
},
{
    "nombre": "POI",
    "titulo": "🎯 POI — Point of Interest",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Zona o nivel donde se espera una reacción del precio, porque antes hubo compras o ventas importantes.",
    "ejemplo": "Un Order Block o un FVG pueden ser POI donde el precio rebota o cambia dirección."
},
{
    "nombre": "Order Block",
    "titulo": "🏛️ Order Block (OB)",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Es la última vela contraria antes de un movimiento fuerte. Marca dónde entró dinero institucional.",
    "ejemplo": "Una vela bajista antes de un gran impulso alcista es un OB de demanda."
},
{
    "nombre": "FVG",
    "titulo": "🌀 FVG — Fair Value Gap",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Espacio entre velas donde el precio se movió tan rápido que no hubo transacciones equilibradas.",
    "ejemplo": "Cuando hay un hueco entre velas, el precio suele volver a ese nivel para 'llenarlo'."
},
{
    "nombre": "Barrida",
    "titulo": "💧 Barrida de Liquidez",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Movimiento rápido donde el precio sobrepasa un alto o bajo para atrapar órdenes (liquidez) antes de revertir.",
    "ejemplo": "El precio supera un máximo anterior y luego cae con fuerza: eso fue una barrida."
},
{
    "nombre": "Rango Asiático",
    "titulo": "🌏 Rango Asiático",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Zona donde el precio se mueve de manera lateral entre las 5 PM y las 2 AM (hora Colombia). Suele marcar acumulación.",
    "ejemplo": "Antes de la sesión de Nueva York, el precio suele barrer un extremo del rango asiático y luego tomar dirección."
},
{
    "nombre": "Rango Diario",
    "titulo": "📅 Rango Diario",
    "categoria": "🧩 Estructura de Mercado",
    "definicion": "Rango entre el máximo (PDH) y el mínimo (PDL) del día anterior.",
    "ejemplo": "Si el precio rompe el PDH pero no sigue subiendo, puede venir una caída."
},

# ============================================================
# 💰 GESTIÓN Y EJECUCIÓN
# ============================================================
{
    "nombre": "RRR",
    "titulo": "📊 RRR — Riesgo / Recompensa",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Relación que mide cuánto puedes ganar comparado con lo que estás dispuesto a perder.",
    "ejemplo": "Si arriesgas $10 para ganar $30, tu RRR es 1:3."
},
{
    "nombre": "Lotaje",
    "titulo": "📦 Lotaje",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Tamaño de la posición que abres. Cuanto mayor sea, más ganas o pierdes por cada movimiento del precio.",
    "ejemplo": "Con una cuenta de $1.000 y riesgo de 1 %, el tamaño de la operación depende del stop loss."
},
{
    "nombre": "Break-even",
    "titulo": "⚖️ Break-even (BE)",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Punto donde no ganas ni pierdes. Se logra al mover el stop loss al precio de entrada.",
    "ejemplo": "Si tu operación llega a 1:1, puedes mover el SL a BE para proteger tu capital."
},
{
    "nombre": "Parciales",
    "titulo": "💸 Parciales",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Cerrar una parte de la operación para asegurar ganancias y reducir riesgo.",
    "ejemplo": "Cerrar el 50 % de la posición cuando el precio alcanza un 1:2 de beneficio."
},
{
    "nombre": "SL",
    "titulo": "🛑 Stop Loss (SL)",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Precio donde se cierra automáticamente una operación para limitar pérdidas.",
    "ejemplo": "Colocar el SL debajo del último mínimo en una compra para protegerte si el precio cae."
},
{
    "nombre": "TP",
    "titulo": "🎯 Take Profit (TP)",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Nivel donde cierras la operación para tomar tus ganancias.",
    "ejemplo": "Colocar el TP en una zona de resistencia cercana o en una relación 1:3."
},
{
    "nombre": "Gestión del Riesgo",
    "titulo": "🛡️ Gestión del Riesgo",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Reglas que te ayudan a proteger tu capital y evitar pérdidas grandes.",
    "ejemplo": "Nunca arriesgar más del 1.5 % por operación."
},
{
    "nombre": "PDH",
    "titulo": "🔺 PDH — Previous Day High",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Máximo del día anterior. Es una zona donde suele haber liquidez (órdenes pendientes).",
    "ejemplo": "Cuando el precio rompe el PDH y no continúa, puede girarse hacia abajo."
},
{
    "nombre": "PDL",
    "titulo": "🔻 PDL — Previous Day Low",
    "categoria": "💰 Gestión y Ejecución",
    "definicion": "Mínimo del día anterior, donde se acumula liquidez de compradores.",
    "ejemplo": "El precio puede barrer el PDL y luego subir con fuerza."
},

# ============================================================
# ⚙️ ANÁLISIS TÉCNICO Y SISTEMA TESLA
# ============================================================
{
    "nombre": "Sistema TESLABTC",
    "titulo": "⚙️ Sistema TESLABTC",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Conjunto de reglas que guían cómo analizar, entrar y salir del mercado usando estructura, liquidez y horarios institucionales.",
    "ejemplo": "El sistema TESLABTC combina confirmaciones como BOS, POI y volumen para ejecutar con precisión."
},
{
    "nombre": "Volumen",
    "titulo": "📈 Volumen",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Muestra cuántas operaciones se hacen en un momento. Indica si hay fuerza real en el movimiento.",
    "ejemplo": "Un BOS con alto volumen es más confiable que uno con poco volumen."
},
{
    "nombre": "Oferta",
    "titulo": "🏷️ Oferta (Supply)",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Zona donde el precio tiende a caer por presencia de vendedores.",
    "ejemplo": "Un OB bajista o zona de resistencia fuerte."
},
{
    "nombre": "Demanda",
    "titulo": "🛒 Demanda (Demand)",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Zona donde el precio tiende a subir porque hay muchos compradores.",
    "ejemplo": "Un OB alcista o zona de soporte relevante."
},
{
    "nombre": "Fibonacci",
    "titulo": "📐 Retrocesos de Fibonacci",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Herramienta que mide cuánto retrocede el precio antes de continuar su tendencia.",
    "ejemplo": "Los retrocesos más comunes están entre 38 % y 61.8 %."
},
{
    "nombre": "Killzones",
    "titulo": "🕒 Killzones — Horarios Institucionales",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Son las horas del día donde los grandes participantes del mercado están más activos (Londres y Nueva York).",
    "ejemplo": "Operar dentro de la sesión de Nueva York mejora las probabilidades de éxito."
},
{
    "nombre": "Liquidez",
    "titulo": "💦 Liquidez",
    "categoria": "⚙️ Técnico / Sistema TESLA",
    "definicion": "Cantidad de órdenes pendientes en el mercado. El precio busca esa liquidez antes de moverse.",
    "ejemplo": "Las barridas ocurren cuando el precio toma la liquidez de los stops antes de girarse."
},

# ============================================================
# 🧠 PSICOLOGÍA Y ESTRATEGIA
# ============================================================
{
    "nombre": "Mentalidad",
    "titulo": "🧠 Mentalidad del Trader",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Es la forma en que piensas y reaccionas frente al mercado. La mentalidad correcta te permite mantener la calma y seguir tu plan.",
    "ejemplo": "Un trader con mentalidad disciplinada no se deja llevar por el miedo ni la euforia."
},
{
    "nombre": "Disciplina",
    "titulo": "🔥 Disciplina",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Seguir tus reglas incluso cuando tienes emociones fuertes. Es la base de la consistencia.",
    "ejemplo": "Esperar tus confirmaciones y no operar por impulso."
},
{
    "nombre": "Paciencia",
    "titulo": "⏳ Paciencia",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Esperar con calma hasta que el mercado muestre una oportunidad clara según tu plan.",
    "ejemplo": "No abrir operaciones si el BOS aún no se ha formado en la zona marcada."
},
{
    "nombre": "Confianza",
    "titulo": "🚀 Confianza",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Creer en tu sistema y en tu proceso, sin dejarte influir por resultados aislados.",
    "ejemplo": "No perder la confianza tras una pérdida, porque es parte del proceso."
},
{
    "nombre": "Plan de Trading",
    "titulo": "📋 Plan de Trading",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Guía que detalla cuándo, cómo y por qué vas a operar. Incluye tus reglas, riesgo y confirmaciones.",
    "ejemplo": "Tu plan puede decir: ‘Operar solo sesión NY, RRR mínimo 1:3, BE en 1:1 + 50 %.’"
},
{
    "nombre": "Scalping",
    "titulo": "⚡ Scalping",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Estilo de trading donde buscas movimientos rápidos y pequeños beneficios.",
    "ejemplo": "Abrir y cerrar operaciones en minutos con objetivos 1:2 o 1:3."
},
{
    "nombre": "Intradía",
    "titulo": "🕑 Intradía",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Operar dentro del mismo día, sin dejar operaciones abiertas durante la noche.",
    "ejemplo": "Buscar setups válidos solo durante la sesión de Nueva York."
},
{
    "nombre": "Swing Trading",
    "titulo": "🌙 Swing Trading",
    "categoria": "🧠 Psicología y Estrategia",
    "definicion": "Operar movimientos más amplios que duran varios días.",
    "ejemplo": "Mantener una posición mientras el precio sigue la tendencia semanal."
},

# ============================================================
# 🎓 CONCEPTOS GENERALES
# ============================================================
{
    "nombre": "Trading",
    "titulo": "💼 Trading",
    "categoria": "🎓 Conceptos Generales",
    "definicion": "Comprar y vender activos financieros buscando obtener ganancias con los cambios de precio.",
    "ejemplo": "Comprar BTC a 100 000 USD y venderlo a 105 000 USD genera una ganancia de 5 000 USD."
},
{
    "nombre": "Broker",
    "titulo": "🏦 Broker",
    "categoria": "🎓 Conceptos Generales",
    "definicion": "Empresa o plataforma que te permite ejecutar operaciones en los mercados.",
    "ejemplo": "Algunos brokers permiten operar criptomonedas, índices o metales."
},
{
    "nombre": "CFD",
    "titulo": "📄 Contrato por Diferencia (CFD)",
    "categoria": "🎓 Conceptos Generales",
    "definicion": "Instrumento financiero que replica el precio de un activo sin tener que comprarlo directamente.",
    "ejemplo": "Puedes operar oro o índices a través de CFD sin poseerlos físicamente."
},
{
    "nombre": "Activos Financieros",
    "titulo": "📈 Activos Financieros",
    "categoria": "🎓 Conceptos Generales",
    "definicion": "Instrumentos que pueden comprarse o venderse, como criptomonedas, acciones o divisas.",
    "ejemplo": "BTC, XAUUSD (oro) y NAS100 son activos financieros populares."
},
{
    "nombre": "Portfolio",
    "titulo": "🗂️ Portfolio",
    "categoria": "🎓 Conceptos Generales",
    "definicion": "Conjunto de inversiones o posiciones activas que posee un trader o inversor.",
    "ejemplo": "Tu portfolio puede incluir BTC, oro y acciones tecnológicas."
}
]
# ============================================================
# 🧩 Funciones auxiliares (para el bot y la API)
# ============================================================

def listar_conceptos():
    """Devuelve la lista completa de conceptos."""
    return CONCEPTOS

def obtener_concepto(nombre: str):
    """Busca un concepto por nombre."""
    for c in CONCEPTOS:
        if c.get("nombre", "").lower() == nombre.lower():
            return c
    return {
        "titulo": "❌ No encontrado",
        "definicion": "El concepto solicitado no está disponible en el glosario.",
        "ejemplo": ""
    }

if __name__ == "__main__":
    categorias = [c.get("categoria") for c in CONCEPTOS]
    print("CATEGORÍAS ENCONTRADAS:")
    for cat in sorted(set(categorias)):
        print("-", cat)
