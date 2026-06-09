/**
 * API service. Currently returns mocked data. Replace `BASE_URL` and
 * implementations to talk to FastAPI later.
 */

export const API = {
  BASE_URL: "/api",

  async request(path, { method = "GET", body, headers } = {}) {
    const res = await fetch(this.BASE_URL + path, {
      method,
      headers: { "Content-Type": "application/json", ...(headers || {}) },
      body: body ? JSON.stringify(body) : undefined,
      credentials: "include",
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return res.json();
  },

  /* --- Mock implementations (FRONT-END ONLY) --- */

  async login(email, password) {
    await new Promise((r) => setTimeout(r, 600));
    if (!email || !password) throw new Error("Credenciais inválidas");
    return { user: { id: "u1", name: "Aluno Logística", email, role: "Coordenador" }, token: "mock.jwt.token" };
  },

  async register(payload) {
    await new Promise((r) => setTimeout(r, 800));
    return { user: { id: "u2", ...payload }, token: "mock.jwt.token" };
  },

  async forgotPassword(email) {
    await new Promise((r) => setTimeout(r, 600));
    return { ok: true, sentTo: email };
  },

  async resetPassword(_email, _code, _newPassword) {
    await new Promise((r) => setTimeout(r, 500));
    return { ok: true };
  },
};