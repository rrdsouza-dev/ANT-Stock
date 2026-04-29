# Supabase

Esta pasta guarda a estrutura SQL planejada para o banco do Supabase.

## Ordem da modelagem

1. Tipos e extensoes do Postgres.
2. Tabelas comuns, como usuarios e escopos.
3. Tabelas da escola e da turma de logistica.
4. Tabelas de estoque que usam `escopo_id` para separar os dados.
5. Funcoes e politicas de seguranca por Row Level Security.

## Separacao dos dados

A tabela `escopos` define se os dados pertencem a:

- `gestao_escola`: dados usados por uma conta de gestao da escola.
- `turma_logistica`: dados usados pela turma de logistica.

As tabelas de estoque sempre recebem `escopo_id` e `tipo_escopo`. Isso evita que produtos, categorias, localizacoes, estoque e movimentacoes de uma turma aparecam para a gestao errada, ou que dados da escola se misturem com dados didaticos da turma.

O arquivo SQL ainda nao foi aplicado ao Supabase. Ele serve como base de criacao quando o projeto for conectado.
