-- Estrutura relacional do banco ANT para Supabase.
create extension if not exists "pgcrypto";

do $$
begin
    create type perfil_codigo as enum ('aluno', 'professor', 'gestao');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type tipo_movimentacao as enum ('entrada', 'saida');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type status_pedido as enum ('aberto', 'separado', 'concluido', 'cancelado');
exception when duplicate_object then null;
end $$;

create table if not exists public.perfis (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    codigo perfil_codigo not null unique,
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
    perfil_id uuid not null references public.perfis(id),
    ativo boolean not null default true
);

create table if not exists public.categorias (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null unique,
    descricao varchar(500),
    ativo boolean not null default true
);

create table if not exists public.localizacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null unique,
    corredor varchar(50),
    prateleira varchar(50),
    posicao varchar(50),
    ativo boolean not null default true
);

create table if not exists public.produtos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(160) not null,
    codigo varchar(80) unique,
    categoria_id uuid references public.categorias(id) on delete set null,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade_minima integer not null default 0 check (quantidade_minima >= 0),
    ativo boolean not null default true
);

create table if not exists public.estoque (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    produto_id uuid not null references public.produtos(id) on delete cascade,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade integer not null default 0 check (quantidade >= 0),
    constraint uq_estoque_produto_local unique (produto_id, localizacao_id)
);

create table if not exists public.pedidos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    usuario_id uuid references public.usuarios(id) on delete set null,
    status status_pedido not null default 'aberto',
    observacao varchar(500)
);

create table if not exists public.itens_pedido (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    pedido_id uuid not null references public.pedidos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete restrict,
    quantidade integer not null check (quantidade > 0),
    constraint uq_itens_pedido_produto unique (pedido_id, produto_id)
);

create table if not exists public.movimentacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    produto_id uuid not null references public.produtos(id) on delete restrict,
    usuario_id uuid references public.usuarios(id) on delete set null,
    pedido_id uuid references public.pedidos(id) on delete set null,
    origem_id uuid references public.localizacoes(id) on delete set null,
    destino_id uuid references public.localizacoes(id) on delete set null,
    tipo tipo_movimentacao not null,
    quantidade integer not null check (quantidade > 0),
    observacao varchar(500),
    movimentado_em timestamptz not null default now()
);

insert into public.perfis (codigo, nome)
values
    ('aluno', 'Aluno'),
    ('professor', 'Professor'),
    ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

create index if not exists ix_perfis_codigo on public.perfis(codigo);
create index if not exists ix_usuarios_auth_id on public.usuarios(auth_id);
create index if not exists ix_usuarios_email on public.usuarios(email);
create index if not exists ix_usuarios_perfil_id on public.usuarios(perfil_id);
create index if not exists ix_categorias_nome on public.categorias(nome);
create index if not exists ix_localizacoes_nome on public.localizacoes(nome);
create index if not exists ix_produtos_nome on public.produtos(nome);
create index if not exists ix_produtos_codigo on public.produtos(codigo);
create index if not exists ix_produtos_categoria_id on public.produtos(categoria_id);
create index if not exists ix_produtos_localizacao_id on public.produtos(localizacao_id);
create index if not exists ix_estoque_produto_id on public.estoque(produto_id);
create index if not exists ix_estoque_localizacao_id on public.estoque(localizacao_id);
create index if not exists ix_pedidos_usuario_id on public.pedidos(usuario_id);
create index if not exists ix_pedidos_status on public.pedidos(status);
create index if not exists ix_itens_pedido_pedido_id on public.itens_pedido(pedido_id);
create index if not exists ix_itens_pedido_produto_id on public.itens_pedido(produto_id);
create index if not exists ix_movimentacoes_produto_id on public.movimentacoes(produto_id);
create index if not exists ix_movimentacoes_usuario_id on public.movimentacoes(usuario_id);
create index if not exists ix_movimentacoes_pedido_id on public.movimentacoes(pedido_id);
create index if not exists ix_movimentacoes_tipo on public.movimentacoes(tipo);

create or replace function public.definir_atualizado_em()
returns trigger
language plpgsql
as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$;

drop trigger if exists definir_perfis_atualizado_em on public.perfis;
create trigger definir_perfis_atualizado_em before update on public.perfis
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_usuarios_atualizado_em on public.usuarios;
create trigger definir_usuarios_atualizado_em before update on public.usuarios
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_categorias_atualizado_em on public.categorias;
create trigger definir_categorias_atualizado_em before update on public.categorias
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_localizacoes_atualizado_em on public.localizacoes;
create trigger definir_localizacoes_atualizado_em before update on public.localizacoes
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_produtos_atualizado_em on public.produtos;
create trigger definir_produtos_atualizado_em before update on public.produtos
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_estoque_atualizado_em on public.estoque;
create trigger definir_estoque_atualizado_em before update on public.estoque
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_pedidos_atualizado_em on public.pedidos;
create trigger definir_pedidos_atualizado_em before update on public.pedidos
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_itens_pedido_atualizado_em on public.itens_pedido;
create trigger definir_itens_pedido_atualizado_em before update on public.itens_pedido
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_movimentacoes_atualizado_em on public.movimentacoes;
create trigger definir_movimentacoes_atualizado_em before update on public.movimentacoes
for each row execute function public.definir_atualizado_em();

alter table public.perfis enable row level security;
alter table public.usuarios enable row level security;
alter table public.categorias enable row level security;
alter table public.localizacoes enable row level security;
alter table public.produtos enable row level security;
alter table public.estoque enable row level security;
alter table public.pedidos enable row level security;
alter table public.itens_pedido enable row level security;
alter table public.movimentacoes enable row level security;

drop policy if exists "servico backend" on public.perfis;
create policy "servico backend" on public.perfis
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.usuarios;
create policy "servico backend" on public.usuarios
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.categorias;
create policy "servico backend" on public.categorias
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.localizacoes;
create policy "servico backend" on public.localizacoes
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.produtos;
create policy "servico backend" on public.produtos
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.estoque;
create policy "servico backend" on public.estoque
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.pedidos;
create policy "servico backend" on public.pedidos
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.itens_pedido;
create policy "servico backend" on public.itens_pedido
for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.movimentacoes;
create policy "servico backend" on public.movimentacoes
for all to service_role using (true) with check (true);
