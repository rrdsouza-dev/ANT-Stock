-- Dados iniciais opcionais para testar o banco Supabase.
insert into public.escopos (id, name, scope_type, active)
values ('00000000-0000-0000-0000-000000000001', 'Escola Demo', 'SCHOOL_MANAGEMENT', true)
on conflict (id) do nothing;

insert into public.categorias (id, scope_id, scope_type, name, description, active)
values (
    '00000000-0000-0000-0000-000000000101',
    '00000000-0000-0000-0000-000000000001',
    'SCHOOL_MANAGEMENT',
    'Materiais',
    'Categoria inicial para testes.',
    true
)
on conflict (id) do nothing;

insert into public.localizacoes (id, scope_id, scope_type, name, active)
values (
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000001',
    'SCHOOL_MANAGEMENT',
    'Almoxarifado',
    true
)
on conflict (id) do nothing;
