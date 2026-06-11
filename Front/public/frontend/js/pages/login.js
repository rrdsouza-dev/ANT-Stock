import { el, renderIcons } from "../utils/helpers.js";
import { router } from "../router.js";
import { session } from "../services/store.js";
import { API } from "../services/api.js";
import { notify } from "../components/notifications.js";
import { validateEmail, validatePassword } from "../utils/validators.js";
import { loginAttempt, clearLoginAttempts, guardedClick } from "../utils/security.js";

export function LoginPage(root) {
  document.body.classList.remove("app-bg");
  document.body.classList.add("app-bg");

  const form = el("form", { class: "auth-form", novalidate: true });
  const emailErr = el("div", { class: "error-text" });
  const passErr = el("div", { class: "error-text" });

  const emailWrap = el("div", { class: "input-wrap" }, [
    el("i", { class: "ico", "data-lucide": "mail" }),
    el("input", { type: "email", class: "input has-icon", name: "email", placeholder: "Email", autocomplete: "email" }),
  ]);
  const passInput = el("input", { type: "password", class: "input has-icon", name: "password", placeholder: "Senha", autocomplete: "current-password" });
  const toggleBtn = el("button", { type: "button", class: "toggle", title: "Mostrar/ocultar senha" }, [el("i", { "data-lucide": "eye-off" })]);
  toggleBtn.addEventListener("click", () => {
    const isPwd = passInput.type === "password";
    passInput.type = isPwd ? "text" : "password";
    toggleBtn.innerHTML = "";
    toggleBtn.appendChild(el("i", { "data-lucide": isPwd ? "eye" : "eye-off" }));
    renderIcons(toggleBtn);
  });
  const passWrap = el("div", { class: "input-wrap" }, [
    el("i", { class: "ico", "data-lucide": "lock" }), passInput, toggleBtn,
  ]);

  const submit = el("button", { type: "submit", class: "btn btn-primary btn-lg btn-block" }, ["Entrar"]);

  form.append(
    el("div", { class: "field" }, [emailWrap, emailErr]),
    el("div", { class: "field" }, [passWrap, passErr]),
    el("div", { class: "forgot" }, [el("a", { href: "#/forgot-password", text: "Esqueceu a senha?" })]),
    submit,
    el("div", { class: "alt-link" }, [el("a", { href: "#/register", text: "Cadastre-se" })]),
  );

  form.addEventListener("submit", guardedClick(async (e) => {
    e.preventDefault();
    const email = form.email.value.trim();
    const password = form.password.value;
    const eErr = validateEmail(email); emailErr.textContent = eErr || "";
    const pErr = validatePassword(password); passErr.textContent = pErr || "";
    if (eErr || pErr) return;
    const gate = loginAttempt();
    if (!gate.ok) { notify(`Muitas tentativas. Aguarde ${gate.lockSec}s.`, "error"); return; }
    submit.innerHTML = ""; submit.appendChild(el("span", { class: "spinner" }));
    try {
      const { user, token } = await API.login(email, password);
      clearLoginAttempts();
      session.signIn(user, token);
      notify(`Bem-vindo, ${user.name}!`);
      router.navigate("/dashboard");
    } catch (err) {
      notify("Não foi possível entrar.", "error");
      submit.textContent = "Entrar";
    }
  }));

  const left = el("div", { class: "auth-left" }, [
    el("div", { class: "brand" }, [el("img", { src: "assets/images/logo-light.jpg", alt: "ANT Stock" })]),
    el("h1", { text: "Bem-vindo de volta!" }),
    el("p", { class: "subtitle", text: "Simplifique sua gestão de estoque e impulsione a produtividade operacional com o ANT Stock. Comece grátis." }),
    form,
    el("div", { class: "auth-footer" }, [
      "Não é membro? ", el("a", { href: "#/register", text: "Cadastre-se agora" }),
    ]),
  ]);

  const right = el("div", { class: "auth-right" }, [
    el("img", { src: "assets/images/illustration.jpg", class: "illu", alt: "Ilustração ANT Stock" }),
    el("div", { class: "tag", html: "Torne seu trabalho mais fácil e organizado com o <b>ANT Stock</b>" }),
  ]);

  const wrap = el("div", { class: "auth-wrap anim-fade" }, [left, right]);
  root.appendChild(wrap);
  renderIcons(root);
}
