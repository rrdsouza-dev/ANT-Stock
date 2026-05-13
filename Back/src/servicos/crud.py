from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlmodel import SQLModel

from src.nucleo.erros import ErroApp
from src.repositorios.base import RepositorioSQL

ModeloT = TypeVar("ModeloT", bound=SQLModel)


class ServicoCrud(Generic[ModeloT]):
    def __init__(self, repositorio: RepositorioSQL[ModeloT], nome_recurso: str) -> None:
        self.repositorio = repositorio
        self.nome_recurso = nome_recurso

    async def listar(
        self,
        *,
        inicio: int = 0,
        limite: int = 100,
        filtros: dict[str, Any] | None = None,
    ) -> list[ModeloT]:
        return await self.repositorio.listar(inicio=inicio, limite=min(limite, 200), filtros=filtros)

    async def buscar(self, item_id: UUID) -> ModeloT:
        item = await self.repositorio.buscar(item_id)
        if item is None:
            raise ErroApp(f"{self.nome_recurso} nao encontrado.", status_code=404, codigo="nao_encontrado")
        return item

    async def criar(self, dados: dict[str, Any]) -> ModeloT:
        return await self.repositorio.criar(dados)

    async def editar(self, item_id: UUID, dados: dict[str, Any]) -> ModeloT:
        item = await self.buscar(item_id)
        dados_limpos = {campo: valor for campo, valor in dados.items() if valor is not None}
        return await self.repositorio.editar(item, dados_limpos)

    async def remover(self, item_id: UUID) -> None:
        item = await self.buscar(item_id)
        await self.repositorio.remover(item)
