# ============================================================
# 🔐 token_utils.py — Validación simple TESLABTC.KG
# Integrado con BOT: los tokens se generan y administran desde el BOT.
# Esta versión no usa archivo físico (solo memoria temporal en contenedor)
# ============================================================

from datetime import datetime, timedelta
import uuid

# Estructura temporal en memoria (sin archivo físico)
TOKENS = {}  # token -> {usuario, nivel, fecha_vencimiento, dias_free}

# ============================================================
# 🧩 GENERAR TOKEN
# ============================================================
def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    """Genera o renueva un token temporal (sin archivo físico)."""
    ahora = datetime.now()

    # Si ya existe un token para el usuario, se renueva
    for t, d in TOKENS.items():
        if d["usuario"] == str(usuario):
            d["fecha_vencimiento"] = ahora + timedelta(days=dias_premium)
            d["nivel"] = "Premium"
            return {
                "estado": "✅",
                "mensaje": "Token renovado correctamente",
                "token": t,
                "vencimiento": d["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S")
            }

    # Si no existe, se crea nuevo
    token = uuid.uuid4().hex[:16].upper()
    TOKENS[token] = {
        "usuario": str(usuario),
        "nivel": "Premium",
        "fecha_activacion": ahora,
        "fecha_vencimiento": ahora + timedelta(days=dias_premium),
        "dias_free": dias_free
    }

    return {
        "estado": "✅",
        "mensaje": "Token creado correctamente",
        "token": token,
        "vencimiento": (ahora + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# 🔎 VALIDAR TOKEN
# ============================================================
def validar_token(token: str):
    """Valida el token y devuelve su nivel (Premium, Free o Expirado)."""
    if not token:
        return {"estado": "❌", "mensaje": "Token faltante."}

    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "mensaje": "Token inválido o no encontrado."}

    ahora = datetime.now()
    vto = data["fecha_vencimiento"]
    dias_free = data.get("dias_free", 10)

    if ahora <= vto:
        return {
            "estado": "✅",
            "nivel": "Premium",
            "usuario": data["usuario"],
            "expira": vto.strftime("%Y-%m-%d %H:%M:%S")
        }

    if vto < ahora <= (vto + timedelta(days=dias_free)):
        return {
            "estado": "✅",
            "nivel": "Free",
            "usuario": data["usuario"],
            "expira": vto.strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": "Token en periodo Free post-premium (gracia)."
        }

    TOKENS.pop(token, None)
    return {"estado": "⚠️", "mensaje": "Token expirado definitivamente y eliminado."}

# ============================================================
# 🧹 LIBERAR TOKEN
# ============================================================
def liberar_token(token: str):
    if token in TOKENS:
        TOKENS.pop(token, None)
        return {"estado": "✅", "mensaje": "Token eliminado correctamente."}
    return {"estado": "⚠️", "mensaje": "Token no encontrado."}

# ============================================================
# 🧾 LISTAR TOKENS (solo para debug)
# ============================================================
def listar_tokens():
    out = {}
    for t, d in TOKENS.items():
        out[t] = {
            "usuario": d["usuario"],
            "nivel": d["nivel"],
            "fecha_vencimiento": d["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S"),
        }
    return out

# ============================================================
# 🧩 VERIFICAR VENCIMIENTOS
# ============================================================
def verificar_vencimientos():
    ahora = datetime.now()
    expirados = []
    for t, d in list(TOKENS.items()):
        if ahora > d["fecha_vencimiento"] + timedelta(days=d.get("dias_free", 10)):
            expirados.append(t)
            TOKENS.pop(t, None)
    return expirados
