import { obterUsuario } from "../core/storage.js";
import { qs, toast } from "../core/utils.js";

export function carregarPerfil() {
  const usuario = obterUsuario();
  if (!usuario) return;
  qs("#perfil-nome").value = usuario.nome || "";
  qs("#perfil-email").value = usuario.email || "";
  qs("#perfil-tipo").value = usuario.perfil || "";
  qs("#perfil-form")?.addEventListener("submit", (evento) => {
    evento.preventDefault();
    toast("Perfil pronto para integracao com endpoint de atualizacao.");
  });
}
