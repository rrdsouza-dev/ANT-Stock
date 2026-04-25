from fastapi import FastAPI

from app.api.router import api_router


# Inicializa a aplicacao principal do backend.
app = FastAPI(
    title="ANT Stock API",
    description="API inicial do WMS academico ANT Stock.",
    version="0.1.0",
)

# Centraliza todas as rotas de negocio em um unico prefixo base.
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Raiz"])
def read_root() -> dict[str, str]:
    # Endpoint basico para confirmar que a API subiu corretamente.
    return {"message": "ANT Stock API online"}


@app.get("/health", tags=["Saude"])
def health_check() -> dict[str, str]:
    # Endpoint simples de saude para testes e monitoramento.
    return {"status": "ok"}
