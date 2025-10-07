from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Importar routers TESLABTC
from routers.dashboard_router import router as dashboard_router
from routers.alertas_router import router as alertas_router

# Crear app principal
app = FastAPI(
    title="TESLABTC A.P. Dashboard",
    description="API completa TESLABTC A.P — análisis, alertas y sonido de confirmación en tiempo real.",
    version="2.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta estática para sonido
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])

# Endpoint raíz
@app.get("/")
def root():
    return {
        "message": "🚀 TESLABTC A.P API online",
        "status": "✅ Sistema operativo",
        "rutas": ["/dashboard", "/alertas", "/static/beep.mp3"]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
