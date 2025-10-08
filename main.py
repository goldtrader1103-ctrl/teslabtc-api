from fastapi import FastAPI
from routers.dashboard_router import router as dashboard_router
from routers.confirmaciones_router import router as confirmaciones_router
from routers.ny_router import router as ny_router
from routers.alertas_router import router as alertas_router

app = FastAPI(title="TESLABTC A.P — Price Action Pura", version="1.0.0")

@app.get("/")
def root():
    return {"message": "🚀 TESLABTC A.P API (PA pura) online — NY 07:00–13:30 COL"}

app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(confirmaciones_router, tags=["confirmaciones"])
app.include_router(ny_router, tags=["ny-session"])
app.include_router(alertas_router, tags=["alertas"])
