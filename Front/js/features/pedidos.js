import { qs } from "../core/utils.js";
import { pedidosMock } from "./mock-data.js";

export function carregarPedidos() {
  const tbody = qs("#pedidos-tbody");
  if (!tbody) return;
  tbody.innerHTML = pedidosMock.map((pedido) => `
    <tr>
      <td>${pedido.id}</td>
      <td>${pedido.data}</td>
      <td>${pedido.itens}</td>
      <td><span class="status-pill">${pedido.status}</span></td>
      <td><button class="btn btn-secondary" type="button">Visualizar</button></td>
    </tr>
  `).join("");
}
