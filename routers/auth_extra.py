# ============================================================
# 🔐 routes/auth_extra.py — Logout de usuarios
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.token_utils import TOKENS, _save_tokens

router = APIRouter(prefix="/auth", tags=["Auth Extra"])

class LogoutIn(BaseModel):
    user_id: str

@router.post("/logout")
def logout(payload: LogoutIn):
    user_id = str(payload.user_id)
    encontrados = [t for t, d in TOKENS.items() if d["usuario"] == user_id]
    if not encontrados:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin sesión activa.")
    for t in encontrados:
        TOKENS.pop(t, None)
    _save_tokens()
    return {"estado": "✅", "mensaje": f"Sesión de {user_id} cerrada correctamente."}
