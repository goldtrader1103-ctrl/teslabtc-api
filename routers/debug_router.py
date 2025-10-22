# ============================================================
# 🧩 debug_router.py — Endpoint para sincronización BOT ↔ API
# ============================================================

from fastapi import APIRouter
import json, os

router = APIRouter()

@router.get("/debug/tokens")
def obtener_tokens():
    """Devuelve los tokens registrados para sincronización con el bot."""
    try:
        if not os.path.exists("tokens.json"):
            return {"tokens": [], "mensaje": "No existe tokens.json"}

        with open("tokens.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return {"tokens": data, "mensaje": "Tokens cargados correctamente"}
    except Exception as e:
        return {"tokens": [], "error": str(e)}
