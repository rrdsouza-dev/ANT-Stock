#!/usr/bin/env python3
"""
Seed inicial: cria a conta gestao@antstock.local no banco.
Execute APÓS conectar o .env ao Supabase:
    python seed_inicial.py
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.nucleo.seguranca import gerar_hash
from src.banco.sessao import SessaoLocal
from src.modelos.autenticacao import Perfil, Usuario, UsuarioDeposito
from src.modelos.estoque import Deposito
from src.modelos.base import PerfilCodigo
from sqlalchemy import text, select

EMAIL = "gestao@antstock.local"
NOME  = "Gestão ANT"
SENHA = "AntStock2026!"

async def main():
    async with SessaoLocal() as sessao:
        # Check if already exists
        res = await sessao.execute(select(Usuario).where(Usuario.email == EMAIL))
        existing = res.scalar_one_or_none()
        if existing:
            print(f"✓ Conta {EMAIL} já existe — nenhuma ação necessária.")
            return

        # Get gestao perfil
        res = await sessao.execute(select(Perfil).where(Perfil.codigo == PerfilCodigo.GESTAO))
        perfil = res.scalar_one_or_none()
        if not perfil:
            perfil = Perfil(codigo=PerfilCodigo.GESTAO, nome="Gestão")
            sessao.add(perfil)
            await sessao.flush()

        # Get default deposit
        res = await sessao.execute(select(Deposito).where(Deposito.nome == "Estoque Escolar"))
        deposito = res.scalar_one_or_none()
        if not deposito:
            from src.modelos.base import TipoDeposito
            deposito = Deposito(nome="Estoque Escolar", tipo=TipoDeposito.ESCOLAR, descricao="Estoque principal")
            sessao.add(deposito)
            await sessao.flush()

        # Create user
        usuario = Usuario(
            email=EMAIL,
            nome=NOME,
            senha_hash=gerar_hash(SENHA),
            provedor="local",
            perfil_id=perfil.id,
            ativo=True,
        )
        sessao.add(usuario)
        await sessao.flush()

        # Link to deposit
        link = UsuarioDeposito(usuario_id=usuario.id, deposito_id=deposito.id)
        sessao.add(link)
        await sessao.commit()

        print(f"✓ Conta criada: {EMAIL} / {SENHA}")
        print(f"  Perfil: gestão | Depósito: {deposito.nome}")
        print()
        print("Para alterar a senha:")
        print("  Use POST /api/v1/autenticacao/recuperar-senha")
        print("  ou: UPDATE public.usuarios SET senha_hash = '<novo hash>' WHERE email = 'gestao@antstock.local';")
        print()
        print("Para remover a conta:")
        print("  DELETE FROM public.usuarios WHERE email = 'gestao@antstock.local';")

asyncio.run(main())
