import { el, renderIcons } from "../utils/helpers.js";
import { router } from "../router.js";
import { API } from "../services/api.js";
import { notify } from "../components/notifications.js";
import { validateEmail, validatePassword } from "../utils/validators.js";
import { canRequest, guardedClick } from "../utils/security.js";

export function ForgotPasswordPage(root) {
  document.body.classList.add("app-bg");

  let step = 1;
  const state = { email: "", code: "" };

  const card = el("div", { class: "auth-card" });
  root.appendChild(el("div", { class: "auth-center" }, [card]));

  function render() {
    card.innerHTML = "";
    const steps = el("div", { class: "steps" }, [1, 2, 3].map((i) => el("div", { class: "step" + (i <= step ? " active" : "") })));
    card.append(
      el("div", { class: "brand" }, [el("img", { src: "assets/images/logo-light.jpg", alt: "ANT Stock" })]),
      steps,
      el("h2", { text: step === 1 ? "Recuperar senha" : step === 2 ? "Verifique seu e-mail" : "Nova senha" }),
      el("p", { class: "subtitle", text: step === 1 ? "Informe o e-mail da sua conta para enviarmos um código." : step === 2 ? `Enviamos um código para ${state.email}` : "Defina uma nova senha segura." }),
    );

    if (step === 1) renderStep1();
    else if (step === 2) renderStep2();
    else renderStep3();

    card.append(el("a", { class: "back-link", href: "#/login" }, [el("i", { "data-lucide": "arrow-left" }), " Voltar para o login"]));
    renderIcons(card);
  }

  function renderStep1() {
    const inp = el("input", { class: "input", type: "email", placeholder: "Email", value: state.email });
    const err = el("div", { class: "error-text" });
    const btn = el("button", { class: "btn btn-primary btn-lg btn-block", text: "Enviar código" });
    const form = el("form", { class: "auth-form" }, [el("div", { class: "field" }, [inp, err]), btn]);
    form.addEventListener("submit", guardedClick(async (e) => {
      e.preventDefault();
      const er = validateEmail(inp.value); err.textContent = er || "";
      if (er) return;
      const t = canRequest("forgot:" + inp.value, 30);
      if (!t.ok) { notify(`Aguarde ${t.wait}s para reenviar.`, "warning"); return; }
      await API.forgotPassword(inp.value);
      state.email = inp.value.trim();
      notify("Código enviado para seu e-mail.");
      step = 2; render();
    }));
    card.append(form);
  }

  function renderStep2() {
    const inputs = Array.from({ length: 6 }).map(() => el("input", { class: "code-cell", maxlength: "1", inputmode: "numeric" }));
    const wrap = el("div", { class: "code-inputs" }, inputs);
    inputs.forEach((inp, i) => {
      inp.addEventListener("input", () => {
        inp.value = inp.value.replace(/\D/g, "");
        if (inp.value && i < 5) inputs[i + 1].focus();
      });
      inp.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !inp.value && i > 0) inputs[i - 1].focus();
      });
    });
    const err = el("div", { class: "error-text" });
    const btn = el("button", { class: "btn btn-primary btn-lg btn-block", text: "Verificar código" });
    const resend = el("button", { type: "button", class: "btn btn-ghost btn-block", text: "Reenviar código" });
    resend.addEventListener("click", guardedClick(async () => {
      const t = canRequest("forgot:" + state.email, 30);
      if (!t.ok) { notify(`Aguarde ${t.wait}s.`, "warning"); return; }
      await API.forgotPassword(state.email);
      notify("Novo código enviado.");
    }));
    const form = el("form", { class: "auth-form" }, [wrap, err, btn, resend]);
    form.addEventListener("submit", guardedClick(async (e) => {
      e.preventDefault();
      const code = inputs.map((i) => i.value).join("");
      if (code.length !== 6) { err.textContent = "Informe os 6 dígitos."; return; }
      state.code = code;
      step = 3; render();
    }));
    card.append(form);
  }

  function renderStep3() {
    const p1 = el("input", { class: "input", type: "password", placeholder: "Nova senha" });
    const p2 = el("input", { class: "input", type: "password", placeholder: "Confirmar nova senha" });
    const err = el("div", { class: "error-text" });
    const btn = el("button", { class: "btn btn-primary btn-lg btn-block", text: "Salvar nova senha" });
    const form = el("form", { class: "auth-form" }, [
      el("div", { class: "field" }, [p1]),
      el("div", { class: "field" }, [p2, err]),
      btn,
    ]);
    form.addEventListener("submit", guardedClick(async (e) => {
      e.preventDefault();
      const v = validatePassword(p1.value); if (v) { err.textContent = v; return; }
      if (p1.value !== p2.value) { err.textContent = "Senhas não conferem."; return; }
      await API.resetPassword(state.email, state.code, p1.value);
      notify("Senha alterada com sucesso!");
      router.navigate("/login");
    }));
    card.append(form);
  }

  render();
}