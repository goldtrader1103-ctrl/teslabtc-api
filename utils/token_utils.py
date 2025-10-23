# ============================================================
# 🔐 token_utils.py — Gestión persistente de tokens TESLABTC.KG
#    - Token único por usuario
#    - Renovación: 30 días Premium desde activación
#    - After premium: 10 días Free (gracia)
#    - Eliminación automática tras 40 días desde activación original
# ============================================================

import json
import os
import uuid
from datetime import datetime, timedelta

TOKENS_FILE = "tokens.json"
TOKENS = {}  # estructura: token -> {usuario, fecha_activacion (iso), fecha_vencimiento (iso), dias_free}

# ------------------------------
# Persistencia
# ------------------------------
def _load_tokens():
    global TOKENS
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # convertir fechas a datetime
                for t, d in raw.items():
                    d["fecha_activacion"] = datetime.fromisoformat(d["fecha_activacion"])
                    d["fecha_vencimiento"] = datetime.fromisoformat(d["fecha_vencimiento"])
                TOKENS = raw
        else:
            TOKENS = {}
    except Exception:
        TOKENS = {}

def _save_tokens():
    serial = {}
    for t, d in TOKENS.items():
        serial[t] = {
            "usuario": d["usuario"],
            "fecha_activacion": d["fecha_activacion"].isoformat(),
            "fecha_vencimiento": d["fecha_vencimiento"].isoformat(),
            "dias_free": d.get("dias_free", 10)
        }
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(serial, f, indent=2, ensure_ascii=False)

# Inicializar
_load_tokens()

# ------------------------------
# Generar o renovar token (token único por usuario)
# ------------------------------
def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    """
    Crea un token para 'usuario' o renueva el existente.
    Retorna dict con estado, mensaje, token y vencimiento.
    """
    # buscar token existente por usuario
    for tok, info in TOKENS.items():
        if str(info.get("usuario")) == str(usuario):
            # renovar: actualizar fechas (manteniendo mismo token)
            ahora = datetime.now()
            info["fecha_activacion"] = ahora
            info["fecha_vencimiento"] = ahora + timedelta(days=dias_premium)
            info["dias_free"] = dias_free
            _save_tokens()
            return {
                "estado": "✅",
                "mensaje": "Token renovado correctamente",
                "token": tok,
                "vencimiento": info["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S")
            }

    # crear nuevo token
    nuevo = uuid.uuid4().hex[:16].upper()
    ahora = datetime.now()
    TOKENS[nuevo] = {
        "usuario": str(usuario),
        "fecha_activacion": ahora,
        "fecha_vencimiento": ahora + timedelta(days=dias_premium),
        "dias_free": dias_free
    }
    _save_tokens()
    return {
        "estado": "✅",
        "mensaje": "Token creado correctamente",
        "token": nuevo,
        "vencimiento": (ahora + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------
# Validar token (aplica reglas 30d premium, +10d free, luego eliminación)
# ------------------------------
def validar_token(token: str):
    """
    Devuelve dict:
      - estado: ✅ / ❌ / ⚠️
      - nivel: Premium | Free (si aplica)
      - usuario
      - expira
      - mensaje (opcional)
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

    # Grace free (post-premium)
    if vto < ahora <= (vto + timedelta(days=dias_free)):
        return {
            "estado": "✅",
            "nivel": "Free",
            "usuario": data["usuario"],
            "expira": vto.strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": "Token en periodo Free post-premium (gracia)."
        }

    # Expirado definitivamente -> eliminar
    TOKENS.pop(token, None)
    _save_tokens()
    return {"estado": "⚠️", "mensaje": "Token expirado definitivamente y eliminado."}

# ------------------------------
# Liberar token manualmente
# ------------------------------
def liberar_token(token: str):
    if token in TOKENS:
        TOKENS.pop(token, None)
        _save_tokens()
        return {"estado": "✅", "mensaje": "Token eliminado correctamente."}
    return {"estado": "⚠️", "mensaje": "Token no encontrado."}

# ------------------------------
# Listar tokens activos (para admin)
# ------------------------------
def listar_tokens():
    out = {}
    for t, d in TOKENS.items():
        out[t] = {
            "usuario": d["usuario"],
            "fecha_activacion": d["fecha_activacion"].strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_vencimiento": d["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S"),
            "dias_free": d.get("dias_free", 10)
        }
    return out

# ------------------------------
# Verificar vencimientos y limpiar (puedes invocar periódicamente)
# ------------------------------
def verificar_vencimientos():
    ahora = datetime.now()
    expirados = []
    for t, d in list(TOKENS.items()):
        if ahora > d["fecha_vencimiento"] + timedelta(days=d.get("dias_free", 10)):
            expirados.append(t)
            TOKENS.pop(t, None)
    if expirados:
        _save_tokens()
    return expirados
