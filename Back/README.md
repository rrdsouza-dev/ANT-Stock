# Back

Estrutura inicial do banco de dados para o backend Python com Supabase.

## O que existe aqui

- `app/core/config.py`: carrega as variaveis de ambiente do arquivo `.env`.
- `app/db/client.py`: cria o cliente Supabase de forma lazy.
- `app/db/repositories/base.py`: base para os futuros repositorios.

## Como conectar depois

1. Copie `.env.example` para `.env`.
2. Preencha `SUPABASE_URL` e `SUPABASE_KEY`.
3. Importe `get_supabase_client` ou herde de `BaseRepository`.

Nenhuma conexao externa e feita automaticamente nesta estrutura.
