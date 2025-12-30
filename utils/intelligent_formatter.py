# ============================================================
# 🧠 intelligent_formatter.py — Formateo de mensajes TESLABTC
# Versión unificada para API (FastAPI) y BOT (Telegram)
# Compatible con analisis_premium v5.3.1 y estructura_utils
# ============================================================

from typing import Dict, Any


# ------------------------------------------------------------
# 🔢 Helper numérico seguro
# ------------------------------------------------------------
def _safe_num(v) -> str:
    try:
        if v is None or v == "—":
            return "—"
        if isinstance(v, (int, float)):
            return f"{v:,.2f}"
        # si ya viene con formato tipo '87,500.26' lo dejamos
        return str(v)
    except Exception:
        return str(v)


# ------------------------------------------------------------
# 🧩 Helpers para leer estructura (H4/H1) en Premium
# ------------------------------------------------------------
def _get_estado_estructura(estructura: Dict[str, Any], tf: str) -> str:
    """
    Lee estructura_detectada["H4"] / ["H1"] que normalmente tienen:
      {
        "estado": "alcista|bajista|lateral|sin_datos",
        "RANGO_HIGH": float|None,
        "RANGO_LOW": float|None,
        ...
      }
    y devuelve siempre un string UPPER seguro.
    """
    dato = estructura.get(tf, "lateral")

    if isinstance(dato, dict):
        est = dato.get("estado", "lateral")
    else:
        est = dato

    # Evitamos errores tipo "'dict' object has no attribute 'upper'"
    if not isinstance(est, str):
        try:
            est = str(est)
        except Exception:
            est = "lateral"

    est = (est or "lateral").upper()
    return est


def _get_rango_txt(estructura: Dict[str, Any], tf: str) -> str:
    """
    Devuelve el rango formateado "LOW – HIGH" para H4/H1
    usando las claves RANGO_LOW / RANGO_HIGH del payload Premium.
    """
    info = estructura.get(tf, {}) or {}
    if not isinstance(info, dict):
        return "N/D"

    hi = info.get("RANGO_HIGH")
    lo = info.get("RANGO_LOW")

    hi_txt = _safe_num(hi) if hi is not None else "N/D"
    lo_txt = _safe_num(lo) if lo is not None else "N/D"
    return f"{lo_txt} – {hi_txt}"


# ------------------------------------------------------------
# 📋 MENSAJE PRINCIPAL: SEÑALES ACTIVAS (Premium)
# ------------------------------------------------------------
def construir_mensaje_operativo(body: Dict[str, Any]) -> str:
    """
    Recibe el payload interno Premium:
      {
        "version": ...,
        "fecha": ...,
        "activo": "BTCUSDT",
        "precio_actual": "...",
        "sesión": "...",
        "fuente_precio": "...",
        "estructura_detectada": { ... },
        "zonas_detectadas": { ... },
        "scalping": {
          "continuacion": {...},
          "correccion": {...}
        },
        "swing": {...},
        "reflexion": "...",
        "slogan": "..."
      }
    y devuelve el texto listo para enviar por Telegram (Markdown).
    """
    fecha = body.get("fecha", "⏳")
    simbolo = body.get("activo", "BTCUSDT")
    precio = body.get("precio_actual", "—")
    sesion = body.get("sesión", body.get("sesion", "Sesión no detectada"))
    reflexion = body.get("reflexion", "Tu disciplina define tu rentabilidad.")
    slogan = body.get(
        "slogan",
        "✨ ¡Tu Mentalidad, Disciplina y Constancia definen tus Resultados!",
    )

    estructura = body.get("estructura_detectada", {}) or {}
    zonas_detectadas = body.get("zonas_detectadas", {}) or {}
    poi_h4 = zonas_detectadas.get("POI_H4", "—")

    scalping = body.get("scalping", {}) or {}
    s_cont = scalping.get("continuacion", {}) or {}
    s_corr = scalping.get("correccion", {}) or {}
    swing = body.get("swing", {}) or {}

    # ---------------------------
    # 🕒 Sesión (solo texto)
    # ---------------------------
    sesion_line = f"🕒 Sesión: {sesion}"

    # ---------------------------
    # 🔹 Helper: bloque scalping
    # ---------------------------
    def _bloque_scalping(nombre: str, data: Dict[str, Any]) -> str:
        activo = bool(data.get("activo", False))
        estado = "✅ ACTIVO" if activo else "⏳ En espera"
        direccion = data.get("direccion", "—")
        riesgo = data.get("riesgo", "N/A")
        entrada = _safe_num(data.get("zona_reaccion", "—"))
        tp1 = _safe_num(data.get("tp1_rr", "1:1 (50% + BE)"))
        tp2 = _safe_num(data.get("tp2_rr", "1:2 (50%)"))
        sl = _safe_num(data.get("sl", "—"))

        sl_alerta = bool(data.get("sl_alerta", False))
        sl_dist = data.get("sl_dist")
        sl_pct = data.get("sl_pct")

        txt: list[str] = []
        txt.append(f"🔷 {nombre}")
        txt.append("──────────────────────────────")
        txt.append(f"📌 Estado: {estado}")
        txt.append(f"📈 Dirección: {direccion}")
        txt.append(f"⚠️ Riesgo: {riesgo}")
        txt.append("")
        txt.append(f"📥 Punto de entrada: {entrada}")
        txt.append(f"🎯 TP1: {tp1}")
        txt.append(f"🎯 TP2: {tp2}")
        txt.append(f"🛡️ SL: {sl}")

        # Aviso extra si el SL es exagerado para scalping
        if sl_alerta and sl_dist is not None and sl_pct is not None:
            dist_txt = _safe_num(sl_dist)
            txt.append(
                f"⚠️ Alerta TESLABTC: SL amplio para scalping (~{dist_txt} puntos, {sl_pct:.2f}% del precio). "
                "El mercado puede estar sobreextendido; considera reducir tamaño o no tomar esta operación."
            )

        return "\\n".join(txt)

    # ---------------------------
    # 🔹 Bloque SWING
    # ---------------------------
    def _bloque_swing(data: Dict[str, Any]) -> str:
        activo = bool(data.get("activo", False))
        estado = "✅ ACTIVO" if activo else "⏳ En espera"
        direccion = data.get("direccion", "—")
        riesgo = data.get("riesgo", "N/A")

        zona_reac = data.get("zona_reaccion")
        if not zona_reac or zona_reac == "—":
            zona_reac = data.get("premium_zone") or poi_h4 or "—"

        tp1 = _safe_num(data.get("tp1_rr", "—"))
        tp2 = _safe_num(data.get("tp2_rr", "—"))
        tp3 = _safe_num(data.get("tp3_objetivo", "—"))
        sl = _safe_num(data.get("sl", "—"))

        txt: list[str] = []
        txt.append("📈 ESCENARIO SWING")
        txt.append("──────────────────────────────")
        txt.append(f"📌 Estado: {estado}")
        txt.append(f"📈 Dirección: {direccion}")
        txt.append(f"⚠️ Riesgo: {riesgo}")
        txt.append(
            "📍 Contexto: Usa el botón de contexto para ver la explicación completa del trade.\n"
        )
        txt.append(f"📥 Zona de reacción: {zona_reac}")
        txt.append(f"🎯 TP1: {tp1}")
        txt.append(f"🎯 TP2: {tp2}")
        txt.append(f"🎯 TP3: {tp3}")
        txt.append(f"🛡️ SL: {sl}\n")
        return "\n".join(txt)

    # ---------------------------
    # 🧾 Construimos TODO
    # ---------------------------
    partes: list[str] = []

    # CABECERA
    partes.append("📋 SEÑALES ACTIVAS")
    partes.append("──────────────────────────────")
    partes.append(f"📅 Fecha: {fecha}")
    partes.append(f"💰 Activo: {simbolo}")
    partes.append(f"💵 Precio actual: {precio}")
    partes.append(sesion_line)
    partes.append("")

    # SCALPING
    partes.append("📊 ESCENARIOS OPERATIVOS SCALPING")
    partes.append("──────────────────────────────")
    partes.append(
        _bloque_scalping(
            "Escenario de Continuación (Tendencia Principal)",
            s_cont,
        )
    )
    partes.append(
        _bloque_scalping(
            "Escenario de Corrección (Contra Tendencia)",
            s_corr,
        )
    )

    # SWING
    partes.append(_bloque_swing(swing))

    # REFLEXIÓN
    partes.append("📓 Reflexión TESLABTC A.P.")
    partes.append("──────────────────────────────")
    partes.append(f"💭 {reflexion}\n")
    partes.append(
        "⚠️ Análisis SCALPING diseñado para la apertura de cada sesión (Asia, Londres y NY)."
    )
    partes.append("⚠️ Análisis SWING actualizado cada vela de 1H.")
    partes.append(slogan)

    return "\n".join(partes)


# ------------------------------------------------------------
# 🆓 MENSAJE FREE: estructura general sin setups
# ------------------------------------------------------------
def construir_mensaje_free(body: Dict[str, Any]) -> str:
    """
    Mensaje para usuarios Free.
    Usa la estructura simplificada H4/H1/M15 que construye main.py.
    """
    fecha = body.get("fecha", "⏳")
    simbolo = body.get("activo", "BTCUSDT")
    precio = body.get("precio_actual", "—")
    sesion = body.get("sesión", body.get("sesion", "Sesión no detectada"))
    fuente = body.get("fuente_precio", "Binance")
    conexion = body.get("conexion_binance", "OK")

    estructura = body.get("estructura_detectada", {}) or {}

    def _fmt_tf(key: str) -> str:
        info = estructura.get(key, {}) or {}
        if isinstance(info, dict):
            estado = info.get("estado", "sin_datos")
            hi = info.get("high")
            lo = info.get("low")
        else:
            # por si en algún caso viene solo texto
            estado = str(info)
            hi = lo = None

        hi_txt = _safe_num(hi) if hi is not None else "N/D"
        lo_txt = _safe_num(lo) if lo is not None else "N/D"
        return f"{estado} | Rango: {lo_txt} – {hi_txt}"

    h4_txt = _fmt_tf("H4 (macro)")
    h1_txt = _fmt_tf("H1 (intradía)")
    m15_txt = _fmt_tf("M15 (reacción)")

    partes: list[str] = []
    partes.append("📋 ANÁLISIS GENERAL (MODO FREE)")
    partes.append("──────────────────────────────")
    partes.append(f"📅 Fecha: {fecha}")
    partes.append(f"💰 Activo: {simbolo}")
    partes.append(f"💵 Precio actual: {precio}")
    partes.append(f"🕒 Sesión: {sesion}")
    partes.append(f"🌐 Fuente precio: {fuente} (conexión: {conexion})")
    partes.append("")
    partes.append("🧭 *Estructura por temporalidad*")
    partes.append(f"• H4 (macro): {h4_txt}")
    partes.append(f"• H1 (intradía): {h1_txt}")
    partes.append(f"• M15 (reacción): {m15_txt}")
    partes.append("")
    partes.append(
        "⚠️ Esta vista Free resume solo la estructura general del mercado."
    )
    partes.append(
        "   Para ver setups SCALPING y SWING completos, activa tu acceso Premium TESLABTC.KG."
    )

    return "\n".join(partes)


# ------------------------------------------------------------
# 📘 CONTEXTO DETALLADO POR ESCENARIO (Premium)
# ------------------------------------------------------------
def construir_contexto_detallado(body: Dict[str, Any], escenario: str) -> str:
    """
    Genera un texto explicativo para:
      - 'scalping_continuacion'
      - 'scalping_correccion'
      - 'swing'
    usando el payload Premium ya cacheado (estructura_detectada, scalping, swing).
    """
    simbolo = body.get("activo", "BTCUSDT")
    precio = body.get("precio_actual", "—")
    sesion = body.get("sesión", body.get("sesion", "Sesión no detectada"))

    estructura = body.get("estructura_detectada", {}) or {}
    dir_h4 = _get_estado_estructura(estructura, "H4")
    dir_h1 = _get_estado_estructura(estructura, "H1")
    rango_h4 = _get_rango_txt(estructura, "H4")
    rango_h1 = _get_rango_txt(estructura, "H1")

    scalping = body.get("scalping", {}) or {}
    s_cont = scalping.get("continuacion", {}) or {}
    s_corr = scalping.get("correccion", {}) or {}
    swing = body.get("swing", {}) or {}
    zonas = body.get("zonas_detectadas", {}) or {}

    header = (
        "📘 *Contexto TESLABTC A.P.*\n\n"
        f"• Activo: *{simbolo}*\n"
        f"• Precio actual: *{precio}*\n"
        f"• Sesión actual: {sesion}\n"
        f"• Estructura H4: *{dir_h4}* | Rango: {rango_h4}\n"
        f"• Estructura H1: *{dir_h1}* | Rango: {rango_h1}\n\n"
    )

    # ------------- CONTINUACIÓN SCALPING -------------
    if escenario == "scalping_continuacion":
        data = s_cont
        entrada = _safe_num(data.get("zona_reaccion", "—"))
        tp1 = _safe_num(data.get("tp1_rr", "1:1 (50% + BE)"))
        tp2 = _safe_num(data.get("tp2_rr", "1:2 (50%)"))
        sl = _safe_num(data.get("sl", "—"))

        txt = header
        txt += "🔷 *Escenario SCALPING de Continuación*\n\n"
        txt += (
            "Este escenario busca operar *a favor de la tendencia intradía (H1)*:\n"
            "1. Se toma como referencia el último HIGH/LOW relevante en M5.\n"
            "2. Se espera la ruptura de ese nivel para gatillar la entrada con BOS limpio.\n"
            "3. La operación respeta la dirección estructural de H1 y se ejecuta solo en zona válida.\n\n"
        )
        txt += f"📥 Punto de entrada estimado: *{entrada}*\n"
        txt += f"🎯 TP1 (1:1 + BE / parciales): *{tp1}*\n"
        txt += f"🎯 TP2 (1:2 objetivo completo): *{tp2}*\n"
        txt += f"🛡️ SL técnico: *{sl}*\n\n"
        txt += (
            "🔎 Gestión sugerida TESLABTC:\n"
            "• Mover a BE al alcanzar TP1.\n"
            "• Asegurar parciales en TP1 y dejar correr hacia TP2 si el contexto lo permite.\n"
            "• Evitar entradas si hay noticias fuertes o el precio está en zona de alta indecisión.\n"
        )
        return txt

    # ------------- CORRECCIÓN SCALPING -------------
    if escenario == "scalping_correccion":
        data = s_corr
        entrada = _safe_num(data.get("zona_reaccion", "—"))
        tp1 = _safe_num(data.get("tp1_rr", "1:1 (50% + BE)"))
        tp2 = _safe_num(data.get("tp2_rr", "1:2 (50%)"))
        sl = _safe_num(data.get("sl", "—"))

        txt = header
        txt += "🔷 *Escenario SCALPING de Corrección*\n\n"
        txt += (
            "Este escenario busca capturar movimientos *contra la tendencia intradía (H1)*:\n"
            "1. La estructura principal va en una dirección, pero se detecta extensión o agotamiento.\n"
            "2. Se usa el último HIGH/LOW de M5 como gatillo de corrección con BOS contra la tendencia.\n"
            "3. El riesgo es más alto al ir contra la dirección principal, por lo que se filtra más.\n\n"
        )
        txt += f"📥 Punto de entrada estimado: *{entrada}*\n"
        txt += f"🎯 TP1 (1:1 + BE / parciales): *{tp1}*\n"
        txt += f"🎯 TP2 (1:2 objetivo de corrección): *{tp2}*\n"
        txt += f"🛡️ SL técnico: *{sl}*\n\n"
        txt += (
            "⚠️ Al ser contra tendencia, este escenario debe filtrarse mejor:\n"
            "• Confirmar agotamiento (mechas largas, pérdida de fuerza, reacción en zona clave).\n"
            "• Reducir tamaño de posición si el contexto no es muy limpio.\n"
            "• Priorizar siempre las operaciones a favor de la estructura principal.\n"
        )
        return txt

    # ------------- SWING -------------
    if escenario == "swing":
        zona_premium = swing.get("premium_zone") or zonas.get("POI_H4", "—")
        zona_reac = swing.get("zona_reaccion") or zona_premium
        tp1 = _safe_num(swing.get("tp1_rr", "1:1 (BE)"))
        tp2 = _safe_num(swing.get("tp2_rr", "1:2 (50%)"))
        tp3 = _safe_num(swing.get("tp3_objetivo", "—"))
        sl = _safe_num(swing.get("sl", "—"))

        txt = header
        txt += "📈 *Escenario SWING TESLABTC*\n\n"
        txt += (
            "La lógica de SWING sigue la estructura de H4 e H1:\n"
            "1. Se identifica una zona PREMIUM en H4 (rango 61.8%–88.6% del último impulso).\n"
            "2. Se espera que el precio llegue a esa zona antes de buscar confirmación.\n"
            "3. En la zona premium, se requiere BOS claro en H1 a favor de la tendencia de H4 antes de validar el trade.\n\n"
        )
        txt += f"📥 Zona PREMIUM H4: *{zona_premium}*\n"
        txt += f"📥 Zona de reacción / gatillo: *{zona_reac}*\n"
        txt += f"🎯 TP1 referencia (1:1 + BE): *{tp1}*\n"
        txt += f"🎯 TP2 referencia (1:2 + parciales): *{tp2}*\n"
        txt += f"🎯 TP3 objetivo estructural (alto/bajo H4): *{tp3}*\n"
        txt += f"🛡️ SL técnico (H1): *{sl}*\n\n"
        txt += (
            "🧩 Idea general:\n"
            "• No se fuerza la entrada si el precio aún no ha llegado a la zona PREMIUM.\n"
            "• Una vez en zona, se espera BOS en H1 en la dirección de H4.\n"
            "• El trade suele tener mayor recorrido y exige más paciencia.\n"
        )
        return txt

    # Si llega aquí, escenario desconocido
    return header + "⚠️ Escenario no reconocido para contexto detallado."
