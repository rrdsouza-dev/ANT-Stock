-- ============================================================
-- ANT STOCK — MASTER MIGRATION
-- Execute este arquivo em um banco Supabase limpo.
-- Substitui todas as migrações anteriores.
-- ============================================================

create extension if not exists "pgcrypto";

-- ── ENUMS ────────────────────────────────────────────────────
do $$ begin create type public.perfil_codigo as enum ('adm', 'professor', 'gestao'); exception when duplicate_object then null; end $$;
do $$ begin create type public.tipo_movimentacao as enum ('entrada', 'saida'); exception when duplicate_object then null; end $$;
do $$ begin create type public.status_pedido as enum ('aberto', 'separado', 'concluido', 'cancelado'); exception when duplicate_object then null; end $$;
do $$ begin create type public.tipo_deposito as enum ('escolar', 'didatico'); exception when duplicate_object then null; end $$;
do $$ begin create type public.status_cadastro as enum ('pendente', 'aprovado', 'recusado'); exception when duplicate_object then null; end $$;

-- ── PERFIS ───────────────────────────────────────────────────
create table if not exists public.perfis (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    codigo          public.perfil_codigo not null unique,
    nome            varchar(40) not null
);

-- ── USUARIOS ─────────────────────────────────────────────────
create table if not exists public.usuarios (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    auth_id         uuid unique references auth.users(id) on delete cascade,
    email           varchar(255) not null unique,
    nome            varchar(120),
    senha_hash      varchar(255),
    provedor        varchar(40) not null default 'local',
    perfil_id       uuid not null references public.perfis(id) on delete restrict,
    sala            varchar(30),
    ativo           boolean not null default true
);

-- ── DEPOSITOS ────────────────────────────────────────────────
create table if not exists public.depositos (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    nome            varchar(120) not null unique,
    tipo            public.tipo_deposito not null,
    descricao       varchar(500),
    ativo           boolean not null default true
);

-- ── USUARIO_DEPOSITOS ────────────────────────────────────────
create table if not exists public.usuario_depositos (
    usuario_id      uuid not null references public.usuarios(id) on delete cascade,
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    criado_em       timestamptz not null default now(),
    primary key (usuario_id, deposito_id)
);

-- ── CATEGORIAS ───────────────────────────────────────────────
create table if not exists public.categorias (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    nome            varchar(120) not null,
    descricao       varchar(500),
    ativo           boolean not null default true
);

-- ── LOCALIZACOES ─────────────────────────────────────────────
create table if not exists public.localizacoes (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    nome            varchar(120) not null,
    torre           varchar(50),
    corredor        varchar(50),
    prateleira      varchar(50),
    posicao         varchar(50),
    ativo           boolean not null default true
);

-- ── PRODUTOS ─────────────────────────────────────────────────
create table if not exists public.produtos (
    id                   uuid primary key default gen_random_uuid(),
    criado_em            timestamptz not null default now(),
    atualizado_em        timestamptz not null default now(),
    deposito_id          uuid not null references public.depositos(id) on delete cascade,
    nome                 varchar(160) not null,
    codigo               varchar(80),
    categoria_id         uuid references public.categorias(id) on delete set null,
    localizacao_id       uuid references public.localizacoes(id) on delete set null,
    quantidade_minima    integer not null default 0 check (quantidade_minima >= 0),
    unidade_medida       varchar(30),
    quantidade_por_caixa integer check (quantidade_por_caixa >= 1),
    validade             varchar(20),
    observacoes          varchar(500),
    ativo                boolean not null default true
);

-- ── ESTOQUE ──────────────────────────────────────────────────
create table if not exists public.estoque (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    produto_id      uuid not null references public.produtos(id) on delete cascade,
    localizacao_id  uuid references public.localizacoes(id) on delete set null,
    quantidade      integer not null default 0 check (quantidade >= 0)
);

-- ── PEDIDOS ──────────────────────────────────────────────────
create table if not exists public.pedidos (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    usuario_id      uuid references public.usuarios(id) on delete set null,
    status          public.status_pedido not null default 'aberto',
    observacao      varchar(500)
);

-- ── ITENS_PEDIDO ─────────────────────────────────────────────
create table if not exists public.itens_pedido (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    pedido_id       uuid not null references public.pedidos(id) on delete cascade,
    produto_id      uuid not null references public.produtos(id) on delete restrict,
    quantidade      integer not null check (quantidade > 0)
);

-- ── MOVIMENTACOES ────────────────────────────────────────────
create table if not exists public.movimentacoes (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    deposito_id     uuid not null references public.depositos(id) on delete cascade,
    produto_id      uuid not null references public.produtos(id) on delete restrict,
    usuario_id      uuid references public.usuarios(id) on delete set null,
    pedido_id       uuid references public.pedidos(id) on delete set null,
    origem_id       uuid references public.localizacoes(id) on delete set null,
    destino_id      uuid references public.localizacoes(id) on delete set null,
    tipo            public.tipo_movimentacao not null,
    quantidade      integer not null check (quantidade > 0),
    observacao      varchar(500),
    movimentado_em  timestamptz not null default now()
);

-- ── CODIGOS_RECUPERACAO ──────────────────────────────────────
create table if not exists public.codigos_recuperacao (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    usuario_id      uuid not null references public.usuarios(id) on delete cascade,
    codigo_hash     varchar(128) not null,
    expira_em       timestamptz not null,
    usado           boolean not null default false,
    tentativas      integer not null default 0 check (tentativas >= 0),
    bloqueado_ate   timestamptz
);

-- ── CADASTRO_PENDENTE ────────────────────────────────────────
create table if not exists public.cadastro_pendente (
    id                  uuid primary key default gen_random_uuid(),
    criado_em           timestamptz not null default now(),
    atualizado_em       timestamptz not null default now(),
    nome                varchar(120) not null,
    email               varchar(255) not null unique,
    senha_hash          varchar(255) not null,
    perfil_solicitado   public.perfil_codigo not null,
    status              varchar(20) not null default 'pendente'
);

-- ── HISTORICO_APROVACOES ─────────────────────────────────────
create table if not exists public.historico_aprovacoes (
    id              uuid primary key default gen_random_uuid(),
    criado_em       timestamptz not null default now(),
    atualizado_em   timestamptz not null default now(),
    usuario_id      uuid not null references public.usuarios(id),
    nome            varchar(120) not null,
    email           varchar(255) not null,
    perfil          public.perfil_codigo not null,
    aprovado_por_id uuid not null references public.usuarios(id)
);

-- ── HISTORICO_RECUSAS ────────────────────────────────────────
create table if not exists public.historico_recusas (
    id                  uuid primary key default gen_random_uuid(),
    criado_em           timestamptz not null default now(),
    atualizado_em       timestamptz not null default now(),
    nome                varchar(120) not null,
    email               varchar(255) not null,
    perfil_solicitado   public.perfil_codigo not null,
    recusado_por_id     uuid not null references public.usuarios(id),
    motivo              varchar(500)
);

-- ── INDEXES ──────────────────────────────────────────────────
create unique index if not exists uq_categorias_nome_deposito       on public.categorias(deposito_id, nome);
create unique index if not exists uq_localizacoes_nome_deposito     on public.localizacoes(deposito_id, nome);
create unique index if not exists uq_produtos_codigo_deposito       on public.produtos(deposito_id, codigo) where codigo is not null and codigo <> '';
create unique index if not exists uq_estoque_deposito_produto_local on public.estoque(deposito_id, produto_id, coalesce(localizacao_id, '00000000-0000-0000-0000-000000000000'));
create unique index if not exists uq_itens_pedido_produto           on public.itens_pedido(pedido_id, produto_id);

create index if not exists ix_usuarios_email           on public.usuarios(email);
create index if not exists ix_usuarios_auth_id         on public.usuarios(auth_id);
create index if not exists ix_usuarios_perfil_id       on public.usuarios(perfil_id);
create index if not exists ix_depositos_tipo           on public.depositos(tipo);
create index if not exists ix_categorias_deposito_id   on public.categorias(deposito_id);
create index if not exists ix_localizacoes_deposito_id on public.localizacoes(deposito_id);
create index if not exists ix_produtos_deposito_id     on public.produtos(deposito_id);
create index if not exists ix_produtos_codigo          on public.produtos(codigo);
create index if not exists ix_produtos_categoria_id    on public.produtos(categoria_id);
create index if not exists ix_estoque_produto_id       on public.estoque(produto_id);
create index if not exists ix_movimentacoes_produto_id on public.movimentacoes(produto_id);
create index if not exists ix_movimentacoes_tipo       on public.movimentacoes(tipo);
create index if not exists ix_codigos_recuperacao_usuario_id on public.codigos_recuperacao(usuario_id);
create index if not exists ix_cadastro_pendente_status on public.cadastro_pendente(status);

-- ── TRIGGER ATUALIZADO_EM ─────────────────────────────────────
create or replace function public.definir_atualizado_em()
returns trigger language plpgsql as $$
begin new.atualizado_em := now(); return new; end; $$;

do $$ declare t text;
begin
  foreach t in array array[
    'perfis','usuarios','depositos','categorias','localizacoes','produtos',
    'estoque','pedidos','itens_pedido','movimentacoes','codigos_recuperacao',
    'cadastro_pendente','historico_aprovacoes','historico_recusas'
  ] loop
    execute format('drop trigger if exists trg_%s_atualizado on public.%I', t, t);
    execute format('create trigger trg_%s_atualizado before update on public.%I for each row execute function public.definir_atualizado_em()', t, t);
  end loop;
end $$;

-- ── DADOS INICIAIS ────────────────────────────────────────────
insert into public.perfis (codigo, nome) values
  ('adm',      'Administrador'),
  ('professor', 'Professor'),
  ('gestao',   'Gestão')
on conflict (codigo) do update set nome = excluded.nome;

insert into public.depositos (nome, tipo, descricao) values
  ('Estoque Escolar',   'escolar',  'Estoque principal de alimentos e suprimentos da escola'),
  ('Estoque Didático A','didatico', 'Ambiente didático para atividades de logística'),
  ('Estoque Didático B','didatico', 'Ambiente didático para simulações de estoque')
on conflict (nome) do update set tipo = excluded.tipo, descricao = excluded.descricao;

-- ── CONTA INICIAL ─────────────────────────────────────────────
-- A conta de gestão é criada via Python após configurar o .env:
--   cd Back && python seed_inicial.py
-- O script usa o mesmo algoritmo bcrypt da aplicação (passlib),
-- garantindo que o login funcione corretamente.

-- ── RLS ───────────────────────────────────────────────────────
do $$ declare t text;
begin
  foreach t in array array[
    'perfis','usuarios','depositos','usuario_depositos','categorias','localizacoes',
    'produtos','estoque','pedidos','itens_pedido','movimentacoes','codigos_recuperacao',
    'cadastro_pendente','historico_aprovacoes','historico_recusas'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "servico backend" on public.%I', t);
    execute format('create policy "servico backend" on public.%I for all to service_role using (true) with check (true)', t);
  end loop;
end $$;
