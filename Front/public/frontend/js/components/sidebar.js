import { el, renderIcons } from "../utils/helpers.js";
import { router } from "../router.js";
import { session } from "../services/store.js";
import { openModal } from "./modal.js";
import { notify } from "./notifications.js";

const NAV = [
  { path: "/dashboard", label: "Dashboard", icon: "layout-dashboard" },
  { path: "/products", label: "Estoque", icon: "package" },
  { path: "/inventory", label: "Entradas/Saídas", icon: "arrow-left-right" },
  { path: "/picking", label: "Picking", icon: "hand" },
  { path: "/reports", label: "Relatórios Logísticos", icon: "clipboard-list" },
  { path: "/school", label: "Gestão Escolar", icon: "graduation-cap" },
  { path: "/users", label: "Usuários", icon: "users" },
  { path: "/settings", label: "Configurações", icon: "settings" },
];
const BOTTOM = [
  { path: "/support", label: "Support", icon: "life-buoy" },
  { action: "logout", label: "Log Out", icon: "log-out" },
];

export function Sidebar(currentPath) {
  const linkNode = (item) => {
    const isActive = currentPath?.startsWith(item.path);
    const a = el("a", {
      class: "nav-item" + (isActive ? " active" : ""),
      href: "#" + item.path,
    }, [el("i", { "data-lucide": item.icon }), el("span", { text: item.label })]);
    return a;
  };

  const bottomNode = (item) => {
    if (item.action === "logout") {
      const btn = el("a", {
        class: "nav-item",
        href: "javascript:void(0)",
        onclick: () => openModal({
          title: "Sair da conta?",
          body: "Você precisará entrar novamente para acessar o painel.",
          primaryLabel: "Sair",
          danger: true,
          onConfirm: () => {
            session.signOut();
            notify("Sessão encerrada.", "info");
            router.navigate("/login");
          },
        }),
      }, [el("i", { "data-lucide": item.icon }), el("span", { text: item.label })]);
      return btn;
    }
    return linkNode(item);
  };

  const aside = el("aside", { class: "sidebar" }, [
    el("div", { class: "brand" }, [
      el("img", { src: "assets/images/logo-dark.jpg", alt: "ANT Stock" }),
    ]),
    el("nav", {}, NAV.map(linkNode)),
    el("div", { class: "nav-bottom" }, BOTTOM.map(bottomNode)),
  ]);

  renderIcons(aside);
  return aside;
}