from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routers.dashboard_router import router as dashboard_router
from routers.alertas_router import router as alertas_router

app = FastAPI(
    title="TESLABTC A.P. Dashboard",
    description="API TESLABTC A.P. — acción del precio pura con confirmaciones, alertas y sesión NY.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(alertas_router, tags=["Alertas"])

@app.get("/")
def root():
    return {
        "message": "🚀 TESLABTC A.P API online",
        "status": "✅",
        "endpoints": ["/estado_general", "/alertas", "/static/beep.mp3"]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
