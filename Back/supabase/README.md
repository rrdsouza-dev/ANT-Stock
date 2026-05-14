# Supabase

Use esta pasta para moldar o banco do ANT no Supabase sem depender do Alembic.

## Ordem

1. Crie o projeto no Supabase.
2. Copie a connection string do pooler e coloque em `Back/.env` como `DATABASE_URL`.
3. Rode `migrations/202605120001_ant_stock.sql` no SQL Editor do Supabase.
4. Opcionalmente rode `seed.sql` para dados iniciais de teste.

O backend continua usando SQLAlchemy via `DATABASE_URL`. O cliente em `src/banco/supabase.py` serve para recursos da API Supabase, como Storage, Auth ou chamadas administrativas.

A tabela `usuarios` possui `auth_id` como FK opcional para `auth.users(id)`, deixando a integracao futura com Supabase Auth preparada sem travar os demais atributos.
