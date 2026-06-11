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
    if (!res.ok) throw new Error(data?.detail || data?.mensagem || `API ${res.status}`);
    return data;
  },

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
        nome: payload.name,
        email: payload.email,
        senha: payload.password,
        perfil: payload.profile || "professor",
      },
    });
    return normalizeAuth(data);
  },

  async forgotPassword(email) {
    return this.request("/autenticacao/recuperar-senha", { method: "POST", body: { email } });
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

  async deposits() {
    return this.request("/depositos");
  },

  async products(depositId) {
    return this.request(`/${depositId}/produtos`);
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

function normalizeUser(usuario) {
  return {
    id: usuario.id,
    name: usuario.nome || usuario.email,
    email: usuario.email,
    role: usuario.perfil === "gestao" ? "Gestao" : "Professor",
    profile: usuario.perfil,
  };
}
