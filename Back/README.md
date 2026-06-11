# ANT Backend

Backend FastAPI do sistema WMS ANT.

O codigo prioriza uma estrutura simples, em portugues, com SQLModel,
SQLAlchemy async, Supabase/PostgreSQL, JWT, Redis/Celery, Loguru, Ruff,
mypy e pytest.

## Estrutura

```text
src/
|-- api/
|   |-- rotas/
|   |-- dependencias.py
|   `-- roteador.py
|-- banco/
|-- esquemas/
|-- intermediarios/
|-- modelos/
|-- nucleo/
|-- repositorios/
|-- servicos/
|-- tarefas/
|-- tests/
|-- utilitarios/
`-- main.py

supabase/
|-- migrations/
|   `-- 202606100001_schema_consolidado_professor_gestao.sql
|-- README.md
`-- seed.sql
```

## Executar localmente

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r ../requirements.txt
copy .env.example .env
uvicorn src.main:app --reload
```

## Supabase

Configure no `Back/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=sua-chave-anon
SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role
```

Depois rode `Back/supabase/migrations/202606100001_schema_consolidado_professor_gestao.sql` no SQL Editor do Supabase. O arquivo `Back/supabase/seed.sql` tem dados iniciais opcionais.

## Modelagem

Entidades principais:

- `perfis`: somente Professor e Gestao.
- `usuarios`: preparado para Supabase Auth via `auth_id`.
- `categorias`, `localizacoes`, `produtos`.
- `estoque`: saldo por produto e localizacao.
- `movimentacoes`: entradas e saidas com `usuario_id`, `produto_id` e `pedido_id`.
- `pedidos` e `itens_pedido`.

Endpoints principais:

- `GET /health`
- `POST /api/v1/autenticacao/cadastro`
- `POST /api/v1/autenticacao/entrar`
- `GET /api/v1/depositos`
- `GET /api/v1/{deposito_id}/produtos`
- `GET /api/v1/{deposito_id}/categorias`
- `GET /api/v1/{deposito_id}/localizacoes`
- `GET /api/v1/{deposito_id}/estoque`
- `GET /api/v1/{deposito_id}/movimentacoes`
- `GET /api/v1/{deposito_id}/pedidos`

## Qualidade

```bash
ruff check .
ruff format .
mypy src
pytest
```
