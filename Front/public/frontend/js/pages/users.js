/**
 * FASE 5 + FASE 6 — Gerenciamento de usuários com perfis e controle de acesso simulado.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { LocalDB } from "../services/localInventoryStore.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { openModal } from "../components/modal.js";
import { guardedClick } from "../utils/security.js";

const ROLES = [
  { value: "administrador", label: "Administrador", color: "chip-danger",
    permissions: ["create", "read", "update", "delete", "manage_users"],
    description: "Acesso total ao sistema incluindo gestão de usuários." },
  { value: "gestor", label: "Gestor", color: "chip-warning",
    permissions: ["create", "read", "update", "delete"],
    description: "Pode criar, editar e excluir registros, mas não gerencia usuários." },
  { value: "professor", label: "Professor", color: "chip-success",
    permissions: ["create", "read", "update"],
    description: "Pode criar e editar registros, mas não pode excluir." },
  { value: "operador", label: "Operador", color: "",
    permissions: ["read", "update"],
    description: "Pode apenas visualizar e atualizar registros existentes." },
];

const PERM_LABELS = {
  create: "Criar", read: "Visualizar", update: "Editar",
  delete: "Excluir", manage_users: "Gerenciar usuários",
};

export function UsersPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    LocalDB.seedUsersIfEmpty();

    const currentUser = session.user;
    const simulatedRole = LocalDB.getSetting("simulated_role", currentUser?.profile || "professor");
    const isAdmin = simulatedRole === "administrador" || simulatedRole === "gestor";

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Usuários" }),
        el("p", { class: "muted", text: "Perfis e permissões do sistema. Dados simulados até integração com backend." }),
      ]),
      isAdmin ? el("button", { class: "btn btn-soft", onclick: guardedClick(() => openUserModal(null)) }, [
        el("i", { "data-lucide": "user-plus" }), "Novo usuário",
      ]) : el("span"),
    ]);

    // Role legend
    const legend = el("div", { class: "card card-pad", style: "margin-bottom:18px" }, [
      el("h3", { text: "Perfis de Acesso", style: "margin-bottom:14px" }),
      el("div", { class: "roles-grid" }, ROLES.map(r =>
        el("div", { class: "role-card" + (r.value === simulatedRole ? " active-role" : "") }, [
          el("div", { class: "role-header" }, [
            el("span", { class: `chip ${r.color}`, text: r.label }),
            r.value === simulatedRole ? el("span", { class: "chip", style: "margin-left:6px", text: "Ativo" }) : el("span"),
          ]),
          el("p", { class: "muted", style: "font-size:0.82em;margin:6px 0" }, [r.description]),
          el("div", { class: "perm-list" }, r.permissions.map(p =>
            el("span", { class: "perm-badge", text: PERM_LABELS[p] || p })
          )),
        ])
      )),
    ]);

    const tableContainer = el("div");
    content.append(head, legend, tableContainer);
    renderIcons(content);

    function load() {
      tableContainer.innerHTML = "";
      const users = LocalDB.userProfiles.list();
      if (!users.length) {
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum usuário cadastrado."]));
        return;
      }
      const rows = users.map(u => ({ ...u }));
      const table = DataTable({
        rows, pageSize: 8,
        columns: [
          { key: "name", label: "Nome" },
          { key: "email", label: "Email" },
          { key: "role", label: "Perfil", render: (r) => {
            const roleInfo = ROLES.find(ro => ro.value === r.role);
            return el("span", { class: `chip ${roleInfo?.color || ""}`, text: roleInfo?.label || r.role });
          }},
          { key: "permissions", label: "Permissões", render: (r) =>
            el("div", { style: "display:flex;flex-wrap:wrap;gap:4px" },
              (r.permissions || []).map(p => el("span", { class: "perm-badge", text: PERM_LABELS[p] || p }))
            )
          },
          ...(isAdmin ? [{
            key: "acoes", label: "Ações", render: (r) =>
              el("div", { class: "pc-actions" }, [
                el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openUserModal(r)) }, [el("i", { "data-lucide": "pencil" })]),
                el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => deleteUser(r)) }, [el("i", { "data-lucide": "trash-2" })]),
              ])
          }] : []),
        ],
      });
      tableContainer.appendChild(table.node);
      renderIcons(tableContainer);
    }

    function openUserModal(user) {
      const isEdit = !!user;
      const nameEl = el("input", { class: "input", value: user?.name || "", placeholder: "Nome completo" });
      const emailEl = el("input", { class: "input", type: "email", value: user?.email || "", placeholder: "Email" });
      const roleEl = el("select", { class: "select" }, ROLES.map(r => {
        const opt = el("option", { value: r.value, text: r.label });
        if (user?.role === r.value) opt.selected = true;
        return opt;
      }));

      // Dynamic permission preview
      const permPreview = el("div", { class: "perm-list", style: "margin-top:8px" });
      function updatePerms() {
        const r = ROLES.find(ro => ro.value === roleEl.value);
        permPreview.innerHTML = "";
        (r?.permissions || []).forEach(p => permPreview.appendChild(el("span", { class: "perm-badge", text: PERM_LABELS[p] || p })));
      }
      roleEl.addEventListener("change", updatePerms);
      updatePerms();

      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? "Salvar" : "Criar"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? "Editar usuário" : "Novo usuário" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Nome *" }), nameEl]),
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Email *" }), emailEl]),
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Perfil" }), roleEl, permPreview]),
          errEl,
        ]),
        el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
      ]);

      const backdrop = el("div", { class: "modal-backdrop" }, [card]);
      const close = () => backdrop.remove();
      backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
      cancelBtn.addEventListener("click", close);

      saveBtn.addEventListener("click", () => {
        const name = nameEl.value.trim();
        const email = emailEl.value.trim();
        if (!name || !email) { errEl.textContent = "Nome e e-mail são obrigatórios."; return; }
        const role = roleEl.value;
        const permissions = ROLES.find(r => r.value === role)?.permissions || [];
        const data = { name, email, role, permissions };
        if (isEdit) LocalDB.userProfiles.update(user.id, data);
        else LocalDB.userProfiles.create(data);
        notify(isEdit ? "Usuário atualizado!" : "Usuário criado!", "success");
        close(); load();
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
      setTimeout(() => nameEl.focus(), 80);
    }

    function deleteUser(user) {
      openModal({
        title: "Excluir usuário",
        body: `Remover "${user.name}"?`,
        primaryLabel: "Excluir", danger: true,
        onConfirm: () => { LocalDB.userProfiles.delete(user.id); notify("Removido.", "warning"); load(); },
      });
    }

    load();
  });
}
