# ============================================================
# 📘 TESLABTC.KG — GLOSARIO TESLA STRATEGY (con emojis)
# ============================================================
# Estructura visual y pedagógica para el bot educativo TESLABOT.KG
# ============================================================

CONCEPTOS = [

    # ============================================================
    # 📈 ESTRUCTURA DE MERCADO
    # ============================================================
    {
        "nombre": "Estructura",
        "titulo": "📊 Estructura de Mercado",
        "categoria": "📈 Estructura",
        "definicion": "Organización del precio en base a altos (H) y bajos (L). Permite identificar la dirección general del mercado.",
        "ejemplo": "Una secuencia de HH y HL define estructura alcista."
    },
    {
        "nombre": "Tendencia",
        "titulo": "🧭 Tendencia",
        "categoria": "📈 Estructura",
        "definicion": "Dirección predominante del precio, ya sea alcista o bajista, definida por los swings mayores.",
        "ejemplo": "En una tendencia alcista se observan HH y HL consecutivos."
    },
    {
        "nombre": "BOS",
        "titulo": "⚡ BOS — Break of Structure",
        "categoria": "📈 Estructura",
        "definicion": "Ruptura de un alto o bajo estructural que confirma cambio de tendencia o continuación institucional.",
        "ejemplo": "Un BOS alcista invalida el último bajo relevante."
    },
    {
        "nombre": "CHoCH",
        "titulo": "🧩 CHoCH — Change of Character",
        "categoria": "📈 Estructura",
        "definicion": "Cambio inicial del comportamiento del precio que puede anticipar un BOS en sentido contrario.",
        "ejemplo": "Un CHoCH bajista dentro de tendencia alcista puede anticipar una reversión."
    },
    {
        "nombre": "POI",
        "titulo": "🎯 POI — Point of Interest",
        "categoria": "📈 Estructura",
        "definicion": "Zona relevante de oferta o demanda donde se espera reacción del precio.",
        "ejemplo": "Un POI puede ser un OB, FVG o nivel psicológico clave."
    },
    {
        "nombre": "Order Block",
        "titulo": "🏛️ Order Block (OB)",
        "categoria": "📈 Estructura",
        "definicion": "Última vela alcista antes de un impulso bajista (o viceversa) que generó un cambio estructural.",
        "ejemplo": "Un OB H1 fuerte suele coincidir con entrada institucional."
    },
    {
        "nombre": "FVG",
        "titulo": "🌀 FVG — Fair Value Gap",
        "categoria": "📈 Estructura",
        "definicion": "Brecha de ineficiencia entre velas consecutivas donde el precio no fue equilibrado.",
        "ejemplo": "El precio suele regresar al FVG antes de continuar su tendencia."
    },
    {
        "nombre": "Barrida",
        "titulo": "💧 Barrida de Liquidez",
        "categoria": "📈 Estructura",
        "definicion": "Movimiento donde el precio barre un alto o bajo anterior capturando liquidez antes de revertir.",
        "ejemplo": "Una barrida del PDH seguida de rechazo indica debilidad alcista."
    },
    {
        "nombre": "Rango Asia",
        "titulo": "🌏 Rango Asiático",
        "categoria": "📈 Estructura",
        "definicion": "Movimiento lateral del precio entre 5 PM y 2 AM COL. Suele marcar zonas de acumulación antes de la sesión NY.",
        "ejemplo": "El precio suele barrer un extremo del rango asiático antes de iniciar tendencia."
    },
    {
        "nombre": "Rango Diario",
        "titulo": "📅 Rango Diario",
        "categoria": "📈 Estructura",
        "definicion": "Área entre el máximo (PDH) y el mínimo (PDL) del día anterior.",
        "ejemplo": "La ruptura del PDH sin continuación indica posible reversión bajista."
    },

    # ============================================================
    # 💰 GESTIÓN Y EJECUCIÓN
    # ============================================================
    {
        "nombre": "Lotaje",
        "titulo": "📦 Lotaje",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Cantidad de unidades o tamaño de posición en una operación. Define el riesgo monetario.",
        "ejemplo": "Un riesgo del 1 % con 50 pips de stop define el lotaje ideal."
    },
    {
        "nombre": "Break-even",
        "titulo": "⚖️ Break-even (BE)",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Nivel donde la operación no genera pérdida ni ganancia.",
        "ejemplo": "Mover SL a entrada en 1:1 convierte la operación en BE."
    },
    {
        "nombre": "Parciales",
        "titulo": "💸 Parciales",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Cierre parcial de la posición para asegurar beneficios o reducir exposición.",
        "ejemplo": "Cerrar 50 % en 1:2 y dejar correr el resto a 1:3."
    },
    {
        "nombre": "RRR",
        "titulo": "📊 RRR — Risk Reward Ratio",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Relación riesgo-beneficio que mide cuántas unidades se ganan por cada unidad arriesgada.",
        "ejemplo": "Un RRR 1:3 significa ganar tres veces lo arriesgado."
    },
    {
        "nombre": "PDH",
        "titulo": "🔺 PDH — Previous Day High",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Máximo del día anterior, referencia de liquidez superior.",
        "ejemplo": "El precio puede barrer el PDH para inducir compras antes de caer."
    },
    {
        "nombre": "PDL",
        "titulo": "🔻 PDL — Previous Day Low",
        "categoria": "💰 Gestión / Ejecución",
        "definicion": "Mínimo del día anterior, referencia de liquidez inferior.",
        "ejemplo": "El rompimiento falso del PDL suele detonar compras institucionales."
    },

    # ============================================================
    # ⚙️ TÉCNICO / SISTEMA TESLA
    # ============================================================
    {
        "nombre": "Sistema",
        "titulo": "⚙️ Sistema TESLABTC",
        "categoria": "⚙️ Técnico",
        "definicion": "Conjunto de reglas, confirmaciones y gestión basadas en estructura, liquidez y reacción institucional.",
        "ejemplo": "El sistema TESLABTC combina BOS, POI, volumen y disciplina."
    },
    {
        "nombre": "Volumen",
        "titulo": "📈 Volumen",
        "categoria": "⚙️ Técnico",
        "definicion": "Cantidad total de operaciones ejecutadas en un periodo. Indica presencia o ausencia institucional.",
        "ejemplo": "Un BOS con alto volumen es más confiable."
    },
    {
        "nombre": "Killzones",
        "titulo": "🕐 Killzones — Horarios Institucionales",
        "categoria": "⚙️ Técnico",
        "definicion": "Zonas horarias con mayor actividad institucional: Londres y Nueva York.",
        "ejemplo": "Operar solo dentro de las Killzones aumenta la efectividad del sistema."
    },

    # ============================================================
    # 🧠 PSICOLOGÍA Y ESTRATEGIA
    # ============================================================
    {
        "nombre": "Disciplina",
        "titulo": "🧘 Disciplina",
        "categoria": "🧠 Psicología / Estrategia",
        "definicion": "Capacidad de seguir tu plan sin interferencia emocional.",
        "ejemplo": "No operar fuera de tu sesión es una muestra de disciplina."
    },
    {
        "nombre": "Paciencia",
        "titulo": "⏳ Paciencia",
        "categoria": "🧠 Psicología / Estrategia",
        "definicion": "Esperar confirmaciones válidas antes de entrar al mercado.",
        "ejemplo": "Paciencia es esperar el BOS dentro del POI y en horario NY."
    },
    {
        "nombre": "Plan de Trading",
        "titulo": "📋 Plan de Trading",
        "categoria": "🧠 Psicología / Estrategia",
        "definicion": "Documento que establece cuándo, cómo y por qué operas, definiendo tus reglas, riesgo y objetivos.",
        "ejemplo": "El plan TESLABTC especifica tus confirmaciones y gestión diaria."
    },
    {
        "nombre": "Mentalidad",
        "titulo": "🧠 Mentalidad del Trader",
        "categoria": "🧠 Psicología / Estrategia",
        "definicion": "Actitud emocional y cognitiva con la que enfrentas el mercado.",
        "ejemplo": "Pensar en ejecución y no en dinero fortalece tu consistencia."
    }
]
# Añadir al final de CONCEPTOS (lista):
CONCEPTOS.extend([
    {"nombre":"Rango", "titulo":"📦 Rango", "categoria":"📈 Estructura",
     "definicion":"Periodo de consolidación con altos y bajos contenidos.",
     "ejemplo":"Precio oscilando entre 100k y 102k es un rango."},
    {"nombre":"Impulso", "titulo":"🚀 Impulso", "categoria":"📈 Estructura",
     "definicion":"Movimiento direccional fuerte con velas consecutivas.",
     "ejemplo":"Serie de velas alcistas largas tras ruptura de PDH."},
    {"nombre":"Retroceso", "titulo":"↩️ Retroceso", "categoria":"📈 Estructura",
     "definicion":"Corrección contra la dirección del impulso dominante.",
     "ejemplo":"Después de romper un HH, el precio corrige a un OB."},
    {"nombre":"PDH", "titulo":"🔺 Previous Day High", "categoria":"💰 Gestión / Ejecución",
     "definicion":"Máximo del día previo (19:00→19:00 COL).", "ejemplo":"Nivel de liquidez superior."},
    {"nombre":"PDL", "titulo":"🔻 Previous Day Low", "categoria":"💰 Gestión / Ejecución",
     "definicion":"Mínimo del día previo (19:00→19:00 COL).", "ejemplo":"Nivel de liquidez inferior."},
    {"nombre":"A.H", "titulo":"🔼 Asia High", "categoria":"📈 Estructura",
     "definicion":"Alto del rango asiático (17:00→02:00 COL).", "ejemplo":"Suele ser barrido antes de NY."},
    {"nombre":"A.L", "titulo":"🔽 Asia Low", "categoria":"📈 Estructura",
     "definicion":"Bajo del rango asiático (17:00→02:00 COL).", "ejemplo":"Suele ser barrido antes de NY."},
    {"nombre":"HIGH", "titulo":"H — High", "categoria":"📈 Estructura",
     "definicion":"Pivote superior de la estructura.", "ejemplo":"HH > H previo."},
    {"nombre":"LOW", "titulo":"L — Low", "categoria":"📈 Estructura",
     "definicion":"Pivote inferior de la estructura.", "ejemplo":"LL < L previo."},
    {"nombre":"HH","titulo":"Higher High","categoria":"📈 Estructura","definicion":"Alto mayor que el alto previo.","ejemplo":"Ruptura de H anterior."},
    {"nombre":"HL","titulo":"Higher Low","categoria":"📈 Estructura","definicion":"Bajo mayor que el bajo previo.","ejemplo":"Corrección poco profunda."},
    {"nombre":"LH","titulo":"Lower High","categoria":"📈 Estructura","definicion":"Alto menor que el alto previo.","ejemplo":"Señal de debilidad alcista."},
    {"nombre":"LL","titulo":"Lower Low","categoria":"📈 Estructura","definicion":"Bajo menor que el bajo previo.","ejemplo":"Continuidad bajista."},
    {"nombre":"Oferta","titulo":"🏷️ Oferta (Supply)","categoria":"⚙️ Técnico","definicion":"Zona donde hay presión vendedora.","ejemplo":"OB bajista."},
    {"nombre":"Demanda","titulo":"🛒 Demanda (Demand)","categoria":"⚙️ Técnico","definicion":"Zona con presión compradora.","ejemplo":"OB alcista."},
    {"nombre":"Consolidación","titulo":"📦 Consolidación","categoria":"📈 Estructura","definicion":"Acumulación lateral previa a expansión.","ejemplo":"Rango estrecho."},
    {"nombre":"Distribución","titulo":"📤 Distribución","categoria":"📈 Estructura","definicion":"Fase de entrega previa a caídas.","ejemplo":"Wick rejections en techo de rango."},
    {"nombre":"Temporalidad","titulo":"⏱️ Temporalidad","categoria":"⚙️ Técnico","definicion":"Marco de tiempo del análisis.","ejemplo":"D / H4 / H1 / M15."},
    {"nombre":"Barrida de Liquidez","titulo":"💧 Barrida de Liquidez","categoria":"📈 Estructura","definicion":"Toma de stops en extremos clave antes de revertir.","ejemplo":"Barrida del PDL y giro alcista."},
    {"nombre":"Liquidez","titulo":"💦 Liquidez","categoria":"⚙️ Técnico","definicion":"Órdenes disponibles para ejecutar transacciones.","ejemplo":"Acumulación sobre PDH/PDL."},
    {"nombre":"BUY","titulo":"🟢 BUY (Compra)","categoria":"⚙️ Técnico","definicion":"Operación a favor de subidas.","ejemplo":"Entrada tras BOS alcista."},
    {"nombre":"SELL","titulo":"🔴 SELL (Venta)","categoria":"⚙️ Técnico","definicion":"Operación buscando caídas.","ejemplo":"Entrada tras BOS bajista."},
    {"nombre":"PIP","titulo":"📏 Pip","categoria":"💰 Gestión","definicion":"Unidad mínima de variación en pares FX.","ejemplo":"0.0001 en EURUSD (referencial)."},
    {"nombre":"Lotaje","titulo":"📦 Lotaje","categoria":"💰 Gestión","definicion":"Tamaño de posición.","ejemplo":"Riesgo 0.5% define lotaje."},
    {"nombre":"Apalancamiento","titulo":"🧮 Apalancamiento","categoria":"💰 Gestión","definicion":"Uso de deuda para ampliar exposición.","ejemplo":"x5, x10."},
    {"nombre":"Spread","titulo":"⚖️ Spread","categoria":"💰 Gestión","definicion":"Diferencia entre precio de compra/venta.","ejemplo":"Mayor en horarios de baja liquidez."},
    {"nombre":"Comisión","titulo":"💸 Comisión","categoria":"💰 Gestión","definicion":"Costo por transacción.","ejemplo":"Fee del exchange o broker."},
    {"nombre":"Fibonacci","titulo":"📐 Retroceso de Fibonacci","categoria":"⚙️ Técnico","definicion":"Herramienta para medir retrocesos (38–62–79%).","ejemplo":"Entrada en 62% del impulso M15."},
    {"nombre":"Price Action","titulo":"📜 Acción del Precio","categoria":"⚙️ Técnico","definicion":"Análisis sin indicadores, sólo precio/volumen.","ejemplo":"Estructura, POI, BOS/CHoCH."},
    {"nombre":"Trading","titulo":"💼 Trading","categoria":"🧠 Psicología / Estrategia","definicion":"Compra/venta de activos con fines especulativos.","ejemplo":"Scalping, Intradía, Swing."},
    {"nombre":"Activos Financieros","titulo":"📈 Activos Financieros","categoria":"⚙️ Técnico","definicion":"Instrumentos transables.","ejemplo":"BTC, XAUUSD, NAS100."},
    {"nombre":"Gestión del Riesgo","titulo":"🛡️ Gestión del Riesgo","categoria":"💰 Gestión","definicion":"Conjunto de reglas para limitar pérdida.","ejemplo":"Riesgo diario 1.5%."},
    {"nombre":"Sistema","titulo":"⚙️ Sistema","categoria":"⚙️ Técnico","definicion":"Reglas TESLABTC (BOS/POI/volumen/horarios).","ejemplo":"Operar sólo con confirmaciones."},
    {"nombre":"Scalping","titulo":"⚡ Scalping","categoria":"🧠 Psicología / Estrategia","definicion":"Operativa de muy corto plazo.","ejemplo":"Target 1:2 en minutos."},
    {"nombre":"Intraday","titulo":"🕑 Intradía","categoria":"🧠 Psicología / Estrategia","definicion":"Operativa dentro de la sesión.","ejemplo":"Sesión NY."},
    {"nombre":"Swing Trading","titulo":"🌙 Swing Trading","categoria":"🧠 Psicología / Estrategia","definicion":"Operaciones de varios días.","ejemplo":"Parciales escalonados."},
    {"nombre":"Position Trading","titulo":"🏔️ Position Trading","categoria":"🧠 Psicología / Estrategia","definicion":"Operaciones de semanas/meses.","ejemplo":"Tendencia macro D/H4."},
    {"nombre":"Broker","titulo":"🏦 Broker","categoria":"⚙️ Técnico","definicion":"Intermediario para ejecutar órdenes.","ejemplo":"Algunos con CFD."},
    {"nombre":"Bull Market","titulo":"🐂 Bull Market (Alcista)","categoria":"📈 Estructura","definicion":"Tendencia general ascendente.","ejemplo":"Secuencia HH/HL."},
    {"nombre":"Bear Market","titulo":"🐻 Bear Market (Bajista)","categoria":"📈 Estructura","definicion":"Tendencia general descendente.","ejemplo":"Secuencia LL/LH."},
    {"nombre":"SL","titulo":"🛑 Stop Loss (SL)","categoria":"💰 Gestión","definicion":"Nivel de invalidación de la operación.","ejemplo":"Alto/bajo anterior."},
    {"nombre":"TP","titulo":"🎯 Take Profit (TP)","categoria":"💰 Gestión","definicion":"Objetivo de beneficio.","ejemplo":"TP1 1:1, TP2 1:2, TP3 1:3."},
    {"nombre":"Zona de Entrada","titulo":"🧭 Zona de Entrada","categoria":"⚙️ Técnico","definicion":"Área candidata para ejecutar con confirmaciones.","ejemplo":"OB H1 + BOS M15."},
    {"nombre":"P.E","titulo":"🎯 Punto de Entrada (P.E)","categoria":"⚙️ Técnico","definicion":"Precio específico de ejecución (si aplica).","ejemplo":"No obligatorio; se espera confirmación."},
    {"nombre":"Parciales","titulo":"💸 Parciales","categoria":"💰 Gestión","definicion":"Cierres parciales para asegurar ganancias.","ejemplo":"50% en 1:2."},
    {"nombre":"Break-even","titulo":"⚖️ Break-even","categoria":"💰 Gestión","definicion":"Sin pérdida/ganancia al mover SL a entrada.","ejemplo":"BE al 1:1 + 50%."},
    {"nombre":"CFD","titulo":"📄 Contrato por Diferencia (CFD)","categoria":"⚙️ Técnico","definicion":"Derivado que replica movimientos del subyacente.","ejemplo":"Algunos brokers minoristas."},
    {"nombre":"Portfolio","titulo":"🗂️ Portfolio","categoria":"💰 Gestión","definicion":"Conjunto de posiciones o inversiones.","ejemplo":"Separar cuentas/tramos."},
])
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

