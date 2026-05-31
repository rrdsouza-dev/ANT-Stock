import { api } from "../core/api.js";
import { obterDeposito } from "../core/storage.js";
import { qs } from "../core/utils.js";
import { produtosMock } from "./mock-data.js";

function linhaProduto(produto) {
  const baixo = produto.status === "Baixo" || produto.quantidade <= produto.quantidade_minima;
  return `
    <tr>
      <td>${produto.codigo || "-"}</td>
      <td>${produto.nome}</td>
      <td>${produto.categoria || produto.categoria_id || "Sem categoria"}</td>
      <td>${produto.quantidade ?? 0}</td>
      <td>${produto.quantidade_minima ?? 0}</td>
      <td><span class="status-pill">${baixo ? "Baixo" : "OK"}</span></td>
      <td><button class="btn btn-secondary" type="button">Editar</button></td>
    </tr>
  `;
}

export async function carregarEstoque() {
  const tbody = qs("#produtos-tbody");
  if (!tbody) return;
  let produtos = produtosMock;
  try {
    const deposito = obterDeposito();
    if (deposito?.id) {
      produtos = await api.listarProdutos(deposito.id);
    }
  } catch {
    produtos = produtosMock;
  }
  tbody.innerHTML = produtos.map(linhaProduto).join("");
}
