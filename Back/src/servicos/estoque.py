from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.modelos import (
    Categoria,
    Estoque,
    ItemPedido,
    Localizacao,
    Movimentacao,
    Pedido,
    PerfilCodigo,
    Produto,
    TipoMovimentacao,
    Usuario,
)
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

ModeloCrudT = TypeVar("ModeloCrudT", bound=SQLModel)


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

    async def verificar_acesso(self, usuario: Usuario, deposito_id: UUID) -> bool:
        # Gestao tem acesso universal a todos os depositos, sem precisar de vinculo explicito.
        if usuario.perfil and usuario.perfil.codigo == PerfilCodigo.GESTAO:
            return True
        return await self.usuario_depositos.existe(usuario.id, deposito_id)

    async def _exigir_acesso(self, usuario: Usuario, deposito_id: UUID) -> None:
        if not await self.verificar_acesso(usuario, deposito_id):
            raise ErroApp("Sem acesso a este deposito", status_code=403, codigo="sem_acesso_deposito")

    async def _buscar_no_deposito(
        self,
        crud: ServicoCrud[ModeloCrudT],
        item_id: UUID,
        deposito_id: UUID,
    ) -> ModeloCrudT:
        item = await crud.buscar(item_id)
        if getattr(item, "deposito_id", None) != deposito_id:
            raise ErroApp(f"{crud.nome_recurso} nao encontrado.", status_code=404, codigo="nao_encontrado")
        return item

    async def _criar_no_deposito(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        crud: ServicoCrud[ModeloCrudT],
        dados: dict[str, Any],
    ) -> ModeloCrudT:
        await self._exigir_acesso(usuario, deposito_id)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados["deposito_id"] = deposito_id
        return await crud.criar(dados)

    async def _editar_no_deposito(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        crud: ServicoCrud[ModeloCrudT],
        item_id: UUID,
        dados: dict[str, Any],
    ) -> ModeloCrudT:
        await self._exigir_acesso(usuario, deposito_id)
        item = await self._buscar_no_deposito(crud, item_id, deposito_id)
        # Remove deposito_id dos dados (não pode ser alterado pelo usuário)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        return await crud.repositorio.editar(item, dados)

    async def _remover_no_deposito(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        crud: ServicoCrud[ModeloCrudT],
        item_id: UUID,
    ) -> None:
        await self._exigir_acesso(usuario, deposito_id)
        item = await self._buscar_no_deposito(crud, item_id, deposito_id)
        await crud.repositorio.remover(item)

    # ── Categorias ──────────────────────────────────────────────

    async def listar_categorias(
        self, usuario: Usuario, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Categoria]:
        await self._exigir_acesso(usuario, deposito_id)
        return await self.categorias.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_categoria(self, usuario: Usuario, deposito_id: UUID, categoria_id: UUID) -> Categoria:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.categorias, categoria_id, deposito_id)

    async def criar_categoria(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Categoria:
        return await self._criar_no_deposito(usuario, deposito_id, self.categorias, dados)

    async def editar_categoria(
        self, usuario: Usuario, deposito_id: UUID, categoria_id: UUID, dados: dict[str, Any]
    ) -> Categoria:
        return await self._editar_no_deposito(usuario, deposito_id, self.categorias, categoria_id, dados)

    async def remover_categoria(self, usuario: Usuario, deposito_id: UUID, categoria_id: UUID) -> None:
        await self._remover_no_deposito(usuario, deposito_id, self.categorias, categoria_id)

    # ── Localizações ────────────────────────────────────────────

    async def listar_localizacoes(
        self, usuario: Usuario, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Localizacao]:
        await self._exigir_acesso(usuario, deposito_id)
        return await self.localizacoes.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_localizacao(self, usuario: Usuario, deposito_id: UUID, localizacao_id: UUID) -> Localizacao:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.localizacoes, localizacao_id, deposito_id)

    async def criar_localizacao(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Localizacao:
        return await self._criar_no_deposito(usuario, deposito_id, self.localizacoes, dados)

    async def editar_localizacao(
        self, usuario: Usuario, deposito_id: UUID, localizacao_id: UUID, dados: dict[str, Any]
    ) -> Localizacao:
        return await self._editar_no_deposito(usuario, deposito_id, self.localizacoes, localizacao_id, dados)

    async def remover_localizacao(self, usuario: Usuario, deposito_id: UUID, localizacao_id: UUID) -> None:
        await self._remover_no_deposito(usuario, deposito_id, self.localizacoes, localizacao_id)

    # ── Produtos ────────────────────────────────────────────────

    async def _validar_referencias_produto(self, deposito_id: UUID, dados: dict[str, Any]) -> None:
        categoria_id = dados.get("categoria_id")
        if categoria_id is not None:
            await self._buscar_no_deposito(self.categorias, categoria_id, deposito_id)
        localizacao_id = dados.get("localizacao_id")
        if localizacao_id is not None:
            await self._buscar_no_deposito(self.localizacoes, localizacao_id, deposito_id)

    async def listar_produtos(
        self, usuario: Usuario, deposito_id: UUID, inicio: int = 0, limite: int = 100
    ) -> list[Produto]:
        await self._exigir_acesso(usuario, deposito_id)
        return await self.produtos.listar(inicio=inicio, limite=limite, filtros={"deposito_id": deposito_id})

    async def buscar_produto(self, usuario: Usuario, deposito_id: UUID, produto_id: UUID) -> Produto:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.produtos, produto_id, deposito_id)

    async def buscar_produto_por_codigo(self, usuario: Usuario, deposito_id: UUID, codigo: str) -> Produto:
        await self._exigir_acesso(usuario, deposito_id)
        produto = await self.produtos.repositorio.por_codigo(deposito_id, codigo)
        if produto is None:
            raise ErroApp(
                "Produto nao encontrado para este codigo.",
                status_code=404,
                codigo="produto_codigo_nao_encontrado",
            )
        return produto

    async def criar_produto(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Produto:
        await self._exigir_acesso(usuario, deposito_id)
        await self._validar_referencias_produto(deposito_id, dados)
        return await self._criar_no_deposito(usuario, deposito_id, self.produtos, dados)

    async def editar_produto(
        self, usuario: Usuario, deposito_id: UUID, produto_id: UUID, dados: dict[str, Any]
    ) -> Produto:
        await self._exigir_acesso(usuario, deposito_id)
        await self._validar_referencias_produto(deposito_id, dados)
        return await self._editar_no_deposito(usuario, deposito_id, self.produtos, produto_id, dados)

    async def remover_produto(self, usuario: Usuario, deposito_id: UUID, produto_id: UUID) -> None:
        await self._remover_no_deposito(usuario, deposito_id, self.produtos, produto_id)

    # ── Estoque ─────────────────────────────────────────────────

    async def listar_estoque(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        localizacao_id: UUID | None = None,
    ) -> list[Estoque]:
        await self._exigir_acesso(usuario, deposito_id)
        filtros = {"deposito_id": deposito_id, "localizacao_id": localizacao_id}
        return await self.estoque.listar(inicio=inicio, limite=limite, filtros=filtros)

    async def estoque_do_produto(self, usuario: Usuario, deposito_id: UUID, produto_id: UUID) -> list[Estoque]:
        await self.buscar_produto(usuario, deposito_id, produto_id)
        return await self.estoque.listar(filtros={"deposito_id": deposito_id, "produto_id": produto_id})

    async def buscar_estoque(self, usuario: Usuario, deposito_id: UUID, estoque_id: UUID) -> Estoque:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.estoque, estoque_id, deposito_id)

    async def criar_estoque(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Estoque:
        await self._exigir_acesso(usuario, deposito_id)
        await self._buscar_no_deposito(self.produtos, dados["produto_id"], deposito_id)
        if dados.get("localizacao_id") is not None:
            await self._buscar_no_deposito(self.localizacoes, dados["localizacao_id"], deposito_id)
        return await self._criar_no_deposito(usuario, deposito_id, self.estoque, dados)

    async def editar_estoque(
        self, usuario: Usuario, deposito_id: UUID, estoque_id: UUID, dados: dict[str, Any]
    ) -> Estoque:
        await self._exigir_acesso(usuario, deposito_id)
        if dados.get("localizacao_id") is not None:
            await self._buscar_no_deposito(self.localizacoes, dados["localizacao_id"], deposito_id)
        return await self._editar_no_deposito(usuario, deposito_id, self.estoque, estoque_id, dados)

    async def remover_estoque(self, usuario: Usuario, deposito_id: UUID, estoque_id: UUID) -> None:
        await self._remover_no_deposito(usuario, deposito_id, self.estoque, estoque_id)

    # ── Pedidos ─────────────────────────────────────────────────

    async def listar_pedidos(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        usuario_filtro_id: UUID | None = None,
    ) -> list[Pedido]:
        await self._exigir_acesso(usuario, deposito_id)
        return await self.pedidos.listar(
            inicio=inicio,
            limite=limite,
            filtros={"deposito_id": deposito_id, "usuario_id": usuario_filtro_id},
        )

    async def buscar_pedido(self, usuario: Usuario, deposito_id: UUID, pedido_id: UUID) -> Pedido:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.pedidos, pedido_id, deposito_id)

    async def criar_pedido(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Pedido:
        dados.setdefault("usuario_id", usuario.id)
        return await self._criar_no_deposito(usuario, deposito_id, self.pedidos, dados)

    async def editar_pedido(
        self, usuario: Usuario, deposito_id: UUID, pedido_id: UUID, dados: dict[str, Any]
    ) -> Pedido:
        return await self._editar_no_deposito(usuario, deposito_id, self.pedidos, pedido_id, dados)

    async def remover_pedido(self, usuario: Usuario, deposito_id: UUID, pedido_id: UUID) -> None:
        await self._remover_no_deposito(usuario, deposito_id, self.pedidos, pedido_id)

    async def itens_do_pedido(self, usuario: Usuario, deposito_id: UUID, pedido_id: UUID) -> list[ItemPedido]:
        await self.buscar_pedido(usuario, deposito_id, pedido_id)
        return await self.repositorio_itens_pedido.por_pedido(deposito_id, pedido_id)

    async def adicionar_item_pedido(
        self, usuario: Usuario, deposito_id: UUID, pedido_id: UUID, dados: dict[str, Any]
    ) -> ItemPedido:
        await self.buscar_pedido(usuario, deposito_id, pedido_id)
        await self._buscar_no_deposito(self.produtos, dados["produto_id"], deposito_id)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados["pedido_id"] = pedido_id
        dados["deposito_id"] = deposito_id
        return await self.itens_pedido.criar(dados)

    # ── Movimentações ───────────────────────────────────────────

    async def listar_movimentacoes(
        self,
        usuario: Usuario,
        deposito_id: UUID,
        inicio: int = 0,
        limite: int = 100,
        produto_id: UUID | None = None,
        pedido_id: UUID | None = None,
    ) -> list[Movimentacao]:
        await self._exigir_acesso(usuario, deposito_id)
        filtros = {"deposito_id": deposito_id, "produto_id": produto_id, "pedido_id": pedido_id}
        return await self.movimentacoes.listar(inicio=inicio, limite=limite, filtros=filtros)

    async def buscar_movimentacao(
        self, usuario: Usuario, deposito_id: UUID, movimentacao_id: UUID
    ) -> Movimentacao:
        await self._exigir_acesso(usuario, deposito_id)
        return await self._buscar_no_deposito(self.movimentacoes, movimentacao_id, deposito_id)

    async def registrar_movimentacao(self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]) -> Movimentacao:
        await self._exigir_acesso(usuario, deposito_id)
        await self._validar_referencias_movimentacao(deposito_id, dados)
        dados = {campo: valor for campo, valor in dados.items() if campo != "deposito_id"}
        dados.setdefault("usuario_id", usuario.id)
        dados["deposito_id"] = deposito_id
        await self._ajustar_estoque(deposito_id, dados)
        return await self.movimentacoes.criar(dados)

    async def registrar_movimentacao_por_codigo(
        self, usuario: Usuario, deposito_id: UUID, dados: dict[str, Any]
    ) -> Movimentacao:
        produto = await self.buscar_produto_por_codigo(usuario, deposito_id, dados.pop("codigo"))
        dados["produto_id"] = produto.id
        return await self.registrar_movimentacao(usuario, deposito_id, dados)

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
