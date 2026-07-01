/**
 * Usuários — lista somente leitura dos usuários reais cadastrados (gestão).
 * Novas contas são criadas pela própria pessoa na tela de Cadastro.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";

export function UsersPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Usuários" }),
        el("p", { class: "muted", text: "Contas cadastradas no sistema. Novas contas são criadas na tela de Cadastro." }),
      ]),
    ]);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando usuários…"]),
    ]);

    content.append(head, tableContainer);
    renderIcons(content);

    async function load() {
      try {
        const users = await API.users({ limite: 200 });
        tableContainer.innerHTML = "";
        if (!users.length) {
          tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum usuário cadastrado."]));
          return;
        }
        const table = DataTable({
          rows: users, pageSize: 10,
          columns: [
            { key: "name", label: "Nome" },
            { key: "email", label: "Email" },
            { key: "role", label: "Perfil", render: (r) =>
              el("span", { class: `chip ${r.profile === "gestao" ? "chip-warning" : "chip-success"}`, text: r.role })
            },
            { key: "turmas", label: "Turmas", render: (r) =>
              r.turmas?.length
                ? el("div", { style: "display:flex;flex-wrap:wrap;gap:4px" },
                    r.turmas.map(t => el("span", { class: "perm-badge", text: t })))
                : el("span", { class: "muted", text: "—" })
            },
            { key: "ativo", label: "Status", render: (r) =>
              el("span", { class: `chip ${r.ativo ? "chip-success" : "chip-danger"}`, text: r.ativo ? "Ativo" : "Inativo" })
            },
          ],
        });
        tableContainer.appendChild(table.node);
        renderIcons(tableContainer);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Acesso restrito à Gestão."]));
        notify(err.message || "Erro ao carregar usuários.", "error");
      }
    }

    load();
  });
}
