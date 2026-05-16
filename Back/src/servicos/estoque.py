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
    RepositorioUsuarioDeposito,
)
from src.servicos.crud import ServicoCrud


class ServicoEstoque:
    def __init__(self, sessao: AsyncSession) -> None:
        self.repositorio_estoque = RepositorioEstoque(sessao)
        self.repositorio_itens_pedido = RepositorioItemPedido(sessao)
        self.usuario_depositos = RepositorioUsuarioDeposito(sessao)

        self.categorias = ServicoCrud[Categoria](RepositorioCategoria(sessao), "Categoria")
        self.localizacoes = ServicoCrud[Localizacao](RepositorioLocalizacao(sessao), "Localizacao")
        self.produtos = ServicoCrud[Produto](RepositorioProduto(sessao), "Produto")
        self.estoque = ServicoCrud[Estoque](self.repositorio_estoque, "Estoque")
        self.movimentacoes = ServicoCrud[Movimentacao](RepositorioMovimentacao(sessao), "Movimentacao")
        self.pedidos = ServicoCrud[Pedido](RepositorioPedido(sessao), "Pedido")
        self.itens_pedido = ServicoCrud[ItemPedido](self.repositorio_itens_pedido, "Item do pedido")

    async def verificar_acesso(self, usuario_id: UUID, deposito_id: UUID) -> bool:
        return await self.usuario_depositos.existe(usuario_id, deposito_id)

    async def _exigir_acesso(self, usuario_id: UUID, deposito_id: UUID) -> None:
        if not await self.verificar_acesso(usuario_id, deposito_id):
            raise ErroApp("Sem acesso a este deposito", status_code=403, codigo="sem_acesso_deposito")

    async def _buscar_no_deposito(self, crud: ServicoCrud[Any], item_id: UUID, deposito_id: UUID) -> Any:
        item = await crud.buscar(item_id)
        if getattr(item, "deposito_id", None) != deposito_id:
            raise ErroApp(f"{crud.nome_recurso} nao encontrado.", status_code=404, codigo="nao_encontrado")
        return item

    async def _criar_no_deposito(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        crud: ServicoCrud[Any],
        dados: dict[str, Any],
    ) -> Any:
        await self._exigir_acesso(usuario_id, deposito_id)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados["deposito_id"] = deposito_id
        return await crud.criar(dados)

    async def _editar_no_deposito(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        crud: ServicoCrud[Any],
        item_id: UUID,
        dados: dict[str, Any],
    ) -> Any:
        await self._exigir_acesso(usuario_id, deposito_id)
        item = await self._buscar_no_deposito(crud, item_id, deposito_id)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados_limpos = {campo: valor for campo, valor in dados.items() if valor is not None}
        return await crud.repositorio.editar(item, dados_limpos)

    async def _remover_no_deposito(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        crud: ServicoCrud[Any],
        item_id: UUID,
    ) -> None:
        await self._exigir_acesso(usuario_id, deposito_id)
        item = await self._buscar_no_deposito(crud, item_id, deposito_id)
        await crud.repositorio.remover(item)

    async def listar_categorias(
        self, usuario_id: UUID, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Categoria]:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self.categorias.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_categoria(self, usuario_id: UUID, deposito_id: UUID, categoria_id: UUID) -> Categoria:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.categorias, categoria_id, deposito_id)

    async def criar_categoria(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Categoria:
        return await self._criar_no_deposito(usuario_id, deposito_id, self.categorias, dados)

    async def editar_categoria(
        self, usuario_id: UUID, deposito_id: UUID, categoria_id: UUID, dados: dict[str, Any]
    ) -> Categoria:
        return await self._editar_no_deposito(usuario_id, deposito_id, self.categorias, categoria_id, dados)

    async def remover_categoria(self, usuario_id: UUID, deposito_id: UUID, categoria_id: UUID) -> None:
        await self._remover_no_deposito(usuario_id, deposito_id, self.categorias, categoria_id)

    async def listar_localizacoes(
        self, usuario_id: UUID, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Localizacao]:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self.localizacoes.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_localizacao(self, usuario_id: UUID, deposito_id: UUID, localizacao_id: UUID) -> Localizacao:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.localizacoes, localizacao_id, deposito_id)

    async def criar_localizacao(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Localizacao:
        return await self._criar_no_deposito(usuario_id, deposito_id, self.localizacoes, dados)

    async def editar_localizacao(
        self, usuario_id: UUID, deposito_id: UUID, localizacao_id: UUID, dados: dict[str, Any]
    ) -> Localizacao:
        return await self._editar_no_deposito(usuario_id, deposito_id, self.localizacoes, localizacao_id, dados)

    async def remover_localizacao(self, usuario_id: UUID, deposito_id: UUID, localizacao_id: UUID) -> None:
        await self._remover_no_deposito(usuario_id, deposito_id, self.localizacoes, localizacao_id)

    async def _validar_referencias_produto(self, deposito_id: UUID, dados: dict[str, Any]) -> None:
        categoria_id = dados.get("categoria_id")
        if categoria_id is not None:
            await self._buscar_no_deposito(self.categorias, categoria_id, deposito_id)
        localizacao_id = dados.get("localizacao_id")
        if localizacao_id is not None:
            await self._buscar_no_deposito(self.localizacoes, localizacao_id, deposito_id)

    async def listar_produtos(
        self, usuario_id: UUID, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Produto]:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self.produtos.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_produto(self, usuario_id: UUID, deposito_id: UUID, produto_id: UUID) -> Produto:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.produtos, produto_id, deposito_id)

    async def criar_produto(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Produto:
        await self._exigir_acesso(usuario_id, deposito_id)
        await self._validar_referencias_produto(deposito_id, dados)
        return await self._criar_no_deposito(usuario_id, deposito_id, self.produtos, dados)

    async def editar_produto(
        self, usuario_id: UUID, deposito_id: UUID, produto_id: UUID, dados: dict[str, Any]
    ) -> Produto:
        await self._exigir_acesso(usuario_id, deposito_id)
        await self._validar_referencias_produto(deposito_id, dados)
        return await self._editar_no_deposito(usuario_id, deposito_id, self.produtos, produto_id, dados)

    async def remover_produto(self, usuario_id: UUID, deposito_id: UUID, produto_id: UUID) -> None:
        await self._remover_no_deposito(usuario_id, deposito_id, self.produtos, produto_id)

    async def listar_estoque(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        localizacao_id: UUID | None = None,
    ) -> list[Estoque]:
        await self._exigir_acesso(usuario_id, deposito_id)
        filtros = {"deposito_id": deposito_id, "localizacao_id": localizacao_id}
        return await self.estoque.listar(inicio=inicio, limite=limite, filtros=filtros)

    async def estoque_do_produto(self, usuario_id: UUID, deposito_id: UUID, produto_id: UUID) -> list[Estoque]:
        await self.buscar_produto(usuario_id, deposito_id, produto_id)
        return await self.estoque.listar(filtros={"deposito_id": deposito_id, "produto_id": produto_id})

    async def buscar_estoque(self, usuario_id: UUID, deposito_id: UUID, estoque_id: UUID) -> Estoque:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.estoque, estoque_id, deposito_id)

    async def criar_estoque(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Estoque:
        await self._exigir_acesso(usuario_id, deposito_id)
        await self._buscar_no_deposito(self.produtos, dados["produto_id"], deposito_id)
        if dados.get("localizacao_id") is not None:
            await self._buscar_no_deposito(self.localizacoes, dados["localizacao_id"], deposito_id)
        return await self._criar_no_deposito(usuario_id, deposito_id, self.estoque, dados)

    async def editar_estoque(
        self, usuario_id: UUID, deposito_id: UUID, estoque_id: UUID, dados: dict[str, Any]
    ) -> Estoque:
        await self._exigir_acesso(usuario_id, deposito_id)
        if dados.get("localizacao_id") is not None:
            await self._buscar_no_deposito(self.localizacoes, dados["localizacao_id"], deposito_id)
        return await self._editar_no_deposito(usuario_id, deposito_id, self.estoque, estoque_id, dados)

    async def remover_estoque(self, usuario_id: UUID, deposito_id: UUID, estoque_id: UUID) -> None:
        await self._remover_no_deposito(usuario_id, deposito_id, self.estoque, estoque_id)

    async def listar_pedidos(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        usuario_filtro_id: UUID | None = None,
    ) -> list[Pedido]:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self.pedidos.listar(
            inicio=inicio,
            limite=limite,
            filtros={"deposito_id": deposito_id, "usuario_id": usuario_filtro_id},
        )

    async def buscar_pedido(self, usuario_id: UUID, deposito_id: UUID, pedido_id: UUID) -> Pedido:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.pedidos, pedido_id, deposito_id)

    async def criar_pedido(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Pedido:
        return await self._criar_no_deposito(usuario_id, deposito_id, self.pedidos, dados)

    async def editar_pedido(
        self, usuario_id: UUID, deposito_id: UUID, pedido_id: UUID, dados: dict[str, Any]
    ) -> Pedido:
        return await self._editar_no_deposito(usuario_id, deposito_id, self.pedidos, pedido_id, dados)

    async def remover_pedido(self, usuario_id: UUID, deposito_id: UUID, pedido_id: UUID) -> None:
        await self._remover_no_deposito(usuario_id, deposito_id, self.pedidos, pedido_id)

    async def itens_do_pedido(self, usuario_id: UUID, deposito_id: UUID, pedido_id: UUID) -> list[ItemPedido]:
        await self.buscar_pedido(usuario_id, deposito_id, pedido_id)
        return await self.repositorio_itens_pedido.por_pedido(deposito_id, pedido_id)

    async def adicionar_item_pedido(
        self, usuario_id: UUID, deposito_id: UUID, pedido_id: UUID, dados: dict[str, Any]
    ) -> ItemPedido:
        await self.buscar_pedido(usuario_id, deposito_id, pedido_id)
        await self._buscar_no_deposito(self.produtos, dados["produto_id"], deposito_id)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados["pedido_id"] = pedido_id
        dados["deposito_id"] = deposito_id
        return await self.itens_pedido.criar(dados)

    async def listar_movimentacoes(
        self,
        usuario_id: UUID,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        produto_id: UUID | None = None,
        pedido_id: UUID | None = None,
    ) -> list[Movimentacao]:
        await self._exigir_acesso(usuario_id, deposito_id)
        filtros = {"deposito_id": deposito_id, "produto_id": produto_id, "pedido_id": pedido_id}
        return await self.movimentacoes.listar(inicio=inicio, limite=limite, filtros=filtros)

    async def buscar_movimentacao(
        self, usuario_id: UUID, deposito_id: UUID, movimentacao_id: UUID
    ) -> Movimentacao:
        await self._exigir_acesso(usuario_id, deposito_id)
        return await self._buscar_no_deposito(self.movimentacoes, movimentacao_id, deposito_id)

    async def registrar_movimentacao(self, usuario_id: UUID, deposito_id: UUID, dados: dict[str, Any]) -> Movimentacao:
        await self._exigir_acesso(usuario_id, deposito_id)
        await self._validar_referencias_movimentacao(deposito_id, dados)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados["deposito_id"] = deposito_id
        await self._ajustar_estoque(deposito_id, dados)
        return await self.movimentacoes.criar(dados)

    async def _validar_referencias_movimentacao(self, deposito_id: UUID, dados: dict[str, Any]) -> None:
        await self._buscar_no_deposito(self.produtos, dados["produto_id"], deposito_id)
        if dados.get("pedido_id") is not None:
            await self._buscar_no_deposito(self.pedidos, dados["pedido_id"], deposito_id)
        for campo in ("origem_id", "destino_id"):
            if dados.get(campo) is not None:
                await self._buscar_no_deposito(self.localizacoes, dados[campo], deposito_id)

    async def _ajustar_estoque(self, deposito_id: UUID, dados: dict[str, Any]) -> None:
        tipo = dados["tipo"]
        produto_id = dados["produto_id"]
        quantidade = dados["quantidade"]
        localizacao_id = dados.get("destino_id") if tipo == TipoMovimentacao.ENTRADA else dados.get("origem_id")

        saldo = await self.repositorio_estoque.por_produto_local(deposito_id, produto_id, localizacao_id)
        if tipo == TipoMovimentacao.ENTRADA:
            if saldo is None:
                await self.estoque.criar(
                    {
                        "deposito_id": deposito_id,
                        "produto_id": produto_id,
                        "localizacao_id": localizacao_id,
                        "quantidade": quantidade,
                    }
                )
                return
            await self.estoque.editar(saldo.id, {"quantidade": saldo.quantidade + quantidade})
            return

        if saldo is None or saldo.quantidade < quantidade:
            raise ErroApp("Estoque insuficiente para a saida.", status_code=409, codigo="estoque_insuficiente")
        await self.estoque.editar(saldo.id, {"quantidade": saldo.quantidade - quantidade})
