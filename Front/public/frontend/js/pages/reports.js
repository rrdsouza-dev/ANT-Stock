import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { DataTable } from "../components/table.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";

export function ReportsPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let movementsData = [];

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Relatórios" }),
        el("p", { class: "muted", text: "Histórico de movimentações de estoque registradas no sistema." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportTxt(movementsData, "movimentacoes.txt");
          notify("TXT exportado.", "success");
        }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportExcel(movementsData, "movimentacoes.xlsx", "Movimentações");
          notify("Excel exportado.", "success");
        }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando movimentações..."]),
    ]);

    content.append(head, tableContainer);
    renderIcons(content);

    async function loadReports() {
      try {
        let depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits || deposits.length === 0) {
            tableContainer.innerHTML = "";
            tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum depósito vinculado ao usuário."]));
            return;
          }
          depositId = deposits[0].id;
          session.setDepositId(depositId);
        }

        const movements = await API.movements(depositId, { limite: 200 });
        movementsData = movements.map(normalizeMovement);

        tableContainer.innerHTML = "";

        if (movementsData.length === 0) {
          tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhuma movimentação registrada."]));
          return;
        }

        const table = DataTable({
          rows: movementsData,
          pageSize: 8,
          columns: [
            { key: "id", label: "ID", render: (r) => el("span", { class: "muted", style: "font-size:0.78em", text: r.id ? r.id.slice(0, 8) + "…" : "—" }) },
            { key: "tipo", label: "Tipo", render: (r) => {
              const cls = r.tipo === "entrada" ? "chip-success" : "chip-warning";
              return el("span", { class: `chip ${cls}`, text: r.tipo });
            }},
            { key: "produto_id", label: "Produto ID", render: (r) => el("span", { class: "muted", style: "font-size:0.78em", text: r.produto_id ? r.produto_id.slice(0, 8) + "…" : "—" }) },
            { key: "quantidade", label: "Quantidade" },
            { key: "data", label: "Data" },
            { key: "observacao", label: "Observação" },
          ],
        });
        tableContainer.appendChild(table.node);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar movimentações."]));
        notify(err.message || "Erro ao carregar relatórios.", "error");
      }
    }

    loadReports();
  });
}

function normalizeMovement(m) {
  return {
    id: m.id,
    tipo: m.tipo || "—",
    produto_id: m.produto_id,
    quantidade: m.quantidade ?? "—",
    data: m.movimentado_em ? m.movimentado_em.slice(0, 10) : (m.criado_em ? m.criado_em.slice(0, 10) : "—"),
    observacao: m.observacao || "—",
  };
}
