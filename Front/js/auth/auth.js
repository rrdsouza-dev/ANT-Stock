import { DEPOSITOS } from "../config/config.js";
import { api } from "../core/api.js";
import { limparSessao, obterUsuario, salvarDeposito, salvarSessao } from "../core/storage.js";
import { navegar, toast } from "../core/utils.js";
import { validarEmail } from "../validacoes/email.js";

let tentativas = Number(sessionStorage.getItem("ant_login_tentativas") || 0);

export async function login(email, senha) {
  if (!validarEmail(email)) {
    throw new Error("Informe um email valido.");
  }
  if (tentativas >= 5) {
    throw new Error("Muitas tentativas. Aguarde alguns minutos antes de tentar novamente.");
  }
  try {
    const resposta = await api.login(email, senha);
    salvarSessao(resposta.token, resposta.usuario);
    const deposito = resposta.usuario.perfil === "gestao" ? DEPOSITOS.gestao : DEPOSITOS.turma2;
    salvarDeposito(deposito);
    tentativas = 0;
    sessionStorage.removeItem("ant_login_tentativas");
    navegar(resposta.usuario.perfil === "gestao" ? "/dashboard-gestao" : "/dashboard-professor");
  } catch (erro) {
    tentativas += 1;
    sessionStorage.setItem("ant_login_tentativas", String(tentativas));
    throw erro;
  }
}

export function exigirAutenticacao() {
  if (!obterUsuario()) {
    navegar("/login");
    return false;
  }
  return true;
}

export function logout() {
  limparSessao();
  toast("Sessao encerrada.");
  navegar("/login");
}
