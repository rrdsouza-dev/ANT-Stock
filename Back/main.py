from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="ANT Stock API",
    description="API inicial do WMS academico ANT Stock.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Raiz"])
def inicio() -> dict[str, str]:
    return {"message": "ANT Stock API online"}


@app.get("/health", tags=["Saude"])
def saude() -> dict[str, str]:
    return {"status": "ok"}
