import { session } from "./store.js";

export const API = {
  BASE_URL: window.ANT_API_BASE_URL || "http://localhost:8000/api/v1",

  async request(path, { method = "GET", body, headers } = {}) {
    const token = session.token;
    const res = await fetch(this.BASE_URL + path, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(headers || {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await readJson(res);
    if (!res.ok) throw new Error(data?.detalhe || data?.detail || data?.mensagem || `API ${res.status}`);
    return data;
  },

  // ── Autenticação ──────────────────────────────────────────────
  async login(email, password) {
    const data = await this.request("/autenticacao/entrar", {
      method: "POST",
      body: { email, senha: password },
    });
    return normalizeAuth(data);
  },

  async register(payload) {
    const data = await this.request("/autenticacao/cadastro", {
      method: "POST",
      body: {
        nome: payload.nome || payload.name,
        email: payload.email,
        senha: payload.senha || payload.password,
        perfil: payload.perfil || payload.profile || "professor",
        turmas: payload.turmas || [],
      },
    });
    return normalizeAuth(data);
  },

  async forgotPassword(email) {
    return this.request("/autenticacao/recuperar-senha", { method: "POST", body: { email } });
  },

  async validateCode(email, code) {
    return this.request("/autenticacao/validar-codigo", {
      method: "POST",
      body: { email, codigo: code },
    });
  },

  async resetPassword(email, code, newPassword) {
    return this.request("/autenticacao/nova-senha", {
      method: "PUT",
      body: { email, codigo: code, nova_senha: newPassword },
    });
  },

  async profile() {
    const usuario = await this.request("/autenticacao/perfil");
    return normalizeUser(usuario);
  },

  async logout() {
    return this.request("/autenticacao/sair", { method: "POST" });
  },

  // ── Usuários (gestão) ────────────────────────────────────────
  async users({ inicio = 0, limite = 100 } = {}) {
    const usuarios = await this.request(`/usuarios?inicio=${inicio}&limite=${limite}`);
    return usuarios.map(normalizeUser);
  },

  // ── Depósitos ─────────────────────────────────────────────────
  async deposits() {
    return this.request("/depositos");
  },

  async createDeposit(data) {
    return this.request("/depositos", { method: "POST", body: data });
  },

  async updateDeposit(depositId, data) {
    return this.request(`/depositos/${depositId}`, { method: "PATCH", body: data });
  },

  async deleteDeposit(depositId) {
    return this.request(`/depositos/${depositId}`, { method: "DELETE" });
  },

  // ── Produtos ──────────────────────────────────────────────────
  async products(depositId, { inicio = 0, limite = 100 } = {}) {
    return this.request(`/${depositId}/produtos?inicio=${inicio}&limite=${limite}`);
  },

  async product(depositId, productId) {
    return this.request(`/${depositId}/produtos/${productId}`);
  },

  async createProduct(depositId, data) {
    return this.request(`/${depositId}/produtos`, { method: "POST", body: data });
  },

  async updateProduct(depositId, productId, data) {
    return this.request(`/${depositId}/produtos/${productId}`, { method: "PATCH", body: data });
  },

  async deleteProduct(depositId, productId) {
    return this.request(`/${depositId}/produtos/${productId}`, { method: "DELETE" });
  },

  // ── Categorias ────────────────────────────────────────────────
  async categories(depositId, { inicio = 0, limite = 200 } = {}) {
    return this.request(`/${depositId}/categorias?inicio=${inicio}&limite=${limite}`);
  },

  async createCategory(depositId, data) {
    return this.request(`/${depositId}/categorias`, { method: "POST", body: data });
  },

  async updateCategory(depositId, categoryId, data) {
    return this.request(`/${depositId}/categorias/${categoryId}`, { method: "PATCH", body: data });
  },

  async deleteCategory(depositId, categoryId) {
    return this.request(`/${depositId}/categorias/${categoryId}`, { method: "DELETE" });
  },

  // ── Localizações ──────────────────────────────────────────────
  async locations(depositId, { inicio = 0, limite = 200 } = {}) {
    return this.request(`/${depositId}/localizacoes?inicio=${inicio}&limite=${limite}`);
  },

  async createLocation(depositId, data) {
    return this.request(`/${depositId}/localizacoes`, { method: "POST", body: data });
  },

  async updateLocation(depositId, locationId, data) {
    return this.request(`/${depositId}/localizacoes/${locationId}`, { method: "PATCH", body: data });
  },

  async deleteLocation(depositId, locationId) {
    return this.request(`/${depositId}/localizacoes/${locationId}`, { method: "DELETE" });
  },

  // ── Estoque ───────────────────────────────────────────────────
  async stock(depositId, { inicio = 0, limite = 100, localizacaoId } = {}) {
    let qs = `inicio=${inicio}&limite=${limite}`;
    if (localizacaoId) qs += `&localizacao_id=${localizacaoId}`;
    return this.request(`/${depositId}/estoque?${qs}`);
  },

  // ── Movimentações ─────────────────────────────────────────────
  async movements(depositId, { inicio = 0, limite = 100, produtoId, pedidoId } = {}) {
    let qs = `inicio=${inicio}&limite=${limite}`;
    if (produtoId) qs += `&produto_id=${produtoId}`;
    if (pedidoId) qs += `&pedido_id=${pedidoId}`;
    return this.request(`/${depositId}/movimentacoes?${qs}`);
  },

  async stockEntry(depositId, data) {
    return this.request(`/${depositId}/movimentacoes/entrada`, { method: "POST", body: data });
  },

  async stockExit(depositId, data) {
    return this.request(`/${depositId}/movimentacoes/saida`, { method: "POST", body: data });
  },

  // ── Pedidos ───────────────────────────────────────────────────
  async orders(depositId, { inicio = 0, limite = 100, usuarioId } = {}) {
    let qs = `inicio=${inicio}&limite=${limite}`;
    if (usuarioId) qs += `&usuario_id=${usuarioId}`;
    return this.request(`/${depositId}/pedidos?${qs}`);
  },

  async createOrder(depositId, data) {
    return this.request(`/${depositId}/pedidos`, { method: "POST", body: data });
  },

  async updateOrder(depositId, orderId, data) {
    return this.request(`/${depositId}/pedidos/${orderId}`, { method: "PATCH", body: data });
  },

  async deleteOrder(depositId, orderId) {
    return this.request(`/${depositId}/pedidos/${orderId}`, { method: "DELETE" });
  },
};

async function readJson(res) {
  const text = await res.text();
  if (!text) return null;
  try { return JSON.parse(text); } catch { return { mensagem: text }; }
}

function normalizeAuth(data) {
  return { user: normalizeUser(data.usuario), token: data.token };
}

export function normalizeUser(usuario) {
  return {
    id: usuario.id,
    name: usuario.nome || usuario.email,
    email: usuario.email,
    role: usuario.perfil === "gestao" ? "Gestao" : "Professor",
    profile: usuario.perfil,
    turmas: usuario.turmas || [],
    ativo: usuario.ativo !== false,
  };
}
