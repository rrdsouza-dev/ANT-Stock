from sqlalchemy.ext.asyncio import AsyncSession

from src.esquemas.autenticacao import CadastroEntrada, EntrarEntrada, TokenSaida, UsuarioSaida
from src.modelos import Perfil, PerfilCodigo, Usuario
from src.nucleo.erros import ErroApp
from src.nucleo.seguranca import checar_senha, criar_token, gerar_hash
from src.repositorios.autenticacao import RepositorioPerfil, RepositorioUsuario

NOMES_PERFIL = {
    PerfilCodigo.ALUNO: "Aluno",
    PerfilCodigo.PROFESSOR: "Professor",
    PerfilCodigo.GESTAO: "Gestao",
}


class ServicoAutenticacao:
    def __init__(self, sessao: AsyncSession) -> None:
        self.perfis = RepositorioPerfil(sessao)
        self.usuarios = RepositorioUsuario(sessao)

    async def cadastrar(self, dados: CadastroEntrada) -> TokenSaida:
        existente = await self.usuarios.por_email(str(dados.email))
        if existente:
            raise ErroApp("Email ja cadastrado.", status_code=409, codigo="email_em_uso")

        perfil = await self._perfil(dados.perfil)
        usuario = await self.usuarios.criar(
            {
                "email": str(dados.email).lower(),
                "nome": dados.nome,
                "senha_hash": gerar_hash(dados.senha),
                "provedor": "local",
                "perfil_id": perfil.id,
                "ativo": True,
            }
        )
        usuario.perfil = perfil
        return self._resposta_token(usuario)

    async def entrar(self, dados: EntrarEntrada) -> TokenSaida:
        usuario = await self.usuarios.por_email(str(dados.email))
        if not usuario or not usuario.senha_hash or not checar_senha(dados.senha, usuario.senha_hash):
            raise ErroApp("Email ou senha invalidos.", status_code=401, codigo="credenciais_invalidas")
        if not usuario.ativo:
            raise ErroApp("Usuario inativo.", status_code=403, codigo="usuario_inativo")
        return self._resposta_token(usuario)

    async def _perfil(self, codigo: PerfilCodigo) -> Perfil:
        perfil = await self.perfis.por_codigo(codigo)
        if perfil:
            return perfil
        return await self.perfis.criar({"codigo": codigo, "nome": NOMES_PERFIL[codigo]})

    def _resposta_token(self, usuario: Usuario) -> TokenSaida:
        perfil = usuario.perfil.codigo if usuario.perfil else None
        token = criar_token(str(usuario.id), {"email": usuario.email, "perfil": perfil})
        return TokenSaida(token=token, usuario=UsuarioSaida.de_modelo(usuario))
