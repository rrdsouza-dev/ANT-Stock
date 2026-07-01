/**
 * Gestão Escolar — CRUD de Depósitos (dados reais, persistidos no backend).
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { openModal } from "../components/modal.js";
import { guardedClick } from "../utils/security.js";

const TIPO_LABEL = { escolar: "Escolar", didatico: "Didático" };

export function SchoolPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const isGestao = session.user?.profile === "gestao";

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Gestão Escolar" }),
        el("p", { class: "muted", text: "Depósitos da escola (estoque escolar, material didático etc.)." }),
      ]),
      isGestao
        ? el("button", { class: "btn btn-soft", onclick: guardedClick(() => openDepositModal(null)) }, [
            el("i", { "data-lucide": "plus" }), "Novo depósito",
          ])
        : el("span"),
    ]);

    const tableContainer = el("div", {}, [
      el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando depósitos…"]),
    ]);
    content.append(head, tableContainer);
    renderIcons(content);

    async function load() {
      try {
        const deposits = await API.deposits();
        tableContainer.innerHTML = "";
        if (!deposits.length) {
          tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum depósito cadastrado."]));
          return;
        }
        const rows = deposits.map(d => ({ ...d, data_fmt: d.criado_em?.slice(0, 10) || "—" }));
        const table = DataTable({
          rows, pageSize: 8,
          columns: [
            { key: "nome", label: "Nome" },
            { key: "tipo", label: "Tipo", render: (r) =>
              el("span", { class: `chip ${r.tipo === "escolar" ? "chip-success" : "chip-info"}`, text: TIPO_LABEL[r.tipo] || r.tipo })
            },
            { key: "descricao", label: "Descrição", render: (r) => el("span", { text: r.descricao || "—" }) },
            { key: "data_fmt", label: "Criado em" },
            ...(isGestao ? [{
              key: "acoes", label: "Ações", render: (r) =>
                el("div", { class: "pc-actions" }, [
                  el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openDepositModal(r)) }, [el("i", { "data-lucide": "pencil" })]),
                  el("button", { class: "icon-btn", title: "Desativar", onclick: guardedClick(() => deleteDeposit(r)) }, [el("i", { "data-lucide": "trash-2" })]),
                ])
            }] : []),
          ],
        });
        tableContainer.appendChild(table.node);
        renderIcons(tableContainer);
      } catch (err) {
        tableContainer.innerHTML = "";
        tableContainer.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar depósitos."]));
        notify(err.message || "Erro.", "error");
      }
    }

    function openDepositModal(deposit) {
      const isEdit = !!deposit;
      const f = {
        nome: el("input", { class: "input", value: deposit?.nome || "", placeholder: "Nome do depósito *" }),
        tipo: (() => {
          const s = el("select", { class: "select" }, [
            el("option", { value: "escolar", text: "Escolar" }),
            el("option", { value: "didatico", text: "Didático" }),
          ]);
          if (deposit?.tipo) s.value = deposit.tipo;
          return s;
        })(),
        desc: el("input", { class: "input", value: deposit?.descricao || "", placeholder: "Descrição (opcional)" }),
      };
      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? "Salvar" : "Criar"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? "Editar depósito" : "Novo depósito" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Nome *" }), f.nome]),
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

      saveBtn.addEventListener("click", async () => {
        const nome = f.nome.value.trim();
        if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
        errEl.textContent = "";
        saveBtn.disabled = true;
        try {
          const data = { nome, tipo: f.tipo.value, descricao: f.desc.value.trim() || undefined };
          if (isEdit) await API.updateDeposit(deposit.id, data);
          else await API.createDeposit(data);
          notify(isEdit ? "Depósito atualizado!" : "Depósito criado!", "success");
          close(); load();
        } catch (err) {
          errEl.textContent = err.message || "Erro ao salvar depósito.";
        } finally {
          saveBtn.disabled = false;
        }
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
      setTimeout(() => f.nome.focus(), 80);
    }

    function deleteDeposit(deposit) {
      openModal({
        title: "Desativar depósito",
        body: `Desativar "${deposit.nome}"? Os produtos e o histórico continuam preservados.`,
        primaryLabel: "Desativar", danger: true,
        onConfirm: async () => {
          await API.deleteDeposit(deposit.id);
          notify("Depósito desativado.", "warning");
          load();
        },
      });
    }

    load();
  });
}
