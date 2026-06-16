import { el, renderIcons, debounce } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { ProductCard } from "../components/cards.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick, sanitize } from "../utils/security.js";

export function ProductsPage(root, ctx) {
  let query = "";
  let category = "Todas";
  let products = [];
  let stockMap = {};
  let categoryMap = {};

  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Estoque" }),
        el("p", { class: "muted", text: "Gerencie produtos, categorias e saldos do estoque." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: () => notify("Cadastro de produto disponível via API.", "info") }, [el("i", { "data-lucide": "plus" }), "Adicionar"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(visibleRows(), "estoque.txt"); notify("Exportado TXT.", "success"); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(visibleRows(), "estoque.xlsx", "Estoque"); notify("Exportado Excel.", "success"); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const search = el("input", { class: "input", placeholder: "Buscar produtos por nome, código ou categoria...", style: "max-width: 420px" });
    const select = el("select", { class: "select", style: "max-width: 220px" }, [el("option", { value: "Todas", text: "Todas" })]);
    const filters = el("div", { class: "filters-row" }, [search, select]);
    const grid = el("div", { class: "product-grid stagger" });

    content.append(head, filters, grid);
    renderIcons(content);

    function visibleRows() {
      return products.filter((p) => {
        const q = sanitize(query).toLowerCase();
        const matchesQ = !q || [p.name, p.code, p.category].some((v) => (v || "").toLowerCase().includes(q));
        const matchesC = category === "Todas" || p.category === category;
        return matchesQ && matchesC;
      });
    }

    function rerender() {
      grid.innerHTML = "";
      const rows = visibleRows();
      if (rows.length === 0) {
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nenhum produto encontrado."]));
        return;
      }
      rows.forEach((product) => grid.appendChild(ProductCard(product)));
      renderIcons(grid);
    }

    function setCategories() {
      const cats = ["Todas", ...new Set(products.map((p) => p.category).filter(Boolean))];
      select.innerHTML = "";
      cats.forEach((item) => select.appendChild(el("option", { value: item, text: item })));
    }

    async function loadProducts() {
      grid.innerHTML = "";
      grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Carregando produtos..."]));
      try {
        let depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits || deposits.length === 0) {
            products = [];
            grid.innerHTML = "";
            grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nenhum depósito vinculado ao usuário."]));
            return;
          }
          depositId = deposits[0].id;
          session.setDepositId(depositId);
        }

        // Load products, stock and categories in parallel
        const [rows, stockRows, cats] = await Promise.all([
          API.products(depositId, { limite: 200 }),
          API.stock(depositId, { limite: 200 }).catch(() => []),
          API.categories(depositId, { limite: 200 }).catch(() => []),
        ]);

        // Build lookup maps
        categoryMap = {};
        for (const c of cats) categoryMap[c.id] = c.nome;

        stockMap = {};
        for (const s of stockRows) {
          stockMap[s.produto_id] = (stockMap[s.produto_id] || 0) + (s.quantidade || 0);
        }

        products = rows.map((item) => {
          const totalQty = stockMap[item.id] || 0;
          const catName = categoryMap[item.categoria_id] || (item.categoria_id ? "Categorizado" : "Sem categoria");
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
            status,
            updated: item.atualizado_em ? item.atualizado_em.slice(0, 10) : "",
          };
        });

        setCategories();
        rerender();
      } catch (err) {
        products = [];
        grid.innerHTML = "";
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Não foi possível carregar produtos da API."]));
        notify(err.message || "Erro ao carregar produtos.", "error");
      }
    }

    search.addEventListener("input", debounce((e) => { query = e.target.value; rerender(); }, 200));
    select.addEventListener("change", (e) => { category = e.target.value; rerender(); });
    loadProducts();
  });
}
