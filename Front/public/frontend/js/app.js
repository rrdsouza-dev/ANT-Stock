import { router } from "./router.js";
import { session } from "./services/store.js";
import { renderIcons } from "./utils/helpers.js";

import { LoginPage } from "./pages/login.js";
import { RegisterPage } from "./pages/register.js";
import { ForgotPasswordPage } from "./pages/forgot-password.js";
import { DashboardPage } from "./pages/dashboard.js";
import { ProductsPage } from "./pages/products.js";
import { InventoryPage } from "./pages/inventory.js";
import { PickingPage } from "./pages/picking.js";
import { ReportsPage } from "./pages/reports.js";
import { ProfilePage } from "./pages/profile.js";
import { SettingsPage } from "./pages/settings.js";
import { ExportsPage } from "./pages/exports.js";
import { CategoriesPage } from "./pages/categories.js";
import { SchoolPage } from "./pages/school.js";
import { UsersPage } from "./pages/users.js";
import { PlaceholderPage } from "./pages/placeholder.js";

// Public
router.register("/login", LoginPage, { public: true });
router.register("/register", RegisterPage, { public: true });
router.register("/forgot-password", ForgotPasswordPage, { public: true });

// Authenticated
router.register("/dashboard", DashboardPage);
router.register("/products", ProductsPage);
router.register("/inventory", InventoryPage);
router.register("/picking", PickingPage);
router.register("/reports", ReportsPage);
router.register("/categories", CategoriesPage);
router.register("/school", SchoolPage);
router.register("/users", UsersPage);
router.register("/settings", SettingsPage);
router.register("/profile", ProfilePage);
router.register("/exports", ExportsPage);
router.register("/support", PlaceholderPage("Suporte", "Fale com a equipe ANT Stock.", "life-buoy"));

router.setGuard((route, path) => {
  const isPublic = !!route?.public;
  const authed = session.isAuthenticated();
  if (!authed && !isPublic) return { redirect: "/login" };
  if (authed && isPublic) return { redirect: "/dashboard" };
  return null;
});

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

window.addEventListener("load", () => renderIcons());
