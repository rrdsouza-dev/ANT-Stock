import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { demoData } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { DataTable } from "../components/table.js";
import { guardedClick } from "../utils/security.js";

export function DashboardPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Relatórios Logísticos" }),
        el("p", { class: "muted", text: "Visão geral de estoque, picking e desempenho das turmas." }),
      ]),
    ]);
    const filters = el("div", { class: "filters-row" }, [
      pill("calendar", "Data/10s"),
      pill("tag", "Categoria"),
      pill("more-vertical", "#10B981"),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(demoData.reports, "relatorios.txt"); notify("Arquivo TXT exportado.", "success"); }) }, [el("i", { "data-lucide": "file-text" }), "Exportar TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(demoData.reports, "relatorios.xlsx", "Relatórios"); notify("Planilha Excel exportada.", "success"); }) }, [el("i", { "data-lucide": "sheet" }), "Exportar Excel"]),
      ]),
    ]);

    // Stat cards
    const stats = el("div", { class: "stat-grid" }, [
      statCard("Itens em Estoque", "12.480", "+4.2%", "up", "package"),
      statCard("Picking Concluídos", "1.823", "+12%", "up", "check-circle-2"),
      statCard("Estoque Baixo", "37", "-3 itens", "down", "alert-triangle"),
      statCard("Alunos Ativos", "156", "+8 novos", "up", "users"),
    ]);

    // Charts
    const pieCard = chartCard("Distribuição de Estoque por Categoria",
      el("div", { class: "chart-box pie" }, [el("canvas", { id: "chart-pie" })]),
      el("div", { class: "legend" }, [
        legendItem("#10b981", "Eletrônicos"),
        legendItem("#7ed29c", "Material Didático"),
        legendItem("#bde9cb", "Móveis"),
      ]),
    );
    const barCard = chartCard("Eficiência Picking por Aluno",
      el("div", { class: "chart-box" }, [el("canvas", { id: "chart-bar" })]),
    );
    const dash = el("div", { class: "dash-grid" }, [pieCard, barCard]);

    // Recent reports table
    const table = DataTable({
      rows: demoData.reports,
      pageSize: 6,
      columns: [
        { key: "type", label: "Tipo" },
        { key: "period", label: "Período" },
        { key: "status", label: "Status", render: (r) => {
          const cls = r.status === "Concluído" ? "chip-success" : "chip-warning";
          return el("span", { class: `chip ${cls}`, text: r.status });
        } },
        { key: "id", label: "Ações", render: (r) => el("button", { class: "btn btn-outline btn-sm", onclick: () => notify(`Visualizando ${r.id}`, "info") }, ["Visualizar"]) },
      ],
    });

    const recentWrap = el("div", { style: "margin-top:18px" }, [
      el("div", { style: "display:flex;align-items:center;justify-content:space-between;margin-bottom:10px" }, [
        el("h2", { text: "Relatórios Recentes" }),
      ]),
      table.node,
    ]);

    content.append(head, filters, stats, dash, recentWrap);
    renderIcons(content);

    // Draw charts after mount
    setTimeout(() => drawCharts(), 0);
  });
}

function pill(icon, label) {
  const p = el("button", { class: "pill-select" }, [el("i", { "data-lucide": icon }), el("span", { text: label }), el("i", { "data-lucide": "chevron-down" })]);
  return p;
}
function statCard(label, value, trend, dir, icon) {
  const node = el("div", { class: "stat-card" }, [
    el("div", { class: "icon-pill" }, [el("i", { "data-lucide": icon })]),
    el("div", { class: "label", text: label }),
    el("div", { class: "value", text: value }),
    el("div", { class: `trend ${dir}` }, [el("i", { "data-lucide": dir === "up" ? "trending-up" : "trending-down" }), el("span", { text: trend })]),
  ]);
  return node;
}
function chartCard(title, ...children) {
  return el("div", { class: "card chart-card" }, [
    el("div", { class: "chart-header" }, [el("h3", { text: title }), el("button", { class: "icon-btn", title: "Mais" }, [el("i", { "data-lucide": "more-horizontal" })])]),
    ...children,
  ]);
}
function legendItem(color, label) {
  return el("span", {}, [el("i", { style: `background:${color}` }), label]);
}

function drawCharts() {
  if (!window.Chart) return;
  const pie = document.getElementById("chart-pie");
  const bar = document.getElementById("chart-bar");
  if (pie) {
    new Chart(pie, {
      type: "doughnut",
      data: {
        labels: ["Eletrônicos", "Material Didático", "Móveis"],
        datasets: [{ data: [42, 33, 25], backgroundColor: ["#10b981", "#7ed29c", "#bde9cb"], borderWidth: 0 }],
      },
      options: { plugins: { legend: { display: false } }, cutout: "55%", responsive: true, maintainAspectRatio: false },
    });
  }
  if (bar) {
    new Chart(bar, {
      type: "bar",
      data: {
        labels: ["João Silva", "Maria Santos", "Pedro Lima", "Ana Costa", "Bruno R.", "Carla M.", "Lucas A."],
        datasets: [
          { label: "Picking", data: [32000, 28000, 35000, 22000, 30000, 36000, 25000], backgroundColor: "#10b981", borderRadius: 8, barThickness: 22 },
          { label: "Meta", data: [40000, 36000, 38000, 32000, 36000, 40000, 32000], backgroundColor: "#bde9cb", borderRadius: 8, barThickness: 22 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { ticks: { callback: (v) => v >= 1000 ? v/1000 + "K" : v }, grid: { color: "#eef3f0" } },
        },
      },
    });
  }
}