-- Dados iniciais opcionais para testar o banco Supabase.
insert into public.perfis (codigo, nome)
values
    ('aluno', 'Aluno'),
    ('professor', 'Professor'),
    ('gestao', 'Gestao')
on conflict (codigo) do update set nome = excluded.nome;

insert into public.categorias (id, nome, descricao, ativo)
values (
    '00000000-0000-0000-0000-000000000101',
    'Materiais',
    'Categoria inicial para testes.',
    true
)
on conflict (id) do nothing;

insert into public.localizacoes (id, nome, ativo)
values (
    '00000000-0000-0000-0000-000000000201',
    'Almoxarifado',
    true
)
on conflict (id) do nothing;
