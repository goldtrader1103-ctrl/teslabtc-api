# ============================================================
# ⚙️ TESLABTC.KG — token_utils.py (versión consolidada 100%)
# ============================================================

import os, json, uuid
from datetime import datetime, timedelta

# ============================================================
# 📁 Archivos persistentes (montados en Fly.io)
# ============================================================
TOKENS_FILE = "/app/data/tokens.json"
USERS_FILE = "/app/data/usuarios.json"
TOKENS = {}

# ============================================================
# 🧩 Utilidades internas
# ============================================================
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

# ============================================================
# 🧠 Generar o renovar token
# ============================================================
def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    """
    Crea o renueva token para un usuario Premium.
    Guarda token en tokens.json y usuario en usuarios.json
    """
    ahora = datetime.now()

    # Si ya existe token, renovar fechas
    for tok, info in TOKENS.items():
        if str(info.get("usuario")) == str(usuario):
            info["fecha_activacion"] = ahora
            info["fecha_vencimiento"] = ahora + timedelta(days=dias_premium)
            info["dias_free"] = dias_free
            _save_tokens()
            _guardar_usuario_premium(usuario, ahora, dias_premium)
            return {
                "estado": "✅",
                "mensaje": "Token renovado correctamente",
                "token": tok,
                "nivel": "Premium",
                "vencimiento": info["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S")
            }

    # Si no existe, crear nuevo
    nuevo = uuid.uuid4().hex[:16].upper()
    TOKENS[nuevo] = {
        "usuario": str(usuario),
        "fecha_activacion": ahora,
        "fecha_vencimiento": ahora + timedelta(days=dias_premium),
        "dias_free": dias_free
    }
    _save_tokens()
    _guardar_usuario_premium(usuario, ahora, dias_premium)
    return {
        "estado": "✅",
        "mensaje": "Token creado correctamente",
        "token": nuevo,
        "nivel": "Premium",
        "vencimiento": (ahora + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# 💾 Guardar usuario Premium
# ============================================================
def _guardar_usuario_premium(usuario: str, fecha_inicio: datetime, dias_premium: int):
    """
    Registra o actualiza un usuario Premium en /app/data/usuarios.json
    """
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        usuarios = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                usuarios = json.load(f)

        usuarios[str(usuario)] = {
            "nivel": "Premium",
            "fecha_activacion": fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_vencimiento": (fecha_inicio + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)

        print(f"✅ Usuario {usuario} guardado/actualizado en usuarios.json")

    except Exception as e:
        print(f"⚠️ Error guardando usuario Premium: {e}")

# ============================================================
# 🔎 Validar token
# ============================================================
def validar_token(token: str):
    ahora = datetime.now()
    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "nivel": "Free", "mensaje": "Token inválido o inexistente."}

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

    # Expirado definitivo
    TOKENS.pop(token, None)
    _save_tokens()
    return {"estado": "❌", "nivel": "Free", "mensaje": "Token expirado definitivo."}

# ============================================================
# ♻️ Liberar token
# ============================================================
def liberar_token(token: str):
    if token in TOKENS:
        TOKENS.pop(token, None)
        _save_tokens()
        return {"estado": "✅", "mensaje": "Token liberado"}
    return {"estado": "⚠️", "mensaje": "Token no encontrado"}

# ============================================================
# 📋 Listar tokens
# ============================================================
def listar_tokens():
    return {
        t: {
            **d,
            "fecha_activacion": d["fecha_activacion"].isoformat(),
            "fecha_vencimiento": d["fecha_vencimiento"].isoformat()
        }
        for t, d in TOKENS.items()
    }

# ============================================================
# ⏰ Verificar vencimientos
# ============================================================
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
# ============================================================
# ⚙️ TESLABTC.KG — token_utils.py (versión consolidada 100%)
# ============================================================

import os, json, uuid
from datetime import datetime, timedelta

# ============================================================
# 📁 Archivos persistentes (montados en Fly.io)
# ============================================================
TOKENS_FILE = "/app/data/tokens.json"
USERS_FILE = "/app/data/usuarios.json"
TOKENS = {}

# ============================================================
# 🧩 Utilidades internas
# ============================================================
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

# ============================================================
# 🧠 Generar o renovar token
# ============================================================
def generar_token(usuario: str, dias_premium: int = 30, dias_free: int = 10):
    """
    Crea o renueva token para un usuario Premium.
    Guarda token en tokens.json y usuario en usuarios.json
    """
    ahora = datetime.now()

    # Si ya existe token, renovar fechas
    for tok, info in TOKENS.items():
        if str(info.get("usuario")) == str(usuario):
            info["fecha_activacion"] = ahora
            info["fecha_vencimiento"] = ahora + timedelta(days=dias_premium)
            info["dias_free"] = dias_free
            _save_tokens()
            _guardar_usuario_premium(usuario, ahora, dias_premium)
            return {
                "estado": "✅",
                "mensaje": "Token renovado correctamente",
                "token": tok,
                "nivel": "Premium",
                "vencimiento": info["fecha_vencimiento"].strftime("%Y-%m-%d %H:%M:%S")
            }

    # Si no existe, crear nuevo
    nuevo = uuid.uuid4().hex[:16].upper()
    TOKENS[nuevo] = {
        "usuario": str(usuario),
        "fecha_activacion": ahora,
        "fecha_vencimiento": ahora + timedelta(days=dias_premium),
        "dias_free": dias_free
    }
    _save_tokens()
    _guardar_usuario_premium(usuario, ahora, dias_premium)
    return {
        "estado": "✅",
        "mensaje": "Token creado correctamente",
        "token": nuevo,
        "nivel": "Premium",
        "vencimiento": (ahora + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# 💾 Guardar usuario Premium
# ============================================================
def _guardar_usuario_premium(usuario: str, fecha_inicio: datetime, dias_premium: int):
    """
    Registra o actualiza un usuario Premium en /app/data/usuarios.json
    """
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        usuarios = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                usuarios = json.load(f)

        usuarios[str(usuario)] = {
            "nivel": "Premium",
            "fecha_activacion": fecha_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_vencimiento": (fecha_inicio + timedelta(days=dias_premium)).strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)

        print(f"✅ Usuario {usuario} guardado/actualizado en usuarios.json")

    except Exception as e:
        print(f"⚠️ Error guardando usuario Premium: {e}")

# ============================================================
# 🔎 Validar token
# ============================================================
def validar_token(token: str):
    ahora = datetime.now()
    data = TOKENS.get(token)
    if not data:
        return {"estado": "❌", "nivel": "Free", "mensaje": "Token inválido o inexistente."}

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

    # Expirado definitivo
    TOKENS.pop(token, None)
    _save_tokens()
    return {"estado": "❌", "nivel": "Free", "mensaje": "Token expirado definitivo."}

# ============================================================
# ♻️ Liberar token
# ============================================================
def liberar_token(token: str):
    if token in TOKENS:
        TOKENS.pop(token, None)
        _save_tokens()
        return {"estado": "✅", "mensaje": "Token liberado"}
    return {"estado": "⚠️", "mensaje": "Token no encontrado"}

# ============================================================
# 📋 Listar tokens
# ============================================================
def listar_tokens():
    return {
        t: {
            **d,
            "fecha_activacion": d["fecha_activacion"].isoformat(),
            "fecha_vencimiento": d["fecha_vencimiento"].isoformat()
        }
        for t, d in TOKENS.items()
    }

# ============================================================
# ⏰ Verificar vencimientos
# ============================================================
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
