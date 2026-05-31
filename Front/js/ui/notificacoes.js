import { toast } from "../core/utils.js";

export function sucesso(mensagem) {
  toast(mensagem);
}

export function erro(mensagem) {
  toast(mensagem);
}
