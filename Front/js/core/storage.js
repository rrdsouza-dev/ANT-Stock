import { DEPOSITO_KEY, TOKEN_KEY, USER_KEY } from "../config/config.js";

export function salvarSessao(token, usuario) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(usuario));
}

export function obterToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function obterUsuario() {
  const bruto = localStorage.getItem(USER_KEY);
  return bruto ? JSON.parse(bruto) : null;
}

export function limparSessao() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(DEPOSITO_KEY);
}

export function salvarDeposito(deposito) {
  localStorage.setItem(DEPOSITO_KEY, JSON.stringify(deposito));
}

export function obterDeposito() {
  const bruto = localStorage.getItem(DEPOSITO_KEY);
  return bruto ? JSON.parse(bruto) : null;
}
