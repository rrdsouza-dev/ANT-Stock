from app.api.router import api_router
from fastapi import FastAPI

app = FastAPI(
    title="ANT Stock API",
    description="API inicial do WMS academico ANT Stock.",
    version="0.1.0",
)

# Todas as rotas de negocio entram pelo prefixo /api.
app.include_router(api_router, prefix="/api")


# Online
@app.get("/", tags=["Raiz"])
def inicio() -> dict[str, str]:
    return {"message": "ANT Stock API online"}


# Monitoramento app
@app.get("/health", tags=["Saude"])
def saude() -> dict[str, str]:
    return {"status": "ok"}
