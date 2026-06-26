/**
 * FASE 3 + FASE 4 — Entradas e Saídas com leitor de código de barras e CRUD.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { BarcodeScanner } from "../components/barcodeScanner.js";
import { openMovementModal, openPreviewCard, openEntryModal, openExitModal, openScanModal } from "../components/productModal.js";

export function InventoryPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let movementsData = [];
    let products = [];
    let categories = [];
    let depositId = null;

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Entradas e Saídas" }),
        el("p", { class: "muted", text: "Registre e acompanhe movimentações de estoque. Use leitor de código de barras ou busca manual." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-ghost btn-sm", title: "Visualiza o card que abre após escaneamento real — sem criar movimentações",
          onclick: guardedClick(() => openPreviewCard({ depositId, products: products.map(p => ({...p, nome: p.name, codigo: p.code})), categories: [], onSave: loadMovements })) }, [
          el("i", { "data-lucide": "eye" }), " Visualizar Card",
        ]),
        el("button", { class: "btn btn-soft", onclick: guardedClick(() => { if (!depositId) { notify("Aguarde…", "warning"); return; } openEntryModal({ depositId, products: products.map(p => ({id:p.id, nome:p.name, codigo:p.code})), categories, onSave: loadMovements }); }) }, [
          el("i", { "data-lucide": "arrow-down-circle" }), " Entrada",
        ]),
        el("button", { class: "btn btn-soft", onclick: guardedClick(() => { if (!depositId) { notify("Aguarde…", "warning"); return; } openExitModal({ depositId, products: products.map(p => ({id:p.id, nome:p.name, codigo:p.code})), categories, onSave: loadMovements }); }) }, [
          el("i", { "data-lucide": "arrow-up-circle" }), " Saída",
        ]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(movementsData, "movimentacoes.txt"); notify("TXT exportado.", "success"); }) },
          [el("i", { "data-lucide": "file-text" }), " TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(movementsData, "movimentacoes.xlsx", "Movimentações"); notify("Excel exportado.", "success"); }) },
          [el("i", { "data-lucide": "sheet" }), " Excel"]),
      ]),
    ]);

    // ── Barcode scanner panel ──────────────────────────────────
    const scannerSection = el("div", { class: "card card-pad", style: "margin-bottom:18px" }, [
      el("h3", { text: "Leitor de Código de Barras", style: "margin-bottom:12px" }),
    ]);

    const scanner = BarcodeScanner({
      autoFocus: false,
      onScan: ({ code, refresh }) => {
        handleScan(code, refresh);
      },
    });
    scannerSection.appendChild(scanner.node);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando movimentações…"]),
    ]);

    content.append(head, scannerSection, tableContainer);
    renderIcons(content);

    async function handleScan(code, refreshHistory) {
      if (!depositId) { notify("Aguarde — carregando depósito…", "warning"); return; }
      try {
        // Try to find product by barcode via API
        const allCats = await API.categories(depositId, { limite: 200 }).catch(() => []);
        const allProds = await API.products(depositId, { limite: 200 }).catch(() => products.map(p => ({id:p.id, nome:p.name, codigo:p.code})));
        const locs = await API.locations(depositId, { limite: 200 }).catch(() => []);

        // Get stock quantities for each product
        const stockData = await API.stock(depositId, { limite: 500 }).catch(() => []);
        const stockMap = {};
        for (const s of stockData) stockMap[s.produto_id] = (stockMap[s.produto_id] || 0) + s.quantidade;
        const prodsWithQty = allProds.map(p => ({ ...p, quantidade: stockMap[p.id] || 0 }));

        refreshHistory?.();
        openScanModal({
          depositId,
          code,
          products: prodsWithQty,
          categories: allCats,
          locations: locs,
          onSave: loadMovements,
        });
      } catch (err) {
        notify(err.message || "Erro na leitura.", "error");
      }
    }

    // legacy compat
    function openMovModal() {}

    function renderTable(rows) {
      tableContainer.innerHTML = "";
      if (!rows.length) {
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhuma movimentação registrada."]));
        return;
      }
      const table = DataTable({
        rows, pageSize: 10,
        columns: [
          { key: "tipo", label: "Tipo", render: (r) =>
            el("span", { class: `chip ${r.tipo === "entrada" ? "chip-success" : "chip-warning"}`, text: r.tipo })
          },
          { key: "produto", label: "Produto" },
          { key: "quantidade", label: "Qtd" },
          { key: "data", label: "Data" },
          { key: "observacao", label: "Observação" },
        ],
      });
      tableContainer.appendChild(table.node);
    }

    async function loadMovements() {
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

        // Load movements, products AND categories (for scan and manual entry/exit modals)
        const [movements, prods, cats] = await Promise.all([
          API.movements(depositId, { limite: 200 }),
          API.products(depositId, { limite: 200 }).catch(() => []),
          API.categories(depositId, { limite: 200 }).catch(() => []),
        ]);
        products = prods.map(p => ({ id: p.id, code: p.codigo || p.id.slice(0, 8), name: p.nome }));
        categories = cats;

        movementsData = movements.map(m => ({
          id: m.id,
          tipo: m.tipo || "—",
          produto: m.produto_id ? (prods.find(p => p.id === m.produto_id)?.nome || m.produto_id.slice(0, 8) + "…") : "—",
          quantidade: m.quantidade ?? "—",
          data: m.movimentado_em ? m.movimentado_em.slice(0, 10) : (m.criado_em ? m.criado_em.slice(0, 10) : "—"),
          observacao: m.observacao || "—",
        }));

        renderTable(movementsData);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar movimentações."]));
        notify(err.message || "Erro.", "error");
      }
    }

    loadMovements();
  });
}
