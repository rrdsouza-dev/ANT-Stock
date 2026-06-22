import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { notify } from "../components/notifications.js";
import { LocalDB } from "../services/localInventoryStore.js";

const SIMULATED_ROLES = [
  { value: "administrador", label: "Administrador" },
  { value: "gestor", label: "Gestor" },
  { value: "professor", label: "Professor" },
  { value: "operador", label: "Operador" },
];

export function SettingsPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [el("div", {}, [el("h1", { text: "Configurações" }), el("p", { class: "muted", text: "Preferências do sistema e segurança." })])]);

    const tabs = ["Geral", "Perfil Simulado", "Notificações", "Segurança"];
    let active = "Geral";
    const tabsRow = el("div", { class: "tabs" });
    const body = el("div");
    function renderTabs() {
      tabsRow.innerHTML = "";
      tabs.forEach((t) => {
        const b = el("button", { class: "tab" + (active === t ? " active" : ""), text: t });
        b.addEventListener("click", () => { active = t; renderTabs(); renderBody(); });
        tabsRow.appendChild(b);
      });
    }
    function row(title, desc, control) {
      return el("div", { class: "setting-row" }, [
        el("div", {}, [el("h4", { text: title }), el("p", { text: desc })]),
        control,
      ]);
    }
    function makeSwitch(initial, onChange) {
      const sw = el("div", { class: "switch" + (initial ? " on" : "") });
      sw.addEventListener("click", () => {
        sw.classList.toggle("on");
        onChange?.(sw.classList.contains("on"));
      });
      return sw;
    }
    function renderBody() {
      body.innerHTML = "";
      const card = el("div", { class: "card card-pad" });
      if (active === "Geral") {
        card.append(
          row("Idioma", "Português (Brasil)", el("select", { class: "select", style: "max-width:200px" }, [el("option", { text: "Português (Brasil)" }), el("option", { text: "English" })])),
          row("Tema escuro", "Em breve.", makeSwitch(false, () => notify("Tema será sincronizado em breve.", "info"))),
        );
      } else if (active === "Perfil Simulado") {
        const current = LocalDB.getSetting("simulated_role", "professor");
        const select = el("select", { class: "select", style: "max-width:240px" }, SIMULATED_ROLES.map(r => {
          const opt = el("option", { value: r.value, text: r.label });
          if (r.value === current) opt.selected = true;
          return opt;
        }));
        select.addEventListener("change", () => {
          LocalDB.setSetting("simulated_role", select.value);
          notify(`Visualização simulada como "${SIMULATED_ROLES.find(r => r.value === select.value)?.label}".`, "info");
        });
        card.append(
          el("p", { class: "muted", style: "margin-bottom:14px;font-size:0.85em" }, [
            "Esta opção altera apenas a visualização de permissões na tela de Usuários, para fins de demonstração. ",
            "O backend ainda não impõe controle de acesso real por perfil.",
          ]),
          row("Perfil ativo (simulado)", "Usado para pré-visualizar permissões na interface.", select),
        );
      } else if (active === "Notificações") {
        card.append(
          row("Alertas por e-mail", "Receba alertas sobre estoque baixo.", makeSwitch(true)),
          row("Push", "Notificações no navegador.", makeSwitch(false)),
          row("Relatórios semanais", "Resumo todas as segundas.", makeSwitch(true)),
        );
      } else {
        card.append(
          row("Autenticação 2 fatores", "Camada extra de proteção.", makeSwitch(false, () => notify("2FA será habilitado após integração.", "info"))),
          row("Sessões ativas", "Desconectar todos os dispositivos.", el("button", { class: "btn btn-outline", text: "Encerrar sessões", onclick: () => notify("Sessões encerradas (simulado).") })),
        );
      }
      body.appendChild(card);
    }
    renderTabs(); renderBody();
    content.append(head, tabsRow, body);
    renderIcons(content);
  });
}