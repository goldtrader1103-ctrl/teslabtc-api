import os, json, uuid
from datetime import datetime, timedelta

# ✅ Ruta persistente (debes montar volumen en Fly en /app/data)
TOKENS_FILE = "/app/data/tokens.json"
TOKENS = {}

def _ensure_dir():
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)

def _load_tokens():
    global TOKENS
    _ensure_dir()
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # normalizar fechas
        for t, d in raw.items():
            d["fecha_activacion"] = datetime.fromisoformat(d["fecha_activacion"])
            d["fecha_vencimiento"] = datetime.fromisoformat(d["fecha_vencimiento"])
        TOKENS = raw
    else:
        TOKENS = {}

def _save_tokens():
    _ensure_dir()
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

# 🔁 Inicializa al importar el módulo
_load_tokens()

def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    # renovar si ya existe
    for tok, info in TOKENS.items():
        if str(info.get("usuario")) == str(usuario):
            ahora = datetime.now()
            info["fecha_activacion"] = ahora
            info["fecha_vencimiento"] = ahora + timedelta(days=dias_premium)
            info["dias_free"] = dias_free
            _save_tokens()
            return {
                "estado": "✅",
                "mensaje": "Token renovado correctamente",
                "token": tok,
                "nivel": "Premium",
                "vencimiento": info["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S")
            }

    # crear nuevo
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
        "nivel": "Premium",
        "vencimiento": (ahora + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
    }

def validar_token(token: str):
    ahora = datetime.now()
    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "nivel": "Free", "mensaje": "Token inválido o inexistente."}

    vto = data["fecha_vencimiento"]
    dias_free = data.get("dias_free", 10)

    if ahora <= vto:
        return {"estado": "✅", "nivel": "Premium", "usuario": data["usuario"], "expira": vto.strftime("%Y-%m-%d %H:%M:%S")}

    if vto < ahora <= (vto + timedelta(days=dias_free)):
        return {"estado": "✅", "nivel": "Free", "usuario": data["usuario"], "expira": vto.strftime("%Y-%m-%d %H:%M:%S"),
                "mensaje": "Token en periodo Free post-premium (gracia)."}

    # expirado definitivo
    TOKENS.pop(token, None)
    _save_tokens()
    return {"estado": "❌", "nivel": "Free", "mensaje": "Token expirado definitivo."}

def liberar_token(token: str):
    if token in TOKENS:
        TOKENS.pop(token, None)
        _save_tokens()
        return {"estado": "✅", "mensaje": "Token liberado"}
    return {"estado": "⚠️", "mensaje": "Token no encontrado"}

def listar_tokens():
    return {t: {**d, "fecha_activacion": d["fecha_activacion"].isoformat(),
                   "fecha_vencimiento": d["fecha_vencimiento"].isoformat()}
            for t, d in TOKENS.items()}

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
