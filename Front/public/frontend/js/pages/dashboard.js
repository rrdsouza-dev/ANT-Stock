import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { DataTable } from "../components/table.js";
import { guardedClick } from "../utils/security.js";

export function DashboardPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let movementsData = [];
    let productsData = [];
    let stockData = [];

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Relatórios Logísticos" }),
        el("p", { class: "muted", text: "Visão geral de estoque, picking e desempenho operacional." }),
      ]),
    ]);

    const exportRow = el("div", { class: "filters-row" }, [
      pill("calendar", "Data"),
      pill("tag", "Categoria"),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportTxt(movementsData, "movimentacoes.txt");
          notify("Arquivo TXT exportado.", "success");
        }) }, [el("i", { "data-lucide": "file-text" }), "Exportar TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportExcel(movementsData, "movimentacoes.xlsx", "Movimentações");
          notify("Planilha Excel exportada.", "success");
        }) }, [el("i", { "data-lucide": "sheet" }), "Exportar Excel"]),
      ]),
    ]);

    // Stat cards (will be updated after data loads)
    const statTotal = el("div", { class: "value", text: "—" });
    const statEntradas = el("div", { class: "value", text: "—" });
    const statBaixo = el("div", { class: "value", text: "—" });
    const statPedidos = el("div", { class: "value", text: "—" });

    const stats = el("div", { class: "stat-grid" }, [
      statCardNode("Itens em Estoque", statTotal, "package"),
      statCardNode("Entradas no Período", statEntradas, "check-circle-2"),
      statCardNode("Estoque Abaixo do Mínimo", statBaixo, "alert-triangle"),
      statCardNode("Pedidos em Aberto", statPedidos, "users"),
    ]);

    // Charts containers
    const pieCard = chartCard("Distribuição de Estoque por Categoria",
      el("div", { class: "chart-box pie" }, [el("canvas", { id: "chart-pie" })]),
      el("div", { class: "legend", id: "pie-legend" }, []),
    );
    const barCard = chartCard("Movimentações Recentes (Entradas vs Saídas)",
      el("div", { class: "chart-box" }, [el("canvas", { id: "chart-bar" })]),
    );
    const dash = el("div", { class: "dash-grid" }, [pieCard, barCard]);

    // Movements table
    const tableWrap = el("div", { style: "margin-top:18px" }, [
      el("div", { style: "display:flex;align-items:center;justify-content:space-between;margin-bottom:10px" }, [
        el("h2", { text: "Movimentações Recentes" }),
      ]),
      el("div", { id: "movements-table-container" }, [
        el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando dados..."]),
      ]),
    ]);

    content.append(head, exportRow, stats, dash, tableWrap);
    renderIcons(content);

    async function loadDashboard() {
      try {
        const deposits = await API.deposits();
        if (!deposits || deposits.length === 0) {
          notify("Nenhum depósito vinculado ao usuário.", "warning");
          updateStats([], [], []);
          return;
        }

        // Persist depositId for other pages
        const deposit = deposits[0];
        session.setDepositId(deposit.id);

        const [products, stock, movements, orders] = await Promise.all([
          API.products(deposit.id, { limite: 200 }).catch(() => []),
          API.stock(deposit.id, { limite: 200 }).catch(() => []),
          API.movements(deposit.id, { limite: 100 }).catch(() => []),
          API.orders(deposit.id, { limite: 100 }).catch(() => []),
        ]);

        productsData = products;
        stockData = stock;
        movementsData = movements.map(normalizeMovement);

        updateStats(products, stock, orders, movements);
        renderMovementsTable(movementsData);

        // Build chart data
        const categories = await API.categories(deposit.id, { limite: 200 }).catch(() => []);
        setTimeout(() => drawCharts(products, stock, categories, movements), 0);
      } catch (err) {
        notify(err.message || "Erro ao carregar dashboard.", "error");
        renderMovementsTable([]);
      }
    }

    function updateStats(products, stock, orders, movements) {
      const totalItems = stock.reduce((s, e) => s + (e.quantidade || 0), 0);
      statTotal.textContent = totalItems.toLocaleString("pt-BR");

      const entradas = (movements || []).filter(m => m.tipo === "entrada").length;
      statEntradas.textContent = entradas.toLocaleString("pt-BR");

      const baixo = products.filter(p => {
        const estoque = stock.filter(e => e.produto_id === p.id).reduce((s, e) => s + e.quantidade, 0);
        return estoque < p.quantidade_minima;
      }).length;
      statBaixo.textContent = baixo.toLocaleString("pt-BR");

      const pedidosAbertos = (orders || []).filter(o => o.status === "aberto").length;
      statPedidos.textContent = pedidosAbertos.toLocaleString("pt-BR");
    }

    function renderMovementsTable(rows) {
      const container = document.getElementById("movements-table-container");
      if (!container) return;
      container.innerHTML = "";
      if (rows.length === 0) {
        container.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhuma movimentação encontrada."]));
        return;
      }
      const table = DataTable({
        rows,
        pageSize: 6,
        columns: [
          { key: "tipo", label: "Tipo", render: (r) => {
            const cls = r.tipo === "entrada" ? "chip-success" : "chip-warning";
            return el("span", { class: `chip ${cls}`, text: r.tipo });
          }},
          { key: "produto", label: "Produto" },
          { key: "quantidade", label: "Quantidade" },
          { key: "data", label: "Data" },
          { key: "observacao", label: "Observação" },
        ],
      });
      container.appendChild(table.node);
    }

    loadDashboard();
  });
}

function normalizeMovement(m) {
  return {
    tipo: m.tipo || "—",
    produto: m.produto_id || "—",
    quantidade: m.quantidade ?? "—",
    data: m.movimentado_em ? m.movimentado_em.slice(0, 10) : (m.criado_em ? m.criado_em.slice(0, 10) : "—"),
    observacao: m.observacao || "—",
  };
}

function pill(icon, label) {
  return el("button", { class: "pill-select" }, [
    el("i", { "data-lucide": icon }),
    el("span", { text: label }),
    el("i", { "data-lucide": "chevron-down" }),
  ]);
}

function statCardNode(label, valueEl, icon) {
  return el("div", { class: "stat-card" }, [
    el("div", { class: "icon-pill" }, [el("i", { "data-lucide": icon })]),
    el("div", { class: "label", text: label }),
    valueEl,
  ]);
}

function chartCard(title, ...children) {
  return el("div", { class: "card chart-card" }, [
    el("div", { class: "chart-header" }, [
      el("h3", { text: title }),
      el("button", { class: "icon-btn", title: "Mais" }, [el("i", { "data-lucide": "more-horizontal" })]),
    ]),
    ...children,
  ]);
}

function drawCharts(products, stock, categories, movements) {
  if (!window.Chart) return;

  // Build category map: categoryId -> name
  const catMap = {};
  for (const c of categories) catMap[c.id] = c.nome;

  // Aggregate stock by category
  const stockByCat = {};
  for (const p of products) {
    const catName = catMap[p.categoria_id] || "Sem categoria";
    const prodStock = stock.filter(e => e.produto_id === p.id).reduce((s, e) => s + e.quantidade, 0);
    stockByCat[catName] = (stockByCat[catName] || 0) + prodStock;
  }
  const catLabels = Object.keys(stockByCat);
  const catValues = catLabels.map(k => stockByCat[k]);
  const palette = ["#10b981","#7ed29c","#bde9cb","#6366f1","#f59e0b","#ef4444","#3b82f6"];

  const pie = document.getElementById("chart-pie");
  if (pie) {
    new Chart(pie, {
      type: "doughnut",
      data: {
        labels: catLabels.length ? catLabels : ["Sem dados"],
        datasets: [{ data: catValues.length ? catValues : [1], backgroundColor: palette.slice(0, catLabels.length || 1), borderWidth: 0 }],
      },
      options: { plugins: { legend: { display: false } }, cutout: "55%", responsive: true, maintainAspectRatio: false },
    });

    // Render legend
    const legend = document.getElementById("pie-legend");
    if (legend) {
      legend.innerHTML = "";
      catLabels.forEach((l, i) => {
        const span = el("span", {}, []);
        const dot = el("i", { style: `background:${palette[i % palette.length]};width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:6px` });
        span.appendChild(dot);
        span.appendChild(document.createTextNode(l));
        legend.appendChild(span);
      });
    }
  }

  // Bar: last 7 days entries vs exits
  const today = new Date();
  const dayLabels = [];
  const entryData = [];
  const exitData = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    dayLabels.push(key.slice(5)); // MM-DD
    const dayMov = movements.filter(m => {
      const mDate = (m.movimentado_em || m.criado_em || "").slice(0, 10);
      return mDate === key;
    });
    entryData.push(dayMov.filter(m => m.tipo === "entrada").reduce((s, m) => s + m.quantidade, 0));
    exitData.push(dayMov.filter(m => m.tipo === "saida").reduce((s, m) => s + m.quantidade, 0));
  }

  const bar = document.getElementById("chart-bar");
  if (bar) {
    new Chart(bar, {
      type: "bar",
      data: {
        labels: dayLabels,
        datasets: [
          { label: "Entradas", data: entryData, backgroundColor: "#10b981", borderRadius: 8, barThickness: 22 },
          { label: "Saídas", data: exitData, backgroundColor: "#bde9cb", borderRadius: 8, barThickness: 22 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: true, position: "top" } },
        scales: {
          x: { grid: { display: false } },
          y: { ticks: { callback: (v) => v >= 1000 ? v / 1000 + "K" : v }, grid: { color: "#eef3f0" } },
        },
      },
    });
  }
}
