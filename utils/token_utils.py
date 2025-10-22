# ============================================================
# 🔐 token_utils.py — Validación simple TESLABTC.KG
# Integrado con BOT: los tokens se generan y administran desde el BOT.
# Este archivo solo valida y mantiene estructura temporal (sin tokens.json)
# ============================================================

from datetime import datetime, timedelta
import uuid

# Estructura temporal en memoria (sin archivo físico)
TOKENS = {}  # token -> {usuario, nivel, fecha_vencimiento}

# ============================================================
# 🧩 GENERAR TOKEN — (solo usado cuando el BOT llama a /admin/create_token)
# ============================================================
def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    """
    Genera un token nuevo o renueva el existente (sin archivo físico).
    """
    ahora = datetime.now()
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
    """
    Devuelve dict:
      - estado: ✅ / ❌ / ⚠️
      - nivel: Premium | Free (si aplica)
      - usuario
      - expira
    """
    if not token:
        return {"estado": "❌", "mensaje": "Token faltante."}

    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "mensaje": "Token inválido o no encontrado."}

    ahora = datetime.now()
    vto = data["fecha_vencimiento"]
    dias_free = data.get("dias_free", 10)

    # Premium activo
    if ahora <= vto:
        return {
            "estado": "✅",
            "nivel": "Premium",
            "usuario": data["usuario"],
            "expira": vto.strftime("%Y-%m-%d %H:%M:%S")
        }

    # Free post-premium
    if vto < ahora <= (vto + timedelta(days=dias_free)):
        return {
            "estado": "✅",
            "nivel": "Free",
            "usuario": data["usuario"],
            "expira": vto.strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": "Token en periodo Free post-premium (gracia)."
        }

    # Expirado
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
# 🧾 LISTAR TOKENS (para debug opcional)
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
