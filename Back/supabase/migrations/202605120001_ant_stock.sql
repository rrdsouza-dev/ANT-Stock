-- Estrutura inicial do banco ANT Stock para Supabase.
create extension if not exists "pgcrypto";

do $$
begin
    create type scopetype as enum ('SCHOOL_MANAGEMENT', 'LOGISTICS_CLASS');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type userprofile as enum ('MANAGEMENT', 'TEACHER', 'STUDENT');
exception when duplicate_object then null;
end $$;

do $$
begin
    create type movementtype as enum ('IN', 'OUT');
exception when duplicate_object then null;
end $$;

create table if not exists public.escopos (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    name varchar(120) not null,
    scope_type scopetype not null,
    school_id uuid,
    class_id uuid,
    active boolean not null default true
);

create table if not exists public.usuarios (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    email varchar(255) not null unique,
    name varchar(120),
    password_hash varchar(255) not null,
    provider varchar(40) default 'local',
    profile userprofile,
    scope_id uuid references public.escopos(id),
    active boolean not null default true
);

create table if not exists public.categorias (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references public.escopos(id),
    scope_type scopetype not null,
    name varchar(120) not null,
    description varchar(500),
    active boolean not null default true,
    constraint uq_categorias_escopo_nome unique (scope_id, name)
);

create table if not exists public.localizacoes (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references public.escopos(id),
    scope_type scopetype not null,
    name varchar(120) not null,
    aisle varchar(50),
    shelf varchar(50),
    position varchar(50),
    active boolean not null default true,
    constraint uq_localizacoes_escopo_nome unique (scope_id, name)
);

create table if not exists public.produtos (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references public.escopos(id),
    scope_type scopetype not null,
    name varchar(160) not null,
    sku varchar(80),
    category_id uuid references public.categorias(id),
    location_id uuid references public.localizacoes(id),
    minimum_quantity integer not null default 0 check (minimum_quantity >= 0),
    active boolean not null default true,
    constraint uq_produtos_escopo_sku unique (scope_id, sku)
);

create table if not exists public.estoques (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references public.escopos(id),
    scope_type scopetype not null,
    product_id uuid not null references public.produtos(id),
    location_id uuid references public.localizacoes(id),
    quantity integer not null default 0 check (quantity >= 0),
    constraint uq_estoques_escopo_produto_local unique (scope_id, product_id, location_id)
);

create table if not exists public.movimentacoes (
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references public.escopos(id),
    scope_type scopetype not null,
    product_id uuid not null references public.produtos(id),
    movement_type movementtype not null,
    quantity integer not null check (quantity > 0),
    user_id uuid references public.usuarios(id),
    origin varchar(120),
    destination varchar(120),
    note varchar(500),
    moved_at timestamptz not null default now()
);

create index if not exists ix_escopos_scope_type on public.escopos(scope_type);
create index if not exists ix_usuarios_email on public.usuarios(email);
create index if not exists ix_categorias_scope_id on public.categorias(scope_id);
create index if not exists ix_categorias_name on public.categorias(name);
create index if not exists ix_localizacoes_scope_id on public.localizacoes(scope_id);
create index if not exists ix_localizacoes_name on public.localizacoes(name);
create index if not exists ix_produtos_scope_id on public.produtos(scope_id);
create index if not exists ix_produtos_name on public.produtos(name);
create index if not exists ix_produtos_sku on public.produtos(sku);
create index if not exists ix_estoques_scope_id on public.estoques(scope_id);
create index if not exists ix_estoques_product_id on public.estoques(product_id);
create index if not exists ix_movimentacoes_scope_id on public.movimentacoes(scope_id);
create index if not exists ix_movimentacoes_product_id on public.movimentacoes(product_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists set_escopos_updated_at on public.escopos;
create trigger set_escopos_updated_at before update on public.escopos
for each row execute function public.set_updated_at();

drop trigger if exists set_usuarios_updated_at on public.usuarios;
create trigger set_usuarios_updated_at before update on public.usuarios
for each row execute function public.set_updated_at();

drop trigger if exists set_categorias_updated_at on public.categorias;
create trigger set_categorias_updated_at before update on public.categorias
for each row execute function public.set_updated_at();

drop trigger if exists set_localizacoes_updated_at on public.localizacoes;
create trigger set_localizacoes_updated_at before update on public.localizacoes
for each row execute function public.set_updated_at();

drop trigger if exists set_produtos_updated_at on public.produtos;
create trigger set_produtos_updated_at before update on public.produtos
for each row execute function public.set_updated_at();

drop trigger if exists set_estoques_updated_at on public.estoques;
create trigger set_estoques_updated_at before update on public.estoques
for each row execute function public.set_updated_at();

drop trigger if exists set_movimentacoes_updated_at on public.movimentacoes;
create trigger set_movimentacoes_updated_at before update on public.movimentacoes
for each row execute function public.set_updated_at();

alter table public.escopos enable row level security;
alter table public.usuarios enable row level security;
alter table public.categorias enable row level security;
alter table public.localizacoes enable row level security;
alter table public.produtos enable row level security;
alter table public.estoques enable row level security;
alter table public.movimentacoes enable row level security;

drop policy if exists "backend service role" on public.escopos;
create policy "backend service role" on public.escopos
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.usuarios;
create policy "backend service role" on public.usuarios
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.categorias;
create policy "backend service role" on public.categorias
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.localizacoes;
create policy "backend service role" on public.localizacoes
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.produtos;
create policy "backend service role" on public.produtos
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.estoques;
create policy "backend service role" on public.estoques
for all to service_role using (true) with check (true);

drop policy if exists "backend service role" on public.movimentacoes;
create policy "backend service role" on public.movimentacoes
for all to service_role using (true) with check (true);
