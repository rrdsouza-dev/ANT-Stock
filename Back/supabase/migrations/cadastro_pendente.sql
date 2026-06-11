-- Tabelas de cadastro pendente e histórico
create table if not exists public.cadastro_pendente (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null,
    email varchar(255) not null unique,
    senha_hash varchar(255) not null,
    perfil_solicitado public.perfil_codigo not null,
    status varchar(20) not null default 'pendente'
);

create table if not exists public.historico_aprovacoes (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    usuario_id uuid not null references public.usuarios(id),
    nome varchar(120) not null,
    email varchar(255) not null,
    perfil public.perfil_codigo not null,
    aprovado_por_id uuid not null references public.usuarios(id)
);

create table if not exists public.historico_recusas (
    id uuid primary key default gen_random_uuid(),
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    nome varchar(120) not null,
    email varchar(255) not null,
    perfil_solicitado public.perfil_codigo not null,
    recusado_por_id uuid not null references public.usuarios(id),
    motivo varchar(500)
);

-- Índices
create index if not exists ix_cadastro_pendente_email on public.cadastro_pendente(email);
create index if not exists ix_cadastro_pendente_status on public.cadastro_pendente(status);
create index if not exists ix_cadastro_pendente_perfil_solicitado on public.cadastro_pendente(perfil_solicitado);
create index if not exists ix_historico_aprovacoes_usuario_id on public.historico_aprovacoes(usuario_id);
create index if not exists ix_historico_aprovacoes_aprovado_por_id on public.historico_aprovacoes(aprovado_por_id);
create index if not exists ix_historico_aprovacoes_email on public.historico_aprovacoes(email);
create index if not exists ix_historico_aprovacoes_perfil on public.historico_aprovacoes(perfil);
create index if not exists ix_historico_recusas_email on public.historico_recusas(email);
create index if not exists ix_historico_recusas_perfil_solicitado on public.historico_recusas(perfil_solicitado);
create index if not exists ix_historico_recusas_recusado_por_id on public.historico_recusas(recusado_por_id);

-- Triggers para atualizado_em
drop trigger if exists definir_cadastro_pendente_atualizado_em on public.cadastro_pendente;
create trigger definir_cadastro_pendente_atualizado_em before update on public.cadastro_pendente
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_historico_aprovacoes_atualizado_em on public.historico_aprovacoes;
create trigger definir_historico_aprovacoes_atualizado_em before update on public.historico_aprovacoes
for each row execute function public.definir_atualizado_em();

drop trigger if exists definir_historico_recusas_atualizado_em on public.historico_recusas;
create trigger definir_historico_recusas_atualizado_em before update on public.historico_recusas
for each row execute function public.definir_atualizado_em();

-- Row Level Security
alter table public.cadastro_pendente enable row level security;
alter table public.historico_aprovacoes enable row level security;
alter table public.historico_recusas enable row level security;

drop policy if exists "servico backend" on public.cadastro_pendente;
create policy "servico backend" on public.cadastro_pendente for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.historico_aprovacoes;
create policy "servico backend" on public.historico_aprovacoes for all to service_role using (true) with check (true);

drop policy if exists "servico backend" on public.historico_recusas;
create policy "servico backend" on public.historico_recusas for all to service_role using (true) with check (true);
