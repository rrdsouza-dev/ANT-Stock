export function comLoading(botao, ativo) {
  if (!botao) return;
  if (ativo) {
    botao.dataset.textoOriginal = botao.textContent;
    botao.innerHTML = '<span class="spinner"></span> Aguarde';
    botao.disabled = true;
    return;
  }
  botao.textContent = botao.dataset.textoOriginal || botao.textContent;
  botao.disabled = false;
}
