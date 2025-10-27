import json
import os

DB_PATH = "/app/data/usuarios.json"

def cargar_usuarios():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def validar_token_api(token):
    usuarios = cargar_usuarios()
    for uid, info in usuarios.items():
        if info.get("token") == token:
            if info.get("nivel") == "Premium":
                return {"valido": True, "nivel": "Premium"}
            else:
                return {"valido": True, "nivel": "Free"}
    return {"valido": False, "nivel": "Free"}
