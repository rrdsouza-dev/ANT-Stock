# ANT

Sistema WMS leve para gerenciamento de estoque, produtos, pedidos e movimentacoes logisticas.

O ANT foi desenvolvido como projeto academico para apoiar o aprendizado de logistica e desenvolvimento web. A proposta e manter um sistema simples, funcional e facil de evoluir.

## Objetivos

- Controlar estoque.
- Registrar entradas e saidas de produtos.
- Organizar produtos e localizacoes.
- Acompanhar pedidos e movimentacoes.
- Simular operacoes logisticas reais.
- Integrar front-end, back-end e Supabase.

## Funcionalidades

### Produtos

- Cadastro de produtos.
- Controle de categorias.
- Localizacao de itens.
- Quantidade minima.

### Estoque

- Entrada de mercadorias.
- Saida de produtos.
- Saldo por produto e localizacao.
- Atualizacao automatica por movimentacao.

### Movimentacoes

- Historico operacional.
- Registro de usuario, produto e pedido.
- Origem e destino por localizacao.

### Usuarios e Acesso

- Cadastro e login.
- Perfis fixos: Aluno, Professor e Gestao.
- Estrutura preparada para Supabase Auth.

## Modelagem

Entidades principais:

- `perfis`
- `usuarios`
- `categorias`
- `localizacoes`
- `produtos`
- `estoque`
- `movimentacoes`
- `pedidos`
- `itens_pedido`

Relacionamentos principais usam chaves simples como `usuario_id`, `produto_id` e `pedido_id`.

## Tecnologias

### Back-end

- Python
- FastAPI
- SQLModel
- SQLAlchemy async

### Front-end

- React
- JavaScript
- HTML
- CSS

### Banco e Autenticacao

- Supabase
- PostgreSQL

## Objetivo Academico

Este projeto foi desenvolvido como base de estudo para estudantes de logistica e tecnologia, com foco em um WMS minimalista, moderno e de facil manutencao.

## Licenca

MIT.
