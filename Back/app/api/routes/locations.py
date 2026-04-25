from fastapi import APIRouter


# Rotas do CRUD de localizacoes fisicas do armazem.
router = APIRouter(prefix="/localizacoes", tags=["Localizacoes"])


@router.get("")
def list_locations() -> dict[str, str]:
    # Lista os enderecos ou setores de armazenagem.
    return {"message": "Endpoint para listar localizacoes"}


@router.get("/{location_id}")
def get_location(location_id: int) -> dict[str, str | int]:
    # Busca uma localizacao especifica pelo identificador.
    return {
        "message": "Endpoint para buscar uma localizacao",
        "location_id": location_id,
    }


@router.post("")
def create_location() -> dict[str, str]:
    # Cadastra uma nova localizacao dentro do armazem.
    return {"message": "Endpoint para criar localizacao"}


@router.put("/{location_id}")
def update_location(location_id: int) -> dict[str, str | int]:
    # Atualiza os dados de uma localizacao existente.
    return {
        "message": "Endpoint para atualizar localizacao",
        "location_id": location_id,
    }


@router.delete("/{location_id}")
def delete_location(location_id: int) -> dict[str, str | int]:
    # Remove uma localizacao do cadastro.
    return {
        "message": "Endpoint para remover localizacao",
        "location_id": location_id,
    }
