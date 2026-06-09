import { router } from "./router.js";
import { session } from "./services/store.js";
import { renderIcons } from "./utils/helpers.js";

import { LoginPage } from "./pages/login.js";
import { RegisterPage } from "./pages/register.js";
import { ForgotPasswordPage } from "./pages/forgot-password.js";
import { DashboardPage } from "./pages/dashboard.js";
import { ProductsPage } from "./pages/products.js";
import { ReportsPage } from "./pages/reports.js";
import { ProfilePage } from "./pages/profile.js";
import { SettingsPage } from "./pages/settings.js";
import { ExportsPage } from "./pages/exports.js";
import { PlaceholderPage } from "./pages/placeholder.js";

// Public routes
router.register("/login", LoginPage, { public: true });
router.register("/register", RegisterPage, { public: true });
router.register("/forgot-password", ForgotPasswordPage, { public: true });

// Authenticated routes
router.register("/dashboard", DashboardPage);
router.register("/products", ProductsPage);
router.register("/inventory", PlaceholderPage("Entradas e Saídas", "Controle de movimentações de estoque.", "arrow-left-right"));
router.register("/picking", PlaceholderPage("Picking", "Listas de separação e progresso da equipe.", "hand"));
router.register("/reports", ReportsPage);
router.register("/school", PlaceholderPage("Gestão Escolar", "Acompanhamento das turmas e atividades.", "graduation-cap"));
router.register("/users", PlaceholderPage("Usuários", "Gerenciamento de usuários e permissões.", "users"));
router.register("/settings", SettingsPage);
router.register("/profile", ProfilePage);
router.register("/exports", ExportsPage);
router.register("/support", PlaceholderPage("Suporte", "Fale com a equipe ANT Stock.", "life-buoy"));

// Guard: require auth for everything except public routes
router.setGuard((route, path) => {
  const isPublic = !!route?.public;
  const authed = session.isAuthenticated();
  if (!authed && !isPublic) return { redirect: "/login" };
  if (authed && isPublic) return { redirect: "/dashboard" };
  return null;
});

// Boot
function boot() {
  if (!location.hash) {
    location.hash = session.isAuthenticated() ? "/dashboard" : "/login";
  } else {
    router.resolve();
  }
  renderIcons();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

// Render icons after dynamic imports of lucide CDN finish loading
window.addEventListener("load", () => renderIcons());