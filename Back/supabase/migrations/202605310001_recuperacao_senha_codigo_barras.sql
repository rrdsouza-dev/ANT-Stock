-- Recuperacao de senha local e reforcos para operacoes por codigo de barras.
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

create index if not exists ix_codigos_recuperacao_usuario_id on public.codigos_recuperacao(usuario_id);
create index if not exists ix_codigos_recuperacao_codigo_hash on public.codigos_recuperacao(codigo_hash);
create unique index if not exists uq_produtos_codigo_deposito on public.produtos(deposito_id, codigo) where codigo is not null;

drop trigger if exists definir_codigos_recuperacao_atualizado_em on public.codigos_recuperacao;
create trigger definir_codigos_recuperacao_atualizado_em before update on public.codigos_recuperacao
for each row execute function public.definir_atualizado_em();

alter table public.codigos_recuperacao enable row level security;

drop policy if exists "servico backend" on public.codigos_recuperacao;
create policy "servico backend" on public.codigos_recuperacao for all to service_role using (true) with check (true);
