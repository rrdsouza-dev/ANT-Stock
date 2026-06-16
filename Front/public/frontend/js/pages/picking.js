import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";

export function PickingPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let ordersData = [];

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Picking" }),
        el("p", { class: "muted", text: "Listas de separação e acompanhamento de pedidos." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(ordersData, "pedidos.txt"); notify("TXT exportado.", "success"); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(ordersData, "pedidos.xlsx", "Pedidos"); notify("Excel exportado.", "success"); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando pedidos..."]),
    ]);

    content.append(head, tableContainer);
    renderIcons(content);

    async function load() {
      try {
        let depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits || deposits.length === 0) {
            tableContainer.innerHTML = "";
            tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum depósito vinculado."]));
            return;
          }
          depositId = deposits[0].id;
          session.setDepositId(depositId);
        }

        const orders = await API.orders(depositId, { limite: 200 });
        ordersData = orders.map(o => ({
          id: o.id ? o.id.slice(0, 8) + "…" : "—",
          status: o.status || "—",
          observacao: o.observacao || "—",
          criado_em: o.criado_em ? o.criado_em.slice(0, 10) : "—",
          atualizado_em: o.atualizado_em ? o.atualizado_em.slice(0, 10) : "—",
        }));

        tableContainer.innerHTML = "";
        if (ordersData.length === 0) {
          tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum pedido encontrado."]));
          return;
        }

        const statusColors = { aberto: "chip-warning", fechado: "chip-success", cancelado: "chip-error" };
        const table = DataTable({
          rows: ordersData, pageSize: 10,
          columns: [
            { key: "id", label: "ID" },
            { key: "status", label: "Status", render: (r) => el("span", { class: `chip ${statusColors[r.status] || ""}`, text: r.status }) },
            { key: "observacao", label: "Observação" },
            { key: "criado_em", label: "Criado em" },
            { key: "atualizado_em", label: "Atualizado em" },
          ],
        });
        tableContainer.appendChild(table.node);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar pedidos."]));
        notify(err.message || "Erro.", "error");
      }
    }

    load();
  });
}
