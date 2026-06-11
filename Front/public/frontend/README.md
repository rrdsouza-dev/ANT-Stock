# ANT Stock - Front-End

Front-end estatico em HTML, CSS e JavaScript puro para o ANT Stock. Nao ha React, Vite, JSX, TSX ou etapa de build.

## Stack

- HTML5 + CSS3
- JavaScript ES Modules
- Lucide Icons, Chart.js e SheetJS via CDN
- Roteador hash em `js/router.js`
- Cliente FastAPI em `js/services/api.js`

## Integracao

Por padrao, o front consome `http://localhost:8000/api/v1`. Para trocar a URL sem build, defina `window.ANT_API_BASE_URL` antes de carregar `js/app.js`.

Fluxos conectados:

- Login: `POST /api/v1/autenticacao/entrar`
- Cadastro de professor: `POST /api/v1/autenticacao/cadastro`
- Recuperacao de senha: `POST /api/v1/autenticacao/recuperar-senha`
- Produtos: lista o primeiro deposito de `GET /api/v1/depositos` e consome `GET /api/v1/{deposito_id}/produtos`

## Executar

Sirva esta pasta com qualquer servidor estatico. Exemplo:

```bash
python -m http.server 5173 --directory Front/public/frontend
```
