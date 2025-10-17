# ============================================================
# 🔐 token_utils.py — Gestión de tokens TESLABTC.KG
# ============================================================

from datetime import datetime, timedelta
import uuid

# Base temporal en memoria (puedes reemplazar por BD más adelante)
TOKENS = {}

# ------------------------------------------------------------
# 🎟️ Generar un nuevo token
# ------------------------------------------------------------
def generar_token(nivel="Free", dias=10):
    token = f"{nivel.upper()}-{uuid.uuid4().hex[:10].upper()}"
    expiracion = datetime.now() + timedelta(days=dias)
    TOKENS[token] = {"nivel": nivel, "expira": expiracion}
    return token

# ------------------------------------------------------------
# ✅ Validar token existente
# ------------------------------------------------------------
def validar_token(token):
    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "mensaje": "Token inválido o no encontrado."}
    if datetime.now() > data["expira"]:
        return {"estado": "⚠️", "mensaje": "Token expirado."}
    return {
        "estado": "✅",
        "nivel": data["nivel"],
        "expira": data["expira"].strftime("%d/%m/%Y %H:%M:%S")
    }

# ------------------------------------------------------------
# 🧹 Verificar y limpiar tokens expirados
# ------------------------------------------------------------
def verificar_vencimientos():
    expirados = []
    for token, info in list(TOKENS.items()):
        if datetime.now() > info["expira"]:
            expirados.append(token)
            TOKENS.pop(token, None)
    return expirados

# ------------------------------------------------------------
# 🗑️ Liberar (eliminar) token manualmente
# ------------------------------------------------------------
def liberar_token(token):
    if token in TOKENS:
        TOKENS.pop(token)
        return {"estado": "✅", "mensaje": "Token eliminado correctamente."}
    return {"estado": "⚠️", "mensaje": "El token no existe o ya fue eliminado."}

# ------------------------------------------------------------
# 📋 Obtener listado de tokens activos
# ------------------------------------------------------------
def listar_tokens():
    activos = {}
    for t, d in TOKENS.items():
        activos[t] = {
            "nivel": d["nivel"],
            "expira": d["expira"].strftime("%d/%m/%Y %H:%M:%S")
        }
    return activos
