import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { demoData } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";

export function ExportsPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [el("div", {}, [el("h1", { text: "Exportações" }), el("p", { class: "muted", text: "Exporte os dados do sistema para uso externo." })])]);
    const dataSets = [
      { key: "products", label: "Estoque (produtos)", rows: demoData.products },
      { key: "reports", label: "Relatórios logísticos", rows: demoData.reports },
    ];
    const grid = el("div", { class: "product-grid" });
    for (const ds of dataSets) {
      grid.appendChild(el("div", { class: "card card-pad" }, [
        el("h3", { text: ds.label }),
        el("p", { class: "muted", style: "margin:6px 0 16px", text: `${ds.rows.length} registro(s) disponíveis para exportação.` }),
        el("div", { style: "display:flex;gap:10px;flex-wrap:wrap" }, [
          el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(ds.rows, `${ds.key}.txt`); notify("TXT exportado."); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
          el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(ds.rows, `${ds.key}.xlsx`, ds.label); notify("Excel exportado."); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
        ]),
      ]));
    }
    content.append(head, grid);
    renderIcons(content);
  });
}