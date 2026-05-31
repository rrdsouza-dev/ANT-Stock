import { api } from "../core/api.js";
import { navegar, toast } from "../core/utils.js";
import { validarEmail } from "../validacoes/email.js";
import { avaliarSenha } from "../validacoes/senha.js";

export function normalizarCodigo(codigo) {
  return String(codigo || "").replace(/\D/g, "").slice(0, 6);
}

export async function solicitarCodigo(email) {
  if (!validarEmail(email)) {
    throw new Error("Informe um email valido.");
  }
  await api.recuperarSenha(email);
  sessionStorage.setItem("ant_reset_email", email);
  toast("Codigo enviado para seu email.");
  navegar("/validar-codigo");
}

export async function validarCodigo(email, codigo) {
  const codigoLimpo = normalizarCodigo(codigo);
  if (codigoLimpo.length !== 6) {
    throw new Error("Informe os 6 digitos do codigo.");
  }
  await api.validarCodigo(email, codigoLimpo);
  sessionStorage.setItem("ant_reset_codigo", codigoLimpo);
  navegar("/nova-senha");
}

export async function redefinirSenha(email, codigo, senha) {
  const forca = avaliarSenha(senha, email);
  if (!forca.valida) {
    throw new Error(forca.mensagem);
  }
  await api.novaSenha(email, codigo, senha);
  sessionStorage.removeItem("ant_reset_email");
  sessionStorage.removeItem("ant_reset_codigo");
  toast("Senha redefinida com sucesso.");
  navegar("/login");
}
