/**
 * FASE 1 + FASE 4 — Página de Estoque com CRUD completo e campos logísticos detalhados.
 */
import { el, renderIcons, debounce } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { notify } from "../components/notifications.js";
import { guardedClick, sanitize } from "../utils/security.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { openProductModal, openMovementModal } from "../components/productModal.js";
import { openModal } from "../components/modal.js";

export function ProductsPage(root, ctx) {
  let query = "";
  let category = "Todas";
  let products = [];
  let stockMap = {};
  let categoryMap = {};
  let depositId = null;
  let allCategories = [];
  let allLocations = [];

  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Estoque" }),
        el("p", { class: "muted", text: "Gerencie produtos, categorias e saldos do estoque." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: guardedClick(openCreate) }, [
          el("i", { "data-lucide": "plus" }), "Adicionar produto",
        ]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportTxt(visibleRows(), "estoque.txt"); notify("Exportado TXT.", "success");
        }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
          exportExcel(visibleRows(), "estoque.xlsx", "Estoque"); notify("Exportado Excel.", "success");
        }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const search = el("input", { class: "input", placeholder: "Buscar por nome, código ou categoria…", style: "max-width:420px" });
    const select = el("select", { class: "select", style: "max-width:220px" }, [el("option", { value: "Todas", text: "Todas" })]);
    const filters = el("div", { class: "filters-row" }, [search, select]);
    const grid = el("div", { class: "product-grid stagger" });

    content.append(head, filters, grid);
    renderIcons(content);

    function visibleRows() {
      return products.filter((p) => {
        const q = sanitize(query).toLowerCase();
        const matchQ = !q || [p.name, p.code, p.category].some((v) => (v || "").toLowerCase().includes(q));
        const matchC = category === "Todas" || p.category === category;
        return matchQ && matchC;
      });
    }

    function rerender() {
      grid.innerHTML = "";
      const rows = visibleRows();
      if (!rows.length) {
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nenhum produto encontrado."]));
        return;
      }
      rows.forEach((p) => grid.appendChild(buildCard(p)));
      renderIcons(grid);
    }

    function buildCard(p) {
      const statusClass = p.status === "Em estoque" ? "chip-success"
        : p.status === "Estoque baixo" ? "chip-warning" : "chip-danger";

      const card = el("article", { class: "product-card" }, [
        el("div", { class: "pc-head" }, [
          el("div", {}, [
            el("div", { class: "pc-code", text: p.code }),
            el("div", { class: "pc-name", text: p.name }),
            el("div", { class: "pc-cat", text: p.category }),
          ]),
          el("span", { class: `chip ${statusClass}`, text: p.status }),
        ]),
        el("div", { class: "pc-row" }, [
          el("div", { class: "pc-qty", html: `${p.quantity}<span>un</span>` }),
          el("div", { class: "pc-actions" }, [
            el("button", { class: "icon-btn", title: "Movimentar", onclick: guardedClick(() => openMov(p)) },
              [el("i", { "data-lucide": "arrow-left-right" })]),
            el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openEdit(p)) },
              [el("i", { "data-lucide": "pencil" })]),
            el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => confirmDelete(p)) },
              [el("i", { "data-lucide": "trash-2" })]),
          ]),
        ]),
      ]);
      renderIcons(card);
      return card;
    }

    function setCategories() {
      const cats = ["Todas", ...new Set(products.map((p) => p.category).filter(Boolean))];
      select.innerHTML = "";
      cats.forEach((c) => select.appendChild(el("option", { value: c, text: c })));
    }

    function openCreate() {
      openProductModal({
        depositId,
        categories: allCategories,
        locations: allLocations,
        onSave: loadProducts,
      });
    }

    function openEdit(p) {
      const raw = {
        id: p.id,
        nome: p.name,
        codigo: p.code !== p.id.slice(0, 8) ? p.code : undefined,
        quantidade_minima: p.minQuantity,
        categoria_id: allCategories.find(c => c.nome === p.category)?.id,
        unidade_medida: p.unidade_medida,
        quantidade_por_caixa: p.quantidade_por_caixa,
        lote: p.lote,
        validade: p.validade,
        observacoes: p.observacoes,
        localizacao_id: p.localizacao_id,
      };
      openProductModal({
        depositId,
        product: raw,
        categories: allCategories,
        locations: allLocations,
        onSave: loadProducts,
      });
    }

    function openMov(p) {
      openMovementModal({ depositId, products, categories: allCategories, locations: allLocations, onSave: loadProducts });
    }

    function confirmDelete(p) {
      openModal({
        title: "Excluir produto",
        body: `Deseja remover "${p.name}" do sistema? Esta ação é irreversível.`,
        primaryLabel: "Excluir",
        danger: true,
        onConfirm: async () => {
          await API.deleteProduct(depositId, p.id);
          notify("Produto removido.", "warning");
          loadProducts();
        },
      });
    }

    async function loadProducts() {
      grid.innerHTML = "";
      grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Carregando produtos…"]));
      try {
        depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits?.length) {
            grid.innerHTML = "";
            grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nenhum depósito vinculado."]));
            return;
          }
          depositId = deposits[0].id;
          session.setDepositId(depositId);
        }

        const [rows, stockRows, cats, locs] = await Promise.all([
          API.products(depositId, { limite: 200 }),
          API.stock(depositId, { limite: 200 }).catch(() => []),
          API.categories(depositId, { limite: 200 }).catch(() => []),
          API.locations(depositId, { limite: 200 }).catch(() => []),
        ]);

        allCategories = cats;
        allLocations = locs;

        categoryMap = {};
        for (const c of cats) categoryMap[c.id] = c.nome;

        stockMap = {};
        for (const s of stockRows) {
          stockMap[s.produto_id] = (stockMap[s.produto_id] || 0) + (s.quantidade || 0);
        }

        products = rows.map((item) => {
          const totalQty = stockMap[item.id] || 0;
          const catName = categoryMap[item.categoria_id] || "Sem categoria";
          let status;
          if (!item.ativo) status = "Inativo";
          else if (totalQty === 0) status = "Esgotado";
          else if (totalQty <= item.quantidade_minima) status = "Estoque baixo";
          else status = "Em estoque";

          return {
            id: item.id,
            code: item.codigo || item.id.slice(0, 8),
            name: item.nome,
            category: catName,
            quantity: totalQty,
            minQuantity: item.quantidade_minima,
            unidade_medida: item.unidade_medida,
            quantidade_por_caixa: item.quantidade_por_caixa,
            lote: item.lote,
            validade: item.validade,
            observacoes: item.observacoes,
            localizacao_id: item.localizacao_id,
            status,
            updated: item.atualizado_em ? item.atualizado_em.slice(0, 10) : "",
          };
        });

        setCategories();
        rerender();
      } catch (err) {
        grid.innerHTML = "";
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Erro ao carregar produtos da API."]));
        notify(err.message || "Erro ao carregar produtos.", "error");
      }
    }

    search.addEventListener("input", debounce((e) => { query = e.target.value; rerender(); }, 200));
    select.addEventListener("change", (e) => { category = e.target.value; rerender(); });
    loadProducts();
  });
}
