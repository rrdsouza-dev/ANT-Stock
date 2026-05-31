import { API_URL, TIMEOUT } from "../config/config.js";
import { obterToken } from "./storage.js";

async function requisicao(endpoint, opcoes = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT);
  const headers = {
    "Content-Type": "application/json",
    ...(opcoes.headers || {}),
  };
  const token = obterToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const resposta = await fetch(`${API_URL}${endpoint}`, {
      ...opcoes,
      headers,
      signal: controller.signal,
    });
    const texto = await resposta.text();
    const dados = texto ? JSON.parse(texto) : null;
    if (!resposta.ok) {
      throw new Error(dados?.detail?.mensagem || dados?.mensagem || "Nao foi possivel concluir a requisicao.");
    }
    return dados;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  login: (email, senha) => requisicao("/autenticacao/entrar", {
    method: "POST",
    body: JSON.stringify({ email, senha }),
  }),
  recuperarSenha: (email) => requisicao("/autenticacao/recuperar-senha", {
    method: "POST",
    body: JSON.stringify({ email }),
  }),
  validarCodigo: (email, codigo) => requisicao("/autenticacao/validar-codigo", {
    method: "POST",
    body: JSON.stringify({ email, codigo }),
  }),
  novaSenha: (email, codigo, senha) => requisicao("/autenticacao/nova-senha", {
    method: "PUT",
    body: JSON.stringify({ email, codigo, nova_senha: senha }),
  }),
  listarProdutos: (depositoId) => requisicao(`/${depositoId}/produtos`),
  criarProduto: (depositoId, dados) => requisicao(`/${depositoId}/produtos`, {
    method: "POST",
    body: JSON.stringify(dados),
  }),
  buscarProdutoPorCodigo: (depositoId, codigo) => requisicao(`/${depositoId}/produtos/codigo/${encodeURIComponent(codigo)}`),
  listarMovimentacoes: (depositoId) => requisicao(`/${depositoId}/movimentacoes`),
  registrarMovimentacao: (depositoId, dados) => requisicao(`/${depositoId}/movimentacoes/codigo`, {
    method: "POST",
    body: JSON.stringify(dados),
  }),
};
