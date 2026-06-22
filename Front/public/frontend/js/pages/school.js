/**
 * FASE 5 — Gestão Escolar com localStorage temporário.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { LocalDB } from "../services/localInventoryStore.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { openModal } from "../components/modal.js";
import { guardedClick } from "../utils/security.js";

export function SchoolPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    LocalDB.seedSchoolIfEmpty();

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Gestão Escolar" }),
        el("p", { class: "muted", text: "Acompanhe depósitos, salas e espaços da escola. Dados locais até integração com Supabase." }),
      ]),
      el("button", { class: "btn btn-soft", onclick: guardedClick(() => openItemModal(null)) }, [
        el("i", { "data-lucide": "plus" }), "Novo item",
      ]),
    ]);

    const tableContainer = el("div");
    content.append(head, tableContainer);
    renderIcons(content);

    function load() {
      tableContainer.innerHTML = "";
      const items = LocalDB.schoolData.list();
      if (!items.length) {
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum item cadastrado."]));
        return;
      }
      const rows = items.map(i => ({ ...i, data_fmt: i.data?.slice(0, 10) || "—" }));
      const table = DataTable({
        rows, pageSize: 8,
        columns: [
          { key: "titulo", label: "Título" },
          { key: "tipo", label: "Tipo", render: (r) => {
            const colors = { deposito: "chip-success", sala: "chip-warning", espaco: "chip-info" };
            return el("span", { class: `chip ${colors[r.tipo] || ""}`, text: r.tipo });
          }},
          { key: "descricao", label: "Descrição" },
          { key: "data_fmt", label: "Data" },
          { key: "acoes", label: "Ações", render: (r) =>
            el("div", { class: "pc-actions" }, [
              el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openItemModal(r)) }, [el("i", { "data-lucide": "pencil" })]),
              el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => deleteItem(r)) }, [el("i", { "data-lucide": "trash-2" })]),
            ])
          },
        ],
      });
      tableContainer.appendChild(table.node);
      renderIcons(tableContainer);
    }

    function openItemModal(item) {
      const isEdit = !!item;
      const f = {
        titulo: el("input", { class: "input", value: item?.titulo || "", placeholder: "Título" }),
        tipo:   (() => {
          const s = el("select", { class: "select" }, [
            el("option", { value: "deposito", text: "Depósito" }),
            el("option", { value: "sala", text: "Sala" }),
            el("option", { value: "espaco", text: "Espaço" }),
          ]);
          if (item?.tipo) s.value = item.tipo;
          return s;
        })(),
        desc: el("input", { class: "input", value: item?.descricao || "", placeholder: "Descrição" }),
      };
      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? "Salvar" : "Criar"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? "Editar item" : "Novo item" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Título *" }), f.titulo]),
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Tipo" }), f.tipo]),
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Descrição" }), f.desc]),
          errEl,
        ]),
        el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
      ]);

      const backdrop = el("div", { class: "modal-backdrop" }, [card]);
      const close = () => backdrop.remove();
      backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
      cancelBtn.addEventListener("click", close);

      saveBtn.addEventListener("click", () => {
        const titulo = f.titulo.value.trim();
        if (!titulo) { errEl.textContent = "Título é obrigatório."; return; }
        const data = {
          titulo, tipo: f.tipo.value, descricao: f.desc.value.trim(),
          data: new Date().toISOString(),
        };
        if (isEdit) LocalDB.schoolData.update(item.id, data);
        else LocalDB.schoolData.create(data);
        notify(isEdit ? "Atualizado!" : "Criado!", "success");
        close(); load();
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
      setTimeout(() => f.titulo.focus(), 80);
    }

    function deleteItem(item) {
      openModal({
        title: "Excluir item",
        body: `Remover "${item.titulo}"?`,
        primaryLabel: "Excluir", danger: true,
        onConfirm: () => { LocalDB.schoolData.delete(item.id); notify("Removido.", "warning"); load(); },
      });
    }

    load();
  });
}
