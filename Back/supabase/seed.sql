-- Dados iniciais opcionais para testar o banco Supabase.
insert into public.perfis (codigo, nome)
values
    ('professor', 'Professor'),
    ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

insert into public.depositos (id, nome, tipo, descricao, ativo)
values (
    '00000000-0000-0000-0000-000000000001',
    'Estoque Escolar',
    'escolar',
    'Deposito inicial para testes.',
    true
)
on conflict (id) do nothing;

insert into public.categorias (id, deposito_id, nome, descricao, ativo)
values (
    '00000000-0000-0000-0000-000000000101',
    '00000000-0000-0000-0000-000000000001',
    'Materiais',
    'Categoria inicial para testes.',
    true
)
on conflict (id) do nothing;

insert into public.localizacoes (id, deposito_id, nome, ativo)
values (
    '00000000-0000-0000-0000-000000000201',
    '00000000-0000-0000-0000-000000000001',
    'Almoxarifado',
    true
)
on conflict (id) do nothing;
