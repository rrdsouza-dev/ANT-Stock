/**
 * FASE 3 + FASE 4 — Entradas e Saídas com leitor de código de barras e CRUD.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { LocalDB } from "../services/localInventoryStore.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { BarcodeScanner } from "../components/barcodeScanner.js";
import { openMovementModal } from "../components/productModal.js";

export function InventoryPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let movementsData = [];
    let products = [];
    let depositId = null;

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Entradas e Saídas" }),
        el("p", { class: "muted", text: "Registre e acompanhe movimentações de estoque. Use leitor de código de barras ou busca manual." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: guardedClick(openMovModal) }, [
          el("i", { "data-lucide": "plus" }), "Registrar",
        ]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(movementsData, "movimentacoes.txt"); notify("TXT exportado.", "success"); }) },
          [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(movementsData, "movimentacoes.xlsx", "Movimentações"); notify("Excel exportado.", "success"); }) },
          [el("i", { "data-lucide": "sheet" }), "Excel"]),
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
        const product = await API.productByCode(depositId, code).catch(() => null);
        if (product) {
          LocalDB.logScan(code, true, product.nome);
          refreshHistory?.();
          notify(`Produto encontrado: ${product.nome}`, "success");
          openMovementModal({
            depositId,
            products,
            onSave: loadMovements,
            initialCode: code,
          });
        } else {
          // Try local match
          const localMatch = products.find(p =>
            p.code === code || p.name.toLowerCase().includes(code.toLowerCase())
          );
          if (localMatch) {
            LocalDB.logScan(code, true, localMatch.name);
            refreshHistory?.();
            notify(`Produto: ${localMatch.name}`, "success");
            openMovementModal({ depositId, products, onSave: loadMovements, initialCode: code });
          } else {
            LocalDB.logScan(code, false);
            refreshHistory?.();
            notify(`Código não encontrado: ${code}`, "warning");
          }
        }
      } catch (err) {
        notify(err.message || "Erro na leitura.", "error");
      }
    }

    function openMovModal() {
      if (!depositId) { notify("Aguarde — carregando…", "warning"); return; }
      openMovementModal({ depositId, products, onSave: loadMovements });
    }

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

        // Load movements AND products (for scanner lookup)
        const [movements, prods] = await Promise.all([
          API.movements(depositId, { limite: 200 }),
          API.products(depositId, { limite: 200 }).catch(() => []),
        ]);
        products = prods.map(p => ({ id: p.id, code: p.codigo || p.id.slice(0, 8), name: p.nome }));

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
