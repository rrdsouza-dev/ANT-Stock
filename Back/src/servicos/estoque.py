from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modelos import Categoria, Estoque, ItemPedido, Localizacao, Movimentacao, Pedido, Produto, TipoMovimentacao
from src.nucleo.erros import ErroApp
from src.repositorios import (
    RepositorioCategoria,
    RepositorioEstoque,
    RepositorioItemPedido,
    RepositorioLocalizacao,
    RepositorioMovimentacao,
    RepositorioPedido,
    RepositorioProduto,
)
from src.servicos.crud import ServicoCrud


class ServicoEstoque:
    def __init__(self, sessao: AsyncSession) -> None:
        self.repositorio_estoque = RepositorioEstoque(sessao)
        self.repositorio_itens_pedido = RepositorioItemPedido(sessao)

        self.categorias = ServicoCrud[Categoria](RepositorioCategoria(sessao), "Categoria")
        self.localizacoes = ServicoCrud[Localizacao](RepositorioLocalizacao(sessao), "Localizacao")
        self.produtos = ServicoCrud[Produto](RepositorioProduto(sessao), "Produto")
        self.estoque = ServicoCrud[Estoque](self.repositorio_estoque, "Estoque")
        self.movimentacoes = ServicoCrud[Movimentacao](RepositorioMovimentacao(sessao), "Movimentacao")
        self.pedidos = ServicoCrud[Pedido](RepositorioPedido(sessao), "Pedido")
        self.itens_pedido = ServicoCrud[ItemPedido](self.repositorio_itens_pedido, "Item do pedido")

    async def estoque_do_produto(self, produto_id: UUID) -> list[Estoque]:
        return await self.estoque.listar(filtros={"produto_id": produto_id})

    async def itens_do_pedido(self, pedido_id: UUID) -> list[ItemPedido]:
        return await self.repositorio_itens_pedido.por_pedido(pedido_id)

    async def registrar_movimentacao(self, dados: dict[str, Any]) -> Movimentacao:
        await self._ajustar_estoque(dados)
        return await self.movimentacoes.criar(dados)

    async def _ajustar_estoque(self, dados: dict[str, Any]) -> None:
        tipo = dados["tipo"]
        produto_id = dados["produto_id"]
        quantidade = dados["quantidade"]
        localizacao_id = dados.get("destino_id") if tipo == TipoMovimentacao.ENTRADA else dados.get("origem_id")

        saldo = await self.repositorio_estoque.por_produto_local(produto_id, localizacao_id)
        if tipo == TipoMovimentacao.ENTRADA:
            if saldo is None:
                await self.estoque.criar(
                    {"produto_id": produto_id, "localizacao_id": localizacao_id, "quantidade": quantidade}
                )
                return
            await self.estoque.editar(saldo.id, {"quantidade": saldo.quantidade + quantidade})
            return

        if saldo is None or saldo.quantidade < quantidade:
            raise ErroApp("Estoque insuficiente para a saida.", status_code=409, codigo="estoque_insuficiente")
        await self.estoque.editar(saldo.id, {"quantidade": saldo.quantidade - quantidade})
