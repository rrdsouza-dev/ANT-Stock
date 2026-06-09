import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { DataTable } from "../components/table.js";
import { demoData } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";

export function ReportsPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Relatórios" }),
        el("p", { class: "muted", text: "Histórico de relatórios gerados pela equipe de logística." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(demoData.reports, "relatorios.txt"); notify("TXT exportado."); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(demoData.reports, "relatorios.xlsx", "Relatórios"); notify("Excel exportado."); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);
    const table = DataTable({
      rows: demoData.reports, pageSize: 8,
      columns: [
        { key: "id", label: "ID" },
        { key: "type", label: "Tipo" },
        { key: "period", label: "Período" },
        { key: "status", label: "Status", render: (r) => el("span", { class: "chip " + (r.status === "Concluído" ? "chip-success" : "chip-warning"), text: r.status }) },
        { key: "id", label: "Ações", render: (r) => el("button", { class: "btn btn-outline btn-sm", onclick: () => notify(`Visualizando ${r.id}`, "info") }, ["Visualizar"]) },
      ],
    });
    content.append(head, table.node);
    renderIcons(content);
  });
}