from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Importar routers
from routers.dashboard_router import router as dashboard_router
from routers.alertas_router import router as alertas_router

# Crear aplicación
app = FastAPI(
    title="TESLABTC A.P. Dashboard",
    description="API unificada TESLABTC A.P. con análisis, alertas y sonido de confirmación.",
    version="2.0.0"
)

# Permitir acceso desde cualquier origen (útil para conectar con tu GPT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta estática (para servir el sonido beep.mp3)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(dashboard_router)
app.include_router(alertas_router)

@app.get("/")
def root():
    return {
        "status": "✅ TESLABTC A.P. API en línea",
        "message": "Bienvenida a la API TESLABTC — lista para análisis, alertas y sonido de confirmación.",
        "endpoints": ["/dashboard", "/alertas"]
    }

# Ejecutar localmente
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
