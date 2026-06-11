from uuid import UUID

from sqlalchemy import select
from sqlmodel import col

from src.modelos import Categoria, Deposito, Estoque, Localizacao, Movimentacao, Produto, UsuarioDeposito
from src.repositorios.base import RepositorioSQL


class RepositorioDeposito(RepositorioSQL[Deposito]):
    modelo = Deposito

    async def por_usuario(self, usuario_id: UUID, inicio: int = 0, limite: int = 100) -> list[Deposito]:
        consulta = (
            select(Deposito)
            .join(UsuarioDeposito, UsuarioDeposito.deposito_id == Deposito.id)
            .where(col(UsuarioDeposito.usuario_id) == usuario_id)
            .where(col(Deposito.ativo).is_(True))
            .offset(inicio)
            .limit(limite)
        )
        resultado = await self.sessao.execute(consulta)
        return list(resultado.scalars().unique().all())


class RepositorioCategoria(RepositorioSQL[Categoria]):
    modelo = Categoria


class RepositorioLocalizacao(RepositorioSQL[Localizacao]):
    modelo = Localizacao


class RepositorioProduto(RepositorioSQL[Produto]):
    modelo = Produto

    async def por_codigo(self, deposito_id: UUID, codigo: str) -> Produto | None:
        consulta = select(Produto).where(
            col(Produto.deposito_id) == deposito_id,
            col(Produto.codigo) == codigo,
            col(Produto.ativo).is_(True),
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()


class RepositorioEstoque(RepositorioSQL[Estoque]):
    modelo = Estoque

    async def por_produto_local(
        self,
        deposito_id: UUID,
        produto_id: UUID,
        localizacao_id: UUID | None,
    ) -> Estoque | None:
        consulta = select(Estoque).where(
            col(Estoque.deposito_id) == deposito_id,
            col(Estoque.produto_id) == produto_id,
        )
        if localizacao_id is None:
            consulta = consulta.where(col(Estoque.localizacao_id).is_(None))
        else:
            consulta = consulta.where(col(Estoque.localizacao_id) == localizacao_id)
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()


class RepositorioMovimentacao(RepositorioSQL[Movimentacao]):
    modelo = Movimentacao
