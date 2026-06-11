import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { session } from "../services/store.js";
import { notify } from "../components/notifications.js";
import { getInitials } from "../utils/helpers.js";
import { maskPhone, validateEmail, required } from "../utils/validators.js";
import { guardedClick } from "../utils/security.js";

export function ProfilePage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const user = session.user || { name: "Professor ANT", email: "professor@antstock.com", role: "Professor" };
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [el("h1", { text: "Perfil" }), el("p", { class: "muted", text: "Gerencie suas informações pessoais." })]),
    ]);
    const side = el("div", { class: "card profile-side" }, [
      el("div", { class: "avatar avatar-lg", text: getInitials(user.name) }),
      el("h3", { text: user.name }),
      el("p", { text: user.email }),
      el("span", { class: "chip chip-success", style: "margin-top:10px", text: user.role }),
    ]);
    const phone = el("input", { class: "input", placeholder: "(11) 99999-9999" });
    phone.addEventListener("input", () => { phone.value = maskPhone(phone.value); });
    const name = el("input", { class: "input", value: user.name });
    const email = el("input", { class: "input", type: "email", value: user.email });
    const role = el("input", { class: "input", value: user.role, disabled: true });
    const errs = { name: el("div", { class: "error-text" }), email: el("div", { class: "error-text" }) };

    const form = el("form", { class: "card card-pad" }, [
      el("h3", { text: "Informações pessoais", style: "margin-bottom:14px" }),
      el("div", { class: "form-grid" }, [
        el("div", { class: "field" }, [el("label", { text: "Nome" }), name, errs.name]),
        el("div", { class: "field" }, [el("label", { text: "Email" }), email, errs.email]),
        el("div", { class: "field" }, [el("label", { text: "Telefone" }), phone]),
        el("div", { class: "field" }, [el("label", { text: "Função" }), role]),
      ]),
      el("div", { style: "display:flex;gap:10px;margin-top:18px;justify-content:flex-end" }, [
        el("button", { type: "reset", class: "btn btn-ghost", text: "Cancelar" }),
        el("button", { type: "submit", class: "btn btn-primary", text: "Salvar alterações" }),
      ]),
    ]);
    form.addEventListener("submit", guardedClick((e) => {
      e.preventDefault();
      const nE = required(name.value, "Nome"); errs.name.textContent = nE || "";
      const eE = validateEmail(email.value); errs.email.textContent = eE || "";
      if (nE || eE) return;
      session.signIn({ ...user, name: name.value, email: email.value });
      notify("Perfil atualizado!");
    }));

    content.append(head, el("div", { class: "profile-grid" }, [side, form]));
    renderIcons(content);
  });
}
