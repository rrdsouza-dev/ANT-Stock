/**
 * FASE 4 — Picking com CRUD de pedidos.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { openModal } from "../components/modal.js";
import { guardedClick } from "../utils/security.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";

export function PickingPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let ordersData = [];
    let depositId = null;

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Picking" }),
        el("p", { class: "muted", text: "Listas de separação e acompanhamento de pedidos." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: guardedClick(openCreateOrder) }, [
          el("i", { "data-lucide": "plus" }), "Novo pedido",
        ]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(ordersData, "pedidos.txt"); notify("TXT exportado.", "success"); }) },
          [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(ordersData, "pedidos.xlsx", "Pedidos"); notify("Excel exportado.", "success"); }) },
          [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando pedidos…"]),
    ]);

    content.append(head, tableContainer);
    renderIcons(content);

    function openCreateOrder() {
      if (!depositId) { notify("Aguarde…", "warning"); return; }
      const obsEl = el("textarea", { class: "input", style: "height:80px", placeholder: "Observações do pedido (opcional)" });
      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "plus" }), "Criar pedido"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: "Novo Pedido de Picking" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Observações" }), obsEl]),
          errEl,
        ]),
        el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
      ]);

      const backdrop = el("div", { class: "modal-backdrop" }, [card]);
      const close = () => backdrop.remove();
      backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
      cancelBtn.addEventListener("click", close);

      saveBtn.addEventListener("click", async () => {
        errEl.textContent = ""; saveBtn.disabled = true;
        try {
          await API.createOrder(depositId, { observacao: obsEl.value.trim() || undefined });
          notify("Pedido criado!", "success");
          close(); load();
        } catch (err) {
          errEl.textContent = err.message || "Erro ao criar pedido.";
        } finally { saveBtn.disabled = false; }
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
    }

    async function load() {
      try {
        depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits?.length) {
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
          _id: o.id,
          status: o.status || "—",
          observacao: o.observacao || "—",
          criado_em: o.criado_em ? o.criado_em.slice(0, 10) : "—",
          atualizado_em: o.atualizado_em ? o.atualizado_em.slice(0, 10) : "—",
          _raw: o,
        }));

        tableContainer.innerHTML = "";
        if (!ordersData.length) {
          tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum pedido encontrado."]));
          return;
        }

        const statusColors = { aberto: "chip-warning", separado: "chip-info", concluido: "chip-success", cancelado: "chip-danger" };
        const table = DataTable({
          rows: ordersData, pageSize: 10,
          columns: [
            { key: "id", label: "ID" },
            { key: "status", label: "Status", render: (r) =>
              el("span", { class: `chip ${statusColors[r.status] || ""}`, text: r.status })
            },
            { key: "observacao", label: "Observação" },
            { key: "criado_em", label: "Criado em" },
            { key: "acoes", label: "Ações", render: (r) =>
              el("div", { class: "pc-actions" }, [
                el("button", { class: "icon-btn", title: "Marcar como separado", onclick: guardedClick(() => changeStatus(r._raw, "separado")) },
                  [el("i", { "data-lucide": "package-check" })]),
                el("button", { class: "icon-btn", title: "Concluir pedido", onclick: guardedClick(() => changeStatus(r._raw, "concluido")) },
                  [el("i", { "data-lucide": "check-circle-2" })]),
                el("button", { class: "icon-btn", title: "Cancelar pedido", onclick: guardedClick(() => changeStatus(r._raw, "cancelado")) },
                  [el("i", { "data-lucide": "x-circle" })]),
                el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => deleteOrder(r._raw)) },
                  [el("i", { "data-lucide": "trash-2" })]),
              ])
            },
          ],
        });
        tableContainer.appendChild(table.node);
        renderIcons(tableContainer);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar pedidos."]));
        notify(err.message || "Erro.", "error");
      }
    }

    async function changeStatus(order, newStatus) {
      try {
        await API.updateOrder(depositId, order.id, { status: newStatus });
        notify(`Pedido ${newStatus}!`, "success");
        load();
      } catch (err) {
        notify(err.message || "Erro ao atualizar pedido.", "error");
      }
    }

    function deleteOrder(order) {
      openModal({
        title: "Excluir pedido",
        body: "Deseja remover este pedido permanentemente?",
        primaryLabel: "Excluir", danger: true,
        onConfirm: async () => {
          await API.deleteOrder(depositId, order.id);
          notify("Pedido removido.", "warning");
          load();
        },
      });
    }

    load();
  });
}
