# ============================================================
# ⚙️ routes/admin_extra.py — Funciones administrativas extra
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
import os, json
from utils.token_utils import TOKENS, _save_tokens, liberar_token

router = APIRouter(prefix="/admin", tags=["Admin Extra"])

ADMIN_FILE = "admin_data.json"

# ------------------------------------------------------------
# Persistencia simple de la clave de admin
# ------------------------------------------------------------
def _load_admin():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"password": "admin-teslabtc-kg"}

def _save_admin(data: dict):
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

ADMIN = _load_admin()

# ------------------------------------------------------------
# Cambiar contraseña de admin
# ------------------------------------------------------------
class ChangePasswordIn(BaseModel):
    current_password: constr(min_length=4)
    new_password: constr(min_length=6)

@router.post("/change_password")
def change_password(payload: ChangePasswordIn):
    current = payload.current_password.strip()
    new_pwd = payload.new_password.strip()

    if current != ADMIN["password"]:
        raise HTTPException(status_code=401, detail="Clave actual incorrecta.")

    ADMIN["password"] = new_pwd
    _save_admin(ADMIN)
    return {"estado": "✅", "mensaje": "Clave de admin actualizada correctamente."}

# ------------------------------------------------------------
# Eliminar usuario (por ID)
# ------------------------------------------------------------
class DeleteUserIn(BaseModel):
    user_id: str

@router.post("/delete_user")
def delete_user(payload: DeleteUserIn):
    user_id = str(payload.user_id)
    encontrados = [t for t, d in TOKENS.items() if d["usuario"] == user_id]
    if not encontrados:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin token activo.")
    for t in encontrados:
        liberar_token(t)
    _save_tokens()
    return {"estado": "✅", "mensaje": f"Usuario {user_id} y tokens eliminados correctamente."}
