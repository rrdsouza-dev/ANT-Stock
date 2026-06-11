-- Schema consolidado ANT Stock para PostgreSQL/Supabase.
-- Perfis permitidos: professor e gestao.

create extension if not exists "pgcrypto";

do $$
begin
    create type public.perfil_codigo as enum ('professor', 'gestao');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type public.tipo_movimentacao as enum ('entrada', 'saida');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type public.status_pedido as enum ('aberto', 'separado', 'concluido', 'cancelado');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type public.tipo_deposito as enum ('escolar', 'didatico');
exception when duplicate_object then null;
end $$;

create table if not exists public.perfis (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    codigo public.perfil_codigo not null unique,
    nome varchar(40) not null
);

create table if not exists public.usuarios (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    auth_id uuid unique references auth.users(id) on delete set null,
    email varchar(255) not null unique,
    nome varchar(120),
    senha_hash varchar(255),
    provedor varchar(40) not null default 'local',
    perfil_id uuid not null references public.perfis(id) on delete restrict,
    ativo boolean not null default true
);

create table if not exists public.depositos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null unique,
    tipo public.tipo_deposito not null,
    descricao varchar(500),
    ativo boolean not null default true
);

create table if not exists public.usuario_depositos (
    usuario_id uuid not null references public.usuarios(id) on delete cascade,
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    criado_em timestamptz not null default now(),
    primary key (usuario_id, deposito_id)
);

create table if not exists public.categorias (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    nome varchar(120) not null,
    descricao varchar(500),
    ativo boolean not null default true
);

create table if not exists public.localizacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    nome varchar(120) not null,
    corredor varchar(50),
    prateleira varchar(50),
    posicao varchar(50),
    ativo boolean not null default true
);

create table if not exists public.produtos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    nome varchar(160) not null,
    codigo varchar(80),
    categoria_id uuid references public.categorias(id) on delete set null,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade_minima integer not null default 0 check (quantidade_minima >= 0),
    ativo boolean not null default true
);

create table if not exists public.estoque (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete cascade,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade integer not null default 0 check (quantidade >= 0)
);

create table if not exists public.pedidos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    usuario_id uuid references public.usuarios(id) on delete set null,
    status public.status_pedido not null default 'aberto',
    observacao varchar(500)
);

create table if not exists public.itens_pedido (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    pedido_id uuid not null references public.pedidos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete restrict,
    quantidade integer not null check (quantidade > 0)
);

create table if not exists public.movimentacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid not null references public.depositos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete restrict,
    usuario_id uuid references public.usuarios(id) on delete set null,
    pedido_id uuid references public.pedidos(id) on delete set null,
    origem_id uuid references public.localizacoes(id) on delete set null,
    destino_id uuid references public.localizacoes(id) on delete set null,
    tipo public.tipo_movimentacao not null,
    quantidade integer not null check (quantidade > 0),
    observacao varchar(500),
    movimentado_em timestamptz not null default now()
);

create table if not exists public.codigos_recuperacao (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    usuario_id uuid not null references public.usuarios(id) on delete cascade,
    codigo_hash varchar(128) not null,
    expira_em timestamptz not null,
    usado boolean not null default false,
    tentativas integer not null default 0 check (tentativas >= 0),
    bloqueado_ate timestamptz
);

create unique index if not exists uq_categorias_nome_deposito on public.categorias(deposito_id, nome);
create unique index if not exists uq_localizacoes_nome_deposito on public.localizacoes(deposito_id, nome);
create unique index if not exists uq_produtos_codigo_deposito on public.produtos(deposito_id, codigo) where codigo is not null;
create unique index if not exists uq_estoque_deposito_produto_local on public.estoque(deposito_id, produto_id, localizacao_id);
create unique index if not exists uq_itens_pedido_produto on public.itens_pedido(deposito_id, pedido_id, produto_id);

create index if not exists ix_usuarios_auth_id on public.usuarios(auth_id);
create index if not exists ix_usuarios_email on public.usuarios(email);
create index if not exists ix_usuarios_perfil_id on public.usuarios(perfil_id);
create index if not exists ix_usuario_depositos_usuario_id on public.usuario_depositos(usuario_id);
create index if not exists ix_usuario_depositos_deposito_id on public.usuario_depositos(deposito_id);
create index if not exists ix_categorias_deposito_id on public.categorias(deposito_id);
create index if not exists ix_localizacoes_deposito_id on public.localizacoes(deposito_id);
create index if not exists ix_produtos_deposito_id on public.produtos(deposito_id);
create index if not exists ix_produtos_categoria_id on public.produtos(categoria_id);
create index if not exists ix_produtos_localizacao_id on public.produtos(localizacao_id);
create index if not exists ix_estoque_deposito_id on public.estoque(deposito_id);
create index if not exists ix_estoque_produto_id on public.estoque(produto_id);
create index if not exists ix_pedidos_deposito_id on public.pedidos(deposito_id);
create index if not exists ix_movimentacoes_deposito_id on public.movimentacoes(deposito_id);
create index if not exists ix_movimentacoes_produto_id on public.movimentacoes(produto_id);
create index if not exists ix_codigos_recuperacao_usuario_id on public.codigos_recuperacao(usuario_id);
create index if not exists ix_codigos_recuperacao_codigo_hash on public.codigos_recuperacao(codigo_hash);

create or replace function public.definir_atualizado_em()
returns trigger
language plpgsql
as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$;

do $$
declare
    tabela text;
begin
    foreach tabela in array array[
        'perfis', 'usuarios', 'depositos', 'categorias', 'localizacoes',
        'produtos', 'estoque', 'pedidos', 'itens_pedido', 'movimentacoes',
        'codigos_recuperacao'
    ]
    loop
        execute format('drop trigger if exists definir_%s_atualizado_em on public.%I', tabela, tabela);
        execute format(
            'create trigger definir_%s_atualizado_em before update on public.%I for each row execute function public.definir_atualizado_em()',
            tabela,
            tabela
        );
    end loop;
end $$;

insert into public.perfis (codigo, nome)
values ('professor', 'Professor'), ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

insert into public.depositos (nome, tipo, descricao)
values
    ('Estoque Escolar', 'escolar', 'Estoque principal de alimentos e suprimentos da escola'),
    ('Estoque Didatico A', 'didatico', 'Ambiente didatico para atividades de logistica'),
    ('Estoque Didatico B', 'didatico', 'Ambiente didatico para simulacoes de estoque')
on conflict (nome) do update set tipo = excluded.tipo, descricao = excluded.descricao;

alter table public.perfis enable row level security;
alter table public.usuarios enable row level security;
alter table public.depositos enable row level security;
alter table public.usuario_depositos enable row level security;
alter table public.categorias enable row level security;
alter table public.localizacoes enable row level security;
alter table public.produtos enable row level security;
alter table public.estoque enable row level security;
alter table public.pedidos enable row level security;
alter table public.itens_pedido enable row level security;
alter table public.movimentacoes enable row level security;
alter table public.codigos_recuperacao enable row level security;

do $$
declare
    tabela text;
begin
    foreach tabela in array array[
        'perfis', 'usuarios', 'depositos', 'usuario_depositos', 'categorias',
        'localizacoes', 'produtos', 'estoque', 'pedidos', 'itens_pedido',
        'movimentacoes', 'codigos_recuperacao'
    ]
    loop
        execute format('drop policy if exists "servico backend" on public.%I', tabela);
        execute format('create policy "servico backend" on public.%I for all to service_role using (true) with check (true)', tabela);
    end loop;
end $$;
