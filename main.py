from fastapi import FastAPI
from routers.dashboard_router import router as dashboard_router
from routers.ny_router import router as ny_router
# Si tienes confirmaciones_router, descomenta la siguiente línea:
# from routers.confirmaciones_router import router as confirmaciones_router

app = FastAPI(
    title="TESLABTC A.P. API",
    version="2.1",
    description="Price Action Puro — BTCUSDT NY Session"
)

@app.get("/", tags=["Root"])
def root():
    return {"status": "online", "service": "TESLABTC A.P API", "session": "NY 07:00–13:30 COL"}

# Routers
app.include_router(ny_router)
app.include_router(dashboard_router)
# app.include_router(confirmaciones_router)
