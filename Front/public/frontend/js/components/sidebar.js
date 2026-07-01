import { el, renderIcons } from "../utils/helpers.js";
import { router } from "../router.js";
import { session } from "../services/store.js";
import { openModal } from "./modal.js";
import { notify } from "./notifications.js";

const NAV = [
  { path: "/dashboard",   label: "Dashboard",           icon: "layout-dashboard" },
  { path: "/products",    label: "Estoque",              icon: "package" },
  { path: "/inventory",   label: "Entradas/Saídas",      icon: "arrow-left-right" },
  { path: "/picking",     label: "Picking",              icon: "hand" },
  { path: "/categories",  label: "Categorias & Locais",  icon: "layers" },
  { path: "/reports",     label: "Relatórios",           icon: "clipboard-list" },
  { path: "/school",      label: "Gestão Escolar",       icon: "graduation-cap" },
  { path: "/users",       label: "Usuários",             icon: "users", gestaoOnly: true },
  { path: "/settings",    label: "Configurações",        icon: "settings" },
];

const BOTTOM = [
  { path: "/exports",  label: "Exportações",  icon: "download" },
  { path: "/support",  label: "Suporte",      icon: "life-buoy" },
  { action: "logout",  label: "Log Out",      icon: "log-out" },
];

// Card com os dados do usuário logado (substitui o antigo texto explicando perfis).
function userInfoCard() {
  const u = session.user || {};
  const initials = (u.name || u.email || "?").trim().charAt(0).toUpperCase();
  const perfilLabel = u.profile === "gestao" ? "Gestão" : "Professor";

  const meta = [
    el("div", { class: "sidebar-user-name", text: u.name || "—" }),
    el("div", { class: "sidebar-user-email", text: u.email || "—" }),
    el("span", { class: "chip chip-info sidebar-user-chip", text: perfilLabel }),
  ];
  if (u.profile === "professor" && u.turmas?.length) {
    meta.push(el("div", { class: "sidebar-user-turmas", text: "Turmas: " + u.turmas.join(", ") }));
  }

  return el("div", { class: "sidebar-user" }, [
    el("div", { class: "avatar", text: initials }),
    el("div", { class: "sidebar-user-meta" }, meta),
  ]);
}

export function Sidebar(currentPath) {
  const perfilAtual = session.user?.profile;
  const navVisivel = NAV.filter(item => !item.gestaoOnly || perfilAtual === "gestao");

  const linkNode = (item) => {
    const isActive = currentPath?.startsWith(item.path);
    return el("a", {
      class: "nav-item" + (isActive ? " active" : ""),
      href: "#" + item.path,
    }, [el("i", { "data-lucide": item.icon }), el("span", { text: item.label })]);
  };

  const bottomNode = (item) => {
    if (item.action === "logout") {
      return el("a", {
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
    }
    return linkNode(item);
  };

  const aside = el("aside", { class: "sidebar" }, [
    el("div", { class: "brand" }, [el("img", { src: "assets/images/logo-dark.jpg", alt: "ANT Stock" })]),
    userInfoCard(),
    el("nav", {}, navVisivel.map(linkNode)),
    el("div", { class: "nav-bottom" }, BOTTOM.map(bottomNode)),
  ]);

  renderIcons(aside);
  return aside;
}
