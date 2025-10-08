from fastapi import FastAPI
from routers.alertas_router import router as alertas_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.ny_router import router as ny_router
from routers.dashboard_router import router as dashboard_router

app = FastAPI(title="TESLABTC A.P", description="API completa para estrategia TESLABTC A.P.")

@app.get("/")
def root():
    return {"message": "🚀 TESLABTC A.P API online"}

app.include_router(alertas_router)
app.include_router(confirmaciones_router)
app.include_router(ny_router)
app.include_router(dashboard_router)
