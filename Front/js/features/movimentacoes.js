import { api } from "../core/api.js";
import { obterDeposito } from "../core/storage.js";
import { qs, toast } from "../core/utils.js";
import { movimentacoesMock } from "./mock-data.js";

export async function carregarMovimentacoes() {
  const tbody = qs("#movimentacoes-tbody");
  if (!tbody) return;
  let itens = movimentacoesMock;
  try {
    const deposito = obterDeposito();
    if (deposito?.id) itens = await api.listarMovimentacoes(deposito.id);
  } catch {
    itens = movimentacoesMock;
  }
  tbody.innerHTML = itens.map((item) => `
    <tr>
      <td>${item.data || item.movimentado_em || "-"}</td>
      <td>${item.produto || item.produto_id}</td>
      <td>${item.tipo}</td>
      <td>${item.quantidade}</td>
      <td>${item.usuario || item.usuario_id || "-"}</td>
      <td>${item.observacao || "-"}</td>
    </tr>
  `).join("");
}

export function ligarMovimentacaoNova() {
  qs("#movimentacao-form")?.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const deposito = obterDeposito();
    const dados = Object.fromEntries(new FormData(evento.currentTarget));
    dados.quantidade = Number(dados.quantidade);
    try {
      await api.registrarMovimentacao(deposito.id, dados);
      toast("Movimentacao registrada.");
      window.location.hash = "/movimentacoes";
    } catch (erro) {
      toast(`Modo demonstracao: ${erro.message}`);
    }
  });
}
