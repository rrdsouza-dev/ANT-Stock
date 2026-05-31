import { api } from "../core/api.js";
import { obterDeposito } from "../core/storage.js";
import { qs, toast } from "../core/utils.js";
import { processarCodigo } from "../scanner/processamento.js";

export function ligarProdutoNovo() {
  const form = qs("#produto-form");
  const codigo = qs("#codigo");
  qs("#validar-codigo")?.addEventListener("click", () => {
    const resultado = processarCodigo(codigo.value);
    codigo.value = resultado.codigo;
    toast(resultado.mensagem);
  });
  form?.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const deposito = obterDeposito();
    const dados = Object.fromEntries(new FormData(form));
    dados.quantidade_minima = Number(dados.quantidade_minima || 0);
    try {
      await api.criarProduto(deposito.id, dados);
      toast("Produto salvo.");
      window.location.hash = "/estoque";
    } catch (erro) {
      toast(`Modo demonstracao: ${erro.message}`);
    }
  });
}
