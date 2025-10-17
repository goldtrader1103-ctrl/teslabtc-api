# utils/auth_utils.py
import datetime
from typing import Dict

# Almacenamiento en memoria para estadísticas de uso
uso_usuarios: Dict[str, Dict] = {}


# ============================================================
# REGISTRAR USO DEL SISTEMA
# ============================================================
def registrar_uso(usuario_id: str) -> None:
    """
    Registra el uso del sistema por un usuario (último acceso y contador).
    """
    ahora = datetime.datetime.utcnow()
    if usuario_id not in uso_usuarios:
        uso_usuarios[usuario_id] = {"veces": 1, "ultimo_uso": ahora}
    else:
        uso_usuarios[usuario_id]["veces"] += 1
        uso_usuarios[usuario_id]["ultimo_uso"] = ahora


# ============================================================
# OBTENER USO DEL SISTEMA
# ============================================================
def obtener_uso(usuario_id: str) -> Dict:
    """
    Devuelve el número de veces que un usuario ha usado el sistema y la fecha del último uso.
    """
    if usuario_id in uso_usuarios:
        return uso_usuarios[usuario_id]
    else:
        return {"veces": 0, "ultimo_uso": None}


# ============================================================
# LIMPIAR USUARIOS INACTIVOS
# ============================================================
def limpiar_inactivos(minutos: int = 120) -> None:
    """
    Elimina usuarios que no han usado el sistema en un rango de tiempo dado.
    """
    ahora = datetime.datetime.utcnow()
    inactivos = [
        user for user, data in uso_usuarios.items()
        if data["ultimo_uso"] and (ahora - data["ultimo_uso"]).total_seconds() > minutos * 60
    ]
    for user in inactivos:
        del uso_usuarios[user]
        print(f"🧹 Usuario inactivo eliminado: {user}")
