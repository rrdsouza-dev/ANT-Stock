import { el, renderIcons } from "../utils/helpers.js";
import { router } from "../router.js";
import { session } from "../services/store.js";
import { API } from "../services/api.js";
import { notify } from "../components/notifications.js";
import { validateEmail, validatePassword, passwordScore, required } from "../utils/validators.js";
import { guardedClick } from "../utils/security.js";

export function RegisterPage(root) {
  document.body.classList.add("app-bg");

  const form = el("form", { class: "auth-form", novalidate: true });
  const errs = { name: el("div", { class: "error-text" }), email: el("div", { class: "error-text" }), pass: el("div", { class: "error-text" }), conf: el("div", { class: "error-text" }) };
  const strength = el("div", { class: "strength" }, [el("span"), el("span"), el("span"), el("span")]);

  const name = el("input", { class: "input", name: "name", placeholder: "Nome completo" });
  const email = el("input", { class: "input", type: "email", name: "email", placeholder: "Email" });
  const pass = el("input", { class: "input", type: "password", name: "password", placeholder: "Senha (mín. 8 caracteres)" });
  const conf = el("input", { class: "input", type: "password", name: "confirm", placeholder: "Confirmar senha" });

  pass.addEventListener("input", () => {
    const s = passwordScore(pass.value);
    strength.className = "strength s" + s;
  });

  const submit = el("button", { class: "btn btn-primary btn-lg btn-block", text: "Criar conta" });

  form.append(
    el("div", { class: "field" }, [name, errs.name]),
    el("div", { class: "field" }, [email, errs.email]),
    el("div", { class: "field" }, [pass, strength, errs.pass]),
    el("div", { class: "field" }, [conf, errs.conf]),
    submit,
  );

  form.addEventListener("submit", guardedClick(async (e) => {
    e.preventDefault();
    const nErr = required(name.value, "Nome"); errs.name.textContent = nErr || "";
    const eErr = validateEmail(email.value); errs.email.textContent = eErr || "";
    const pErr = validatePassword(pass.value); errs.pass.textContent = pErr || "";
    const cErr = pass.value !== conf.value ? "As senhas não conferem." : null;
    errs.conf.textContent = cErr || "";
    if (nErr || eErr || pErr || cErr) return;
    submit.innerHTML = ""; submit.appendChild(el("span", { class: "spinner" }));
    try {
      const { user, token } = await API.register({
        name: name.value.trim(),
        email: email.value.trim(),
        password: pass.value,
        profile: "professor",
      });
      session.signIn(user, token);
      notify("Conta criada com sucesso!");
      router.navigate("/dashboard");
    } catch {
      notify("Não foi possível criar a conta.", "error");
      submit.textContent = "Criar conta";
    }
  }));

  const card = el("div", { class: "auth-card" }, [
    el("div", { class: "brand" }, [el("img", { src: "assets/images/logo-light.jpg", alt: "ANT Stock" })]),
    el("h2", { text: "Crie sua conta" }),
    el("p", { class: "subtitle", text: "Comece a organizar seu estoque em segundos." }),
    form,
    el("a", { class: "back-link", href: "#/login" }, [el("i", { "data-lucide": "arrow-left" }), " Voltar para o login"]),
  ]);

  root.appendChild(el("div", { class: "auth-center" }, [card]));
  renderIcons(root);
}
