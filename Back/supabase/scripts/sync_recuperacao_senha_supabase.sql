-- Script manual para Supabase: sincroniza perfis, codigos de recuperacao e indices.
-- Execute no SQL Editor do Supabase conectado ao projeto ANT.
create extension if not exists "pgcrypto";

insert into public.perfis (codigo, nome)
values
    ('professor', 'Professor'),
    ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

do $$
declare
    perfil_professor uuid;
    perfil_aluno uuid;
begin
    select id into perfil_professor from public.perfis where codigo::text = 'professor';
    select id into perfil_aluno from public.perfis where codigo::text = 'aluno';

    if perfil_aluno is not null then
        update public.usuarios
        set perfil_id = perfil_professor
        where perfil_id = perfil_aluno;

        delete from public.perfis where id = perfil_aluno;
    end if;
end $$;

do $$
begin
    if exists (
        select 1
        from pg_enum e
        join pg_type t on t.oid = e.enumtypid
        where t.typname = 'perfil_codigo' and e.enumlabel = 'aluno'
    ) then
        alter type perfil_codigo rename to perfil_codigo_old;
        create type perfil_codigo as enum ('professor', 'gestao');
        alter table public.perfis
            alter column codigo type perfil_codigo
            using codigo::text::perfil_codigo;
        drop type perfil_codigo_old;
    end if;
end $$;

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

alter table public.codigos_recuperacao
    alter column usuario_id set not null,
    alter column codigo_hash set not null,
    alter column expira_em set not null,
    alter column usado set default false,
    alter column tentativas set default 0;

alter table public.codigos_recuperacao
    drop constraint if exists ck_codigos_recuperacao_tentativas;

alter table public.codigos_recuperacao
    add constraint ck_codigos_recuperacao_tentativas check (tentativas >= 0);

create index if not exists ix_codigos_recuperacao_usuario_id on public.codigos_recuperacao(usuario_id);
create index if not exists ix_codigos_recuperacao_codigo_hash on public.codigos_recuperacao(codigo_hash);
create index if not exists ix_codigos_recuperacao_expira_em on public.codigos_recuperacao(expira_em);
create index if not exists ix_codigos_recuperacao_usado on public.codigos_recuperacao(usado);
create unique index if not exists uq_produtos_codigo_deposito on public.produtos(deposito_id, codigo) where codigo is not null;

drop trigger if exists definir_codigos_recuperacao_atualizado_em on public.codigos_recuperacao;
create trigger definir_codigos_recuperacao_atualizado_em before update on public.codigos_recuperacao
for each row execute function public.definir_atualizado_em();

alter table public.codigos_recuperacao enable row level security;

drop policy if exists "servico backend" on public.codigos_recuperacao;
create policy "servico backend" on public.codigos_recuperacao for all to service_role using (true) with check (true);
