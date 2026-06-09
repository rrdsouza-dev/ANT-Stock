/** Tiny pub/sub store + localStorage-backed session. */
const KEY = "antstock:session";

const listeners = new Set();
let state = load();

function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || "null") || { user: null }; }
  catch { return { user: null }; }
}
function save() { localStorage.setItem(KEY, JSON.stringify(state)); }

export const session = {
  get user() { return state.user; },
  isAuthenticated() { return !!state.user; },
  signIn(user) { state = { user }; save(); emit(); },
  signOut() { state = { user: null }; save(); emit(); },
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
};

function emit() { for (const fn of listeners) fn(state); }

/** Demo data for products & reports - replace with API.* later. */
export const demoData = {
  products: Array.from({ length: 36 }).map((_, i) => {
    const cats = ["Eletrônicos", "Material Didático", "Móveis", "Logística", "Limpeza"];
    const status = ["Em estoque", "Estoque baixo", "Esgotado"];
    const names = ["Notebook Aluno", "Cadeira Ergonômica", "Caixa Picking", "Kit Apostilas", "Etiquetadora", "Caderno A4", "Mesa Bancada", "Tablet Educacional", "Carrinho Logístico", "Fita Demarcação"];
    return {
      code: `AS-${String(1000 + i)}`,
      name: names[i % names.length] + " " + (i + 1),
      category: cats[i % cats.length],
      quantity: Math.floor(Math.random() * 220),
      status: status[i % status.length],
      updated: new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
    };
  }),
  reports: Array.from({ length: 18 }).map((_, i) => ({
    id: `RL-${String(2000 + i)}`,
    type: ["Estoque Mínimo - Turma Logística", "Picking Mensal", "Entradas e Saídas", "Inventário Geral"][i % 4],
    period: `0${(i % 9) + 1}/05/2024 - ${(i % 28) + 1}/05/2024`,
    status: ["Concluído", "Concluído", "Em processamento"][i % 3],
  })),
};