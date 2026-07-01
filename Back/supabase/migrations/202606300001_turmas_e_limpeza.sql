-- Migração: turmas (múltiplas) em usuarios + remoção do fluxo de aprovação morto
-- Data: 2026-06-30
--
-- Contexto: o fluxo de "cadastro pendente / aprovação / recusa" nunca foi
-- exposto por nenhuma rota da API (código morto). O campo "sala" (única
-- turma) é substituído por "turmas" (array), permitindo que um professor
-- esteja vinculado a várias turmas (ex.: 2A e 3A).

-- 1) Adiciona a coluna turmas (array de texto) em usuarios.
alter table public.usuarios
  add column if not exists turmas text[] not null default '{}';

-- 2) Migra o valor único de "sala" (se existir) para o array "turmas".
update public.usuarios
  set turmas = array[sala]
  where sala is not null and sala <> '' and turmas = '{}';

-- 3) Remove a coluna antiga "sala".
alter table public.usuarios
  drop column if exists sala;

-- 4) Remove as tabelas do fluxo de aprovação de cadastro (nunca utilizado pela API).
drop table if exists public.historico_recusas cascade;
drop table if exists public.historico_aprovacoes cascade;
drop table if exists public.cadastro_pendente cascade;

-- 5) Remove o tipo enum associado, que não é mais referenciado por nenhuma coluna.
drop type if exists public.status_cadastro;
