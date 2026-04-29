-- Schema inicial do ANT Stock para Supabase.
-- A ordem abaixo respeita as dependencias entre tabelas.

create extension if not exists "pgcrypto";

create type public.tipo_escopo as enum ('gestao_escola', 'turma_logistica');
create type public.perfil_usuario as enum ('gestao', 'professor', 'aluno');
create type public.tipo_movimentacao as enum ('entrada', 'saida');

create table public.usuarios (
    id uuid primary key references auth.users(id) on delete cascade,
    email text,
    nome text,
    provedor text,
    perfil public.perfil_usuario,
    escopo_id uuid,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create table public.escolas (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    codigo text unique,
    cidade text,
    estado text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create table public.turmas_logistica (
    id uuid primary key default gen_random_uuid(),
    escola_id uuid not null references public.escolas(id) on delete cascade,
    nome text not null,
    ano integer not null,
    periodo text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (escola_id, nome, ano)
);

create table public.escopos (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    tipo public.tipo_escopo not null,
    escola_id uuid references public.escolas(id) on delete cascade,
    turma_id uuid references public.turmas_logistica(id) on delete cascade,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (id, tipo),
    check (
        (tipo = 'gestao_escola' and escola_id is not null and turma_id is null)
        or
        (tipo = 'turma_logistica' and turma_id is not null and escola_id is null)
    )
);

alter table public.usuarios
    add constraint usuarios_escopo_id_fkey
    foreign key (escopo_id) references public.escopos(id) on delete set null;

create unique index escopos_gestao_escola_unico
    on public.escopos(escola_id)
    where tipo = 'gestao_escola';

create unique index escopos_turma_logistica_unico
    on public.escopos(turma_id)
    where tipo = 'turma_logistica';

create table public.gestao_escola (
    id uuid primary key default gen_random_uuid(),
    escola_id uuid not null references public.escolas(id) on delete cascade,
    usuario_id uuid not null references public.usuarios(id) on delete cascade,
    cargo text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (escola_id, usuario_id)
);

create table public.alunos_logistica (
    id uuid primary key default gen_random_uuid(),
    turma_id uuid not null references public.turmas_logistica(id) on delete cascade,
    usuario_id uuid not null references public.usuarios(id) on delete cascade,
    matricula text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    unique (turma_id, usuario_id)
);

create table public.categorias (
    id uuid primary key default gen_random_uuid(),
    escopo_id uuid not null,
    tipo_escopo public.tipo_escopo not null,
    nome text not null,
    descricao text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    foreign key (escopo_id, tipo_escopo)
        references public.escopos(id, tipo)
        on delete cascade,
    unique (escopo_id, nome)
);

create table public.localizacoes (
    id uuid primary key default gen_random_uuid(),
    escopo_id uuid not null,
    tipo_escopo public.tipo_escopo not null,
    nome text not null,
    corredor text,
    prateleira text,
    posicao text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    foreign key (escopo_id, tipo_escopo)
        references public.escopos(id, tipo)
        on delete cascade,
    unique (escopo_id, nome)
);

create table public.produtos (
    id uuid primary key default gen_random_uuid(),
    escopo_id uuid not null,
    tipo_escopo public.tipo_escopo not null,
    nome text not null,
    sku text,
    categoria_id uuid references public.categorias(id) on delete set null,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade_minima integer not null default 0 check (quantidade_minima >= 0),
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    foreign key (escopo_id, tipo_escopo)
        references public.escopos(id, tipo)
        on delete cascade,
    unique (escopo_id, sku)
);

create table public.estoques (
    id uuid primary key default gen_random_uuid(),
    escopo_id uuid not null,
    tipo_escopo public.tipo_escopo not null,
    produto_id uuid not null references public.produtos(id) on delete cascade,
    localizacao_id uuid references public.localizacoes(id) on delete set null,
    quantidade integer not null default 0 check (quantidade >= 0),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    foreign key (escopo_id, tipo_escopo)
        references public.escopos(id, tipo)
        on delete cascade,
    unique (escopo_id, produto_id, localizacao_id)
);

create table public.movimentacoes (
    id uuid primary key default gen_random_uuid(),
    escopo_id uuid not null,
    tipo_escopo public.tipo_escopo not null,
    produto_id uuid not null references public.produtos(id) on delete cascade,
    tipo public.tipo_movimentacao not null,
    quantidade integer not null check (quantidade > 0),
    usuario_id uuid references public.usuarios(id) on delete set null,
    origem text,
    destino text,
    observacao text,
    movimentado_em timestamptz not null default now(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    foreign key (escopo_id, tipo_escopo)
        references public.escopos(id, tipo)
        on delete cascade
);

create index categorias_escopo_idx on public.categorias(escopo_id);
create index localizacoes_escopo_idx on public.localizacoes(escopo_id);
create index produtos_escopo_idx on public.produtos(escopo_id);
create index estoques_escopo_idx on public.estoques(escopo_id);
create index movimentacoes_escopo_idx on public.movimentacoes(escopo_id);

create or replace function public.usuario_pode_acessar_escopo(alvo uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select exists (
        select 1
        from public.escopos e
        left join public.gestao_escola ge
            on ge.escola_id = e.escola_id
            and ge.usuario_id = auth.uid()
            and ge.ativo = true
        left join public.alunos_logistica al
            on al.turma_id = e.turma_id
            and al.usuario_id = auth.uid()
            and al.ativo = true
        left join public.usuarios u
            on u.id = auth.uid()
            and u.escopo_id = e.id
        where e.id = alvo
          and e.ativo = true
          and (
              ge.id is not null
              or al.id is not null
              or u.id is not null
          )
    );
$$;

create or replace function public.usuario_pode_alterar_escopo(alvo uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select exists (
        select 1
        from public.escopos e
        left join public.gestao_escola ge
            on ge.escola_id = e.escola_id
            and ge.usuario_id = auth.uid()
            and ge.ativo = true
        left join public.alunos_logistica al
            on al.turma_id = e.turma_id
            and al.usuario_id = auth.uid()
            and al.ativo = true
        left join public.usuarios u
            on u.id = auth.uid()
        where e.id = alvo
          and e.ativo = true
          and (
              ge.id is not null
              or (
                  e.tipo = 'turma_logistica'
                  and al.id is not null
              )
              or (
                  u.escopo_id = e.id
                  and u.perfil in ('gestao', 'professor')
              )
          )
    );
$$;

alter table public.usuarios enable row level security;
alter table public.escolas enable row level security;
alter table public.turmas_logistica enable row level security;
alter table public.escopos enable row level security;
alter table public.gestao_escola enable row level security;
alter table public.alunos_logistica enable row level security;
alter table public.categorias enable row level security;
alter table public.localizacoes enable row level security;
alter table public.produtos enable row level security;
alter table public.estoques enable row level security;
alter table public.movimentacoes enable row level security;

create policy "usuario ve proprio perfil"
    on public.usuarios
    for select
    using (id = auth.uid());

create policy "usuario atualiza proprio perfil"
    on public.usuarios
    for update
    using (id = auth.uid())
    with check (id = auth.uid());

create policy "usuario ve proprio escopo"
    on public.escopos
    for select
    using (public.usuario_pode_acessar_escopo(id));

create policy "usuario ve escola do escopo"
    on public.escolas
    for select
    using (
        exists (
            select 1
            from public.escopos e
            where e.escola_id = escolas.id
              and public.usuario_pode_acessar_escopo(e.id)
        )
    );

create policy "usuario ve turma do escopo"
    on public.turmas_logistica
    for select
    using (
        exists (
            select 1
            from public.escopos e
            where e.turma_id = turmas_logistica.id
              and public.usuario_pode_acessar_escopo(e.id)
        )
    );

create policy "usuario ve vinculo gestao"
    on public.gestao_escola
    for select
    using (usuario_id = auth.uid());

create policy "usuario ve vinculo turma"
    on public.alunos_logistica
    for select
    using (usuario_id = auth.uid());

create policy "usuario ve categorias do escopo"
    on public.categorias
    for select
    using (public.usuario_pode_acessar_escopo(escopo_id));

create policy "usuario ve localizacoes do escopo"
    on public.localizacoes
    for select
    using (public.usuario_pode_acessar_escopo(escopo_id));

create policy "usuario ve produtos do escopo"
    on public.produtos
    for select
    using (public.usuario_pode_acessar_escopo(escopo_id));

create policy "usuario ve estoque do escopo"
    on public.estoques
    for select
    using (public.usuario_pode_acessar_escopo(escopo_id));

create policy "usuario ve movimentacoes do escopo"
    on public.movimentacoes
    for select
    using (public.usuario_pode_acessar_escopo(escopo_id));

create policy "membro altera categorias do escopo"
    on public.categorias
    for all
    using (public.usuario_pode_alterar_escopo(escopo_id))
    with check (public.usuario_pode_alterar_escopo(escopo_id));

create policy "membro altera localizacoes do escopo"
    on public.localizacoes
    for all
    using (public.usuario_pode_alterar_escopo(escopo_id))
    with check (public.usuario_pode_alterar_escopo(escopo_id));

create policy "membro altera produtos do escopo"
    on public.produtos
    for all
    using (public.usuario_pode_alterar_escopo(escopo_id))
    with check (public.usuario_pode_alterar_escopo(escopo_id));

create policy "membro altera estoque do escopo"
    on public.estoques
    for all
    using (public.usuario_pode_alterar_escopo(escopo_id))
    with check (public.usuario_pode_alterar_escopo(escopo_id));

create policy "membro altera movimentacoes do escopo"
    on public.movimentacoes
    for all
    using (public.usuario_pode_alterar_escopo(escopo_id))
    with check (public.usuario_pode_alterar_escopo(escopo_id));
