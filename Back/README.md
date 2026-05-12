<!-- Guia rapido do backend FastAPI. -->
# ANT Stock Backend

Backend FastAPI moderno com SQLModel, SQLAlchemy async, Supabase/PostgreSQL,
JWT, Redis/Celery, Loguru, Ruff, mypy e pytest.

## Estrutura

```text
src/
|-- api/
|   |-- endpoints/
|   |-- deps.py
|   `-- router.py
|-- core/
|-- database/
|-- middlewares/
|-- models/
|-- repositories/
|-- schemas/
|-- services/
|-- tasks/
|-- tests/
|-- utils/
`-- main.py

supabase/
|-- migrations/
|   `-- 202605120001_ant_stock.sql
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

Para usar Supabase como banco, configure no `Back/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=sua-chave-anon
SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role
```

Depois rode `Back/supabase/migrations/202605120001_ant_stock.sql` no SQL Editor do Supabase. O arquivo `Back/supabase/seed.sql` tem dados iniciais opcionais.

Endpoints principais:

- `GET /health`
- `POST /api/v1/autenticacao/cadastro`
- `POST /api/v1/autenticacao/entrar`
- `GET /api/v1/produtos`
- `GET /api/v1/categorias`
- `GET /api/v1/localizacoes`
- `GET /api/v1/estoque`
- `GET /api/v1/movimentacoes`

## Qualidade

```bash
ruff check .
ruff format .
mypy src
pytest
```
