from datetime import timedelta
from hashlib import sha256
from secrets import randbelow
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.esquemas.autenticacao import (
    CadastroEntrada,
    EntrarEntrada,
    NovaSenhaEntrada,
    RecuperarSenhaEntrada,
    TokenSaida,
    UsuarioSaida,
    ValidarCodigoEntrada,
)
from src.modelos import Perfil, PerfilCodigo, Usuario
from src.modelos.base import agora_utc
from src.nucleo.erros import ErroApp
from src.nucleo.seguranca import checar_senha, criar_token, gerar_hash
from src.repositorios.autenticacao import (
    RepositorioCodigoRecuperacao,
    RepositorioPerfil,
    RepositorioUsuario,
    RepositorioUsuarioDeposito,
)
from src.repositorios.estoque import RepositorioDeposito

_NOMES_PERFIL = {
    PerfilCodigo.PROFESSOR: "Professor",
    PerfilCodigo.GESTAO: "Gestao",
    PerfilCodigo.ADM: "Administrador",
}


class ServicoAutenticacao:
    def __init__(self, sessao: AsyncSession) -> None:
        self.perfis = RepositorioPerfil(sessao)
        self.usuarios = RepositorioUsuario(sessao)
        self.usuario_depositos = RepositorioUsuarioDeposito(sessao)
        self.depositos = RepositorioDeposito(sessao)
        self.codigos = RepositorioCodigoRecuperacao(sessao)

    async def cadastrar(self, dados: CadastroEntrada) -> TokenSaida:
        if await self.usuarios.por_email(str(dados.email)):
            raise ErroApp("Email ja cadastrado.", status_code=409, codigo="email_em_uso")

        perfil = await self._obter_ou_criar_perfil(dados.perfil)
        usuario = await self.usuarios.criar({
            "email": str(dados.email).lower(),
            "nome": dados.nome,
            "senha_hash": gerar_hash(dados.senha),
            "provedor": "local",
            "perfil_id": perfil.id,
            "turmas": dados.turmas if dados.perfil == PerfilCodigo.PROFESSOR else [],
            "ativo": True,
        })
        usuario.perfil = perfil

        # Todo usuario novo (professor ou gestao) recebe acesso automatico a todos
        # os depositos ativos da escola. Evita o erro "Sem acesso a este deposito"
        # logo apos o cadastro, ja que nao existe fluxo de vinculo manual no Front.
        depositos_ativos = await self.depositos.listar(limite=200, filtros={"ativo": True})
        await self.usuario_depositos.vincular_a_depositos(usuario.id, [d.id for d in depositos_ativos])

        return self._gerar_token(usuario)

    async def entrar(self, dados: EntrarEntrada) -> TokenSaida:
        usuario = await self.usuarios.por_email(str(dados.email))
        if not usuario or not usuario.senha_hash or not checar_senha(dados.senha, usuario.senha_hash):
            raise ErroApp("Email ou senha invalidos.", status_code=401, codigo="credenciais_invalidas")
        if not usuario.ativo:
            raise ErroApp("Usuario inativo.", status_code=403, codigo="usuario_inativo")
        return self._gerar_token(usuario)

    async def recuperar_senha(self, dados: RecuperarSenhaEntrada) -> str:
        usuario = await self.usuarios.por_email(str(dados.email))
        if not usuario or not usuario.ativo:
            return "Se o email existir, um codigo sera enviado."

        codigo = f"{randbelow(1_000_000):06d}"
        await self.codigos.criar({
            "usuario_id": usuario.id,
            "codigo_hash": self._hash_codigo(codigo),
            "expira_em": agora_utc() + timedelta(minutes=15),
            "usado": False,
            "tentativas": 0,
        })
        # Em producao enviar por email. Retorno facilita testes locais.
        return f"Codigo de recuperacao gerado. Use {codigo} em ambiente local."

    async def validar_codigo(self, dados: ValidarCodigoEntrada) -> None:
        usuario, registro = await self._validar_registro(str(dados.email), dados.codigo)
        if registro.usuario_id != usuario.id:
            raise ErroApp("Codigo invalido.", status_code=400, codigo="codigo_invalido")

    async def nova_senha(self, dados: NovaSenhaEntrada) -> None:
        usuario, registro = await self._validar_registro(str(dados.email), dados.codigo)
        await self.usuarios.editar(usuario, {"senha_hash": gerar_hash(dados.nova_senha)})
        await self.codigos.editar(registro, {"usado": True})

    async def verificar_acesso(self, usuario_id: UUID, deposito_id: UUID) -> bool:
        return await self.usuario_depositos.existe(usuario_id, deposito_id)

    async def listar_usuarios(self, inicio: int = 0, limite: int = 100) -> list[Usuario]:
        return await self.usuarios.listar_com_perfil(inicio=inicio, limite=limite)

    # ── Métodos privados ────────────────────────────────────────

    async def _obter_ou_criar_perfil(self, codigo: PerfilCodigo) -> Perfil:
        perfil = await self.perfis.por_codigo(codigo)
        if perfil:
            return perfil
        return await self.perfis.criar({"codigo": codigo, "nome": _NOMES_PERFIL[codigo]})

    async def _validar_registro(self, email: str, codigo: str):
        usuario = await self.usuarios.por_email(email)
        if not usuario:
            raise ErroApp("Codigo invalido.", status_code=400, codigo="codigo_invalido")

        registro = await self.codigos.ultimo_ativo(usuario.id)
        agora = agora_utc()

        if not registro or registro.expira_em < agora:
            raise ErroApp("Codigo expirado.", status_code=400, codigo="codigo_expirado")
        if registro.bloqueado_ate and registro.bloqueado_ate > agora:
            raise ErroApp("Codigo temporariamente bloqueado.", status_code=429, codigo="codigo_bloqueado")
        if registro.codigo_hash != self._hash_codigo(codigo):
            tentativas = registro.tentativas + 1
            patch = {"tentativas": tentativas}
            if tentativas >= 3:
                patch["bloqueado_ate"] = agora + timedelta(minutes=5)
            await self.codigos.editar(registro, patch)
            raise ErroApp("Codigo invalido.", status_code=400, codigo="codigo_invalido")

        return usuario, registro

    def _hash_codigo(self, codigo: str) -> str:
        return sha256(codigo.encode()).hexdigest()

    def _gerar_token(self, usuario: Usuario) -> TokenSaida:
        perfil = usuario.perfil.codigo if usuario.perfil else None
        token = criar_token(str(usuario.id), {"email": usuario.email, "perfil": perfil})
        return TokenSaida(token=token, usuario=UsuarioSaida.de_modelo(usuario))
