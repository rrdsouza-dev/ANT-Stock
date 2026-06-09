import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { ProductCard } from "../components/cards.js";
import { demoData } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick, sanitize } from "../utils/security.js";
import { debounce } from "../utils/helpers.js";

export function ProductsPage(root, ctx) {
  let query = "";
  let category = "Todas";
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Estoque" }),
        el("p", { class: "muted", text: "Gerencie todos os produtos da turma de logística." }),
      ]),
      el("div", { class: "exports" }, [
        el("button", { class: "btn btn-soft", onclick: () => notify("Novo produto (simulado).", "info") }, [el("i", { "data-lucide": "plus" }), "Adicionar"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportTxt(visibleRows(), "estoque.txt"); notify("Exportado TXT.", "success"); }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
        el("button", { class: "btn btn-primary", onclick: guardedClick(() => { exportExcel(visibleRows(), "estoque.xlsx", "Estoque"); notify("Exportado Excel.", "success"); }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
      ]),
    ]);

    const search = el("input", { class: "input", placeholder: "Buscar produtos por nome, código ou categoria...", style: "max-width: 420px" });
    const cats = ["Todas", "Eletrônicos", "Material Didático", "Móveis", "Logística", "Limpeza"];
    const select = el("select", { class: "select", style: "max-width: 220px" }, cats.map((c) => el("option", { value: c, text: c })));
    const filters = el("div", { class: "filters-row" }, [search, select]);

    const grid = el("div", { class: "product-grid stagger" });
    content.append(head, filters, grid);
    renderIcons(content);

    function visibleRows() {
      return demoData.products.filter((p) => {
        const q = sanitize(query).toLowerCase();
        const matchesQ = !q || [p.name, p.code, p.category].some((v) => v.toLowerCase().includes(q));
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
      for (const p of rows) grid.appendChild(ProductCard(p));
    }
    search.addEventListener("input", debounce((e) => { query = e.target.value; rerender(); }, 200));
    select.addEventListener("change", (e) => { category = e.target.value; rerender(); });
    rerender();
  });
}