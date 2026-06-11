import { el, renderIcons, debounce } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { ProductCard } from "../components/cards.js";
import { API } from "../services/api.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick, sanitize } from "../utils/security.js";

export function ProductsPage(root, ctx) {
  let query = "";
  let category = "Todas";
  let products = [];

  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Estoque" }),
        el("p", { class: "muted", text: "Gerencie produtos, categorias e saldos do estoque." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: () => notify("Cadastro de produto deve ser feito pela API.", "info") }, [el("i", { "data-lucide": "plus" }), "Adicionar"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(visibleRows(), "estoque.txt"); notify("Exportado TXT.", "success"); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(visibleRows(), "estoque.xlsx", "Estoque"); notify("Exportado Excel.", "success"); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const search = el("input", { class: "input", placeholder: "Buscar produtos por nome, codigo ou categoria...", style: "max-width: 420px" });
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
      const categories = ["Todas", ...new Set(products.map((p) => p.category).filter(Boolean))];
      select.innerHTML = "";
      categories.forEach((item) => select.appendChild(el("option", { value: item, text: item })));
    }

    async function loadProducts() {
      grid.innerHTML = "";
      grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Carregando produtos..."]));
      try {
        const [deposit] = await API.deposits();
        if (!deposit) {
          products = [];
          grid.innerHTML = "";
          grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nenhum deposito vinculado ao usuario."]));
          return;
        }
        const rows = await API.products(deposit.id);
        products = rows.map((item) => ({
          code: item.codigo || item.id,
          name: item.nome,
          category: item.categoria_id ? "Categorizado" : "Sem categoria",
          quantity: item.quantidade_minima,
          status: item.ativo ? "Ativo" : "Inativo",
          updated: item.atualizado_em ? item.atualizado_em.slice(0, 10) : "",
        }));
        setCategories();
        rerender();
      } catch (err) {
        products = [];
        grid.innerHTML = "";
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center;grid-column:1/-1" }, ["Nao foi possivel carregar produtos da API."]));
        notify(err.message || "Erro ao carregar produtos.", "error");
      }
    }

    search.addEventListener("input", debounce((event) => { query = event.target.value; rerender(); }, 200));
    select.addEventListener("change", (event) => { category = event.target.value; rerender(); });
    loadProducts();
  });
}
