# ANT Stock Backend

Backend FastAPI moderno com SQLModel, SQLAlchemy async, PostgreSQL, Alembic,
JWT, Redis/Celery, Loguru, Ruff, mypy e pytest.

## Estrutura

```text
src/
├── api/
│   ├── endpoints/
│   └── routes.py
├── core/
├── database/
├── middlewares/
├── models/
├── repositories/
├── schemas/
├── services/
├── tasks/
├── tests/
├── utils/
└── main.py
```

## Executar localmente

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r ../requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```

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

