# main.py
from fastapi import FastAPI
from routers.alertas_router import router as alertas_router

app = FastAPI(title="TESLABTC A.P. API")

# Prefijo "/alertas" para agrupar tus endpoints
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])

@app.get("/")
def root():
    return {"mensaje": "✨ TESLABTC A.P. API funcionando correctamente 🚀"}
