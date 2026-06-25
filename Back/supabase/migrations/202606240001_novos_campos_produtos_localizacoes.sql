-- Migração: novos campos em produtos e localizacoes
-- Data: 2026-06-24

-- Adicionar campo torre em localizacoes
alter table public.localizacoes
  add column if not exists torre varchar(50);

-- Adicionar novos campos em produtos
alter table public.produtos
  add column if not exists unidade_medida varchar(30),
  add column if not exists quantidade_por_caixa integer check (quantidade_por_caixa >= 1),
  add column if not exists validade varchar(20),
  add column if not exists observacoes varchar(500);

-- Adicionar campo sala em usuarios (para perfil professor)
alter table public.usuarios
  add column if not exists sala varchar(30);
