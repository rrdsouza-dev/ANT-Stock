import { el, renderIcons } from "../utils/helpers.js";
import { notify } from "./notifications.js";

export function ProductCard(p) {
  const statusClass = p.status === "Em estoque" ? "chip-success" : p.status === "Estoque baixo" ? "chip-warning" : "chip-danger";
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
        el("button", { class: "icon-btn", title: "Editar", onclick: () => notify(`Editando ${p.name}`, "info") }, [el("i", { "data-lucide": "pencil" })]),
        el("button", { class: "icon-btn", title: "Excluir", onclick: () => notify(`${p.name} removido (simulado)`, "warning") }, [el("i", { "data-lucide": "trash-2" })]),
      ]),
    ]),
  ]);
  renderIcons(card);
  return card;
}

export function StatCard({ label, value, trend, trendDir = "up", icon = "activity" }) {
  const node = el("div", { class: "stat-card" }, [
    el("div", { class: "icon-pill" }, [el("i", { "data-lucide": icon })]),
    el("div", { class: "label", text: label }),
    el("div", { class: "value", text: value }),
    trend ? el("div", { class: `trend ${trendDir}` }, [
      el("i", { "data-lucide": trendDir === "up" ? "trending-up" : "trending-down" }),
      el("span", { text: trend }),
    ]) : null,
  ]);
  renderIcons(node);
  return node;
}