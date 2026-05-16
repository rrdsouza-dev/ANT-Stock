-- Estrutura relacional do banco ANT para Supabase com isolamento por deposito.
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

create table if not exists public.depositos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null unique,
    tipo varchar(40) not null check (tipo in ('escolar', 'didatico')),
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
    deposito_id uuid references public.depositos(id) on delete cascade,
    nome varchar(120) not null,
    descricao varchar(500),
    ativo boolean not null default true
);

create table if not exists public.localizacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid references public.depositos(id) on delete cascade,
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
    deposito_id uuid references public.depositos(id) on delete cascade,
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
    deposito_id uuid references public.depositos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete cascade,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade integer not null default 0 check (quantidade >= 0)
);

create table if not exists public.pedidos (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid references public.depositos(id) on delete cascade,
    usuario_id uuid references public.usuarios(id) on delete set null,
    status status_pedido not null default 'aberto',
    observacao varchar(500)
);

create table if not exists public.itens_pedido (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid references public.depositos(id) on delete cascade,
    pedido_id uuid not null references public.pedidos(id) on delete cascade,
    produto_id uuid not null references public.produtos(id) on delete restrict,
    quantidade integer not null check (quantidade > 0)
);

create table if not exists public.movimentacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    deposito_id uuid references public.depositos(id) on delete cascade,
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

alter table public.categorias add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.localizacoes add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.produtos add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.estoque add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.pedidos add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.itens_pedido add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;
alter table public.movimentacoes add column if not exists deposito_id uuid references public.depositos(id) on delete cascade;

insert into public.perfis (codigo, nome)
values
    ('aluno', 'Aluno'),
    ('professor', 'Professor'),
    ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

insert into public.depositos (nome, tipo, descricao)
values
    ('Estoque Escolar', 'escolar', 'Estoque real de alimentos e suprimentos da escola'),
    ('Turma A - Didatico', 'didatico', 'Estoque simulado para turma A de logistica'),
    ('Turma B - Didatico', 'didatico', 'Estoque simulado para turma B de logistica')
on conflict (nome) do update set
    tipo = excluded.tipo,
    descricao = excluded.descricao;

do $$
declare
    deposito_padrao uuid;
begin
    select id into deposito_padrao from public.depositos where nome = 'Estoque Escolar';

    update public.categorias set deposito_id = deposito_padrao where deposito_id is null;
    update public.localizacoes set deposito_id = deposito_padrao where deposito_id is null;
    update public.produtos set deposito_id = deposito_padrao where deposito_id is null;
    update public.estoque e set deposito_id = p.deposito_id from public.produtos p
        where e.produto_id = p.id and e.deposito_id is null;
    update public.estoque set deposito_id = deposito_padrao where deposito_id is null;
    update public.pedidos set deposito_id = deposito_padrao where deposito_id is null;
    update public.itens_pedido i set deposito_id = p.deposito_id from public.pedidos p
        where i.pedido_id = p.id and i.deposito_id is null;
    update public.itens_pedido set deposito_id = deposito_padrao where deposito_id is null;
    update public.movimentacoes m set deposito_id = p.deposito_id from public.produtos p
        where m.produto_id = p.id and m.deposito_id is null;
    update public.movimentacoes set deposito_id = deposito_padrao where deposito_id is null;

    insert into public.usuario_depositos (usuario_id, deposito_id)
    select id, deposito_padrao from public.usuarios
    on conflict do nothing;
end $$;

alter table public.categorias alter column deposito_id set not null;
alter table public.localizacoes alter column deposito_id set not null;
alter table public.produtos alter column deposito_id set not null;
alter table public.estoque alter column deposito_id set not null;
alter table public.pedidos alter column deposito_id set not null;
alter table public.itens_pedido alter column deposito_id set not null;
alter table public.movimentacoes alter column deposito_id set not null;

alter table public.categorias drop constraint if exists categorias_nome_key;
alter table public.localizacoes drop constraint if exists localizacoes_nome_key;
alter table public.produtos drop constraint if exists produtos_codigo_key;
alter table public.estoque drop constraint if exists uq_estoque_produto_local;
alter table public.itens_pedido drop constraint if exists uq_itens_pedido_produto;

create unique index if not exists uq_categorias_nome_deposito on public.categorias(deposito_id, nome);
create unique index if not exists uq_localizacoes_nome_deposito on public.localizacoes(deposito_id, nome);
create unique index if not exists uq_produtos_codigo_deposito on public.produtos(deposito_id, codigo) where codigo is not null;
create unique index if not exists uq_estoque_deposito_produto_local
on public.estoque(deposito_id, produto_id, localizacao_id);
create unique index if not exists uq_itens_pedido_produto on public.itens_pedido(deposito_id, pedido_id, produto_id);

create index if not exists ix_perfis_codigo on public.perfis(codigo);
create index if not exists ix_usuarios_auth_id on public.usuarios(auth_id);
create index if not exists ix_usuarios_email on public.usuarios(email);
create index if not exists ix_usuarios_perfil_id on public.usuarios(perfil_id);
create index if not exists ix_depositos_tipo on public.depositos(tipo);
create index if not exists ix_usuario_depositos_usuario_id on public.usuario_depositos(usuario_id);
create index if not exists ix_usuario_depositos_deposito_id on public.usuario_depositos(deposito_id);
create index if not exists ix_categorias_deposito_id on public.categorias(deposito_id);
create index if not exists ix_categorias_nome on public.categorias(nome);
create index if not exists ix_localizacoes_deposito_id on public.localizacoes(deposito_id);
create index if not exists ix_localizacoes_nome on public.localizacoes(nome);
create index if not exists ix_produtos_deposito_id on public.produtos(deposito_id);
create index if not exists ix_produtos_nome on public.produtos(nome);
create index if not exists ix_produtos_codigo on public.produtos(codigo);
create index if not exists ix_produtos_categoria_id on public.produtos(categoria_id);
create index if not exists ix_produtos_localizacao_id on public.produtos(localizacao_id);
create index if not exists ix_estoque_deposito_id on public.estoque(deposito_id);
create index if not exists ix_estoque_produto_id on public.estoque(produto_id);
create index if not exists ix_estoque_localizacao_id on public.estoque(localizacao_id);
create index if not exists ix_pedidos_deposito_id on public.pedidos(deposito_id);
create index if not exists ix_pedidos_usuario_id on public.pedidos(usuario_id);
create index if not exists ix_pedidos_status on public.pedidos(status);
create index if not exists ix_itens_pedido_deposito_id on public.itens_pedido(deposito_id);
create index if not exists ix_itens_pedido_pedido_id on public.itens_pedido(pedido_id);
create index if not exists ix_itens_pedido_produto_id on public.itens_pedido(produto_id);
create index if not exists ix_movimentacoes_deposito_id on public.movimentacoes(deposito_id);
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

drop trigger if exists definir_depositos_atualizado_em on public.depositos;
create trigger definir_depositos_atualizado_em before update on public.depositos
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
alter table public.depositos enable row level security;
alter table public.usuario_depositos enable row level security;
alter table public.categorias enable row level security;
alter table public.localizacoes enable row level security;
alter table public.produtos enable row level security;
alter table public.estoque enable row level security;
alter table public.pedidos enable row level security;
alter table public.itens_pedido enable row level security;
alter table public.movimentacoes enable row level security;

drop policy if exists "servico backend" on public.perfis;
create policy "servico backend" on public.perfis for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.usuarios;
create policy "servico backend" on public.usuarios for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.depositos;
create policy "servico backend" on public.depositos for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.usuario_depositos;
create policy "servico backend" on public.usuario_depositos for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.categorias;
create policy "servico backend" on public.categorias for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.localizacoes;
create policy "servico backend" on public.localizacoes for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.produtos;
create policy "servico backend" on public.produtos for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.estoque;
create policy "servico backend" on public.estoque for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.pedidos;
create policy "servico backend" on public.pedidos for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.itens_pedido;
create policy "servico backend" on public.itens_pedido for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.movimentacoes;
create policy "servico backend" on public.movimentacoes for all to service_role using (true) with check (true);
