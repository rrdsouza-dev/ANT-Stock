#!/usr/bin/env python3
"""
Seed inicial — ANT Stock
Cria a conta gestao@antstock.local e o depósito padrão.

Execute da pasta Back/:
    cd Back
    python seed_inicial.py
"""
import asyncio, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv
env_path = RAIZ / ".env"
if not env_path.exists():
    print(f"ERRO: .env não encontrado em {env_path}")
    sys.exit(1)

load_dotenv(env_path, override=True)
print("✓ .env carregado")

import src.nucleo.configuracao as _cfg
_cfg.configuracao.cache_clear()

import os
db_url = os.getenv("DATABASE_URL", "")
if not db_url or "SUA_SENHA" in db_url or "SEU_PROJECT" in db_url or db_url.endswith("localhost:5432/ant_stock"):
    print(f"\nERRO: DATABASE_URL inválida: {db_url[:80]}")
    print("Configure em Back/.env com a URL real do Supabase Pooler (Session mode).")
    print("Exemplo:")
    print("  DATABASE_URL=postgresql+asyncpg://postgres.ttmricxpuqytkbkxnpba:SUA_SENHA@aws-1-us-west-2.pooler.supabase.com:5432/postgres")
    sys.exit(1)

print(f"✓ DATABASE_URL: {db_url[:60]}…")

from src.nucleo.seguranca import gerar_hash
from src.banco.sessao import SessaoLocal
from src.modelos.autenticacao import Perfil, Usuario, UsuarioDeposito
from src.modelos.estoque import Deposito
from src.modelos.base import PerfilCodigo, TipoDeposito
from sqlalchemy import select, text

EMAIL = "gestao@antstock.local"
NOME  = "Gestão ANT"
SENHA = "AntStock2026!"

async def main():
    print("\nConectando ao Supabase…")
    async with SessaoLocal() as sessao:
        await sessao.execute(text("SELECT 1"))
        print("✓ Conexão OK\n")

        res = await sessao.execute(select(Usuario).where(Usuario.email == EMAIL))
        if res.scalar_one_or_none():
            print(f"✓ Conta {EMAIL} já existe — nada a fazer.")
            return

        res = await sessao.execute(select(Perfil).where(Perfil.codigo == PerfilCodigo.GESTAO))
        perfil = res.scalar_one_or_none()
        if not perfil:
            perfil = Perfil(codigo=PerfilCodigo.GESTAO, nome="Gestão")
            sessao.add(perfil)
            await sessao.flush()

        res = await sessao.execute(select(Deposito).where(Deposito.nome == "Estoque Escolar"))
        deposito = res.scalar_one_or_none()
        if not deposito:
            deposito = Deposito(nome="Estoque Escolar", tipo=TipoDeposito.ESCOLAR, descricao="Estoque principal da escola")
            sessao.add(deposito)
            await sessao.flush()

        usuario = Usuario(
            email=EMAIL, nome=NOME,
            senha_hash=gerar_hash(SENHA),
            provedor="local",
            perfil_id=perfil.id,
            ativo=True,
        )
        sessao.add(usuario)
        await sessao.flush()
        sessao.add(UsuarioDeposito(usuario_id=usuario.id, deposito_id=deposito.id))
        await sessao.commit()

        print("╔════════════════════════════════════════╗")
        print("║  ✓  Conta criada com sucesso!           ║")
        print("╠════════════════════════════════════════╣")
        print(f"║  Email : {EMAIL:<30} ║")
        print(f"║  Senha : {SENHA:<30} ║")
        print(f"║  Perfil: Gestão                        ║")
        print("╚════════════════════════════════════════╝")

asyncio.run(main())
