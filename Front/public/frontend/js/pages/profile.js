import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { session } from "../services/store.js";
import { API, normalizeUser } from "../services/api.js";
import { notify } from "../components/notifications.js";
import { getInitials } from "../utils/helpers.js";
import { maskPhone, validateEmail, required } from "../utils/validators.js";
import { guardedClick } from "../utils/security.js";

export function ProfilePage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    // Start with session data, then refresh from API
    let user = session.user || { name: "Usuário ANT", email: "", role: "Professor" };

    const avatar = el("div", { class: "avatar avatar-lg", text: getInitials(user.name) });
    const nameDisplay = el("h3", { text: user.name });
    const emailDisplay = el("p", { text: user.email });
    const roleChip = el("span", { class: "chip chip-success", style: "margin-top:10px", text: user.role });

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [el("h1", { text: "Perfil" }), el("p", { class: "muted", text: "Gerencie suas informações pessoais." })]),
    ]);
    const side = el("div", { class: "card profile-side" }, [avatar, nameDisplay, emailDisplay, roleChip]);

    const phone = el("input", { class: "input", placeholder: "(11) 99999-9999" });
    phone.addEventListener("input", () => { phone.value = maskPhone(phone.value); });
    const nameInput = el("input", { class: "input", value: user.name });
    const emailInput = el("input", { class: "input", type: "email", value: user.email });
    const roleInput = el("input", { class: "input", value: user.role, disabled: true });
    const errs = { name: el("div", { class: "error-text" }), email: el("div", { class: "error-text" }) };

    const form = el("form", { class: "card card-pad" }, [
      el("h3", { text: "Informações pessoais", style: "margin-bottom:14px" }),
      el("div", { class: "form-grid" }, [
        el("div", { class: "field" }, [el("label", { text: "Nome" }), nameInput, errs.name]),
        el("div", { class: "field" }, [el("label", { text: "Email" }), emailInput, errs.email]),
        el("div", { class: "field" }, [el("label", { text: "Telefone" }), phone]),
        el("div", { class: "field" }, [el("label", { text: "Função" }), roleInput]),
      ]),
      el("div", { style: "display:flex;gap:10px;margin-top:18px;justify-content:flex-end" }, [
        el("button", { type: "reset", class: "btn btn-ghost", text: "Cancelar" }),
        el("button", { type: "submit", class: "btn btn-primary", text: "Salvar alterações" }),
      ]),
    ]);

    form.addEventListener("submit", guardedClick((e) => {
      e.preventDefault();
      const nE = required(nameInput.value, "Nome"); errs.name.textContent = nE || "";
      const eE = validateEmail(emailInput.value); errs.email.textContent = eE || "";
      if (nE || eE) return;
      // Update local session with new name/email
      session.signIn({ ...user, name: nameInput.value, email: emailInput.value });
      avatar.textContent = getInitials(nameInput.value);
      nameDisplay.textContent = nameInput.value;
      emailDisplay.textContent = emailInput.value;
      notify("Perfil atualizado localmente! Alterações de nome/email requerem endpoint de atualização no backend.", "info");
    }));

    content.append(head, el("div", { class: "profile-grid" }, [side, form]));
    renderIcons(content);

    // Refresh profile from API
    API.profile().then((freshUser) => {
      user = freshUser;
      nameInput.value = freshUser.name;
      emailInput.value = freshUser.email;
      roleInput.value = freshUser.role;
      nameDisplay.textContent = freshUser.name;
      emailDisplay.textContent = freshUser.email;
      roleChip.textContent = freshUser.role;
      avatar.textContent = getInitials(freshUser.name);
      // Keep session in sync
      session.signIn(freshUser, session.token);
    }).catch(() => {
      // Silently keep session data if API call fails
    });
  });
}
