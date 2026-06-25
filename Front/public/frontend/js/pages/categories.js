/**
 * FASE 4 — CRUD completo de Categorias e Localizações.
 */
import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { DataTable } from "../components/table.js";
import { notify } from "../components/notifications.js";
import { openModal } from "../components/modal.js";
import { guardedClick } from "../utils/security.js";

export function CategoriesPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    let depositId = null;
    let activeTab = "categorias";

    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Categorias & Localizações" }),
        el("p", { class: "muted", text: "Gerencie categorias de produtos e localizações físicas do depósito." }),
      ]),
    ]);

    const tabsRow = el("div", { class: "tabs" });
    const body = el("div", { style: "margin-top:16px" });

    content.append(head, tabsRow, body);

    function renderTabs() {
      tabsRow.innerHTML = "";
      ["categorias", "localizacoes"].forEach(t => {
        const b = el("button", {
          class: "tab" + (activeTab === t ? " active" : ""),
          text: t === "categorias" ? "Categorias" : "Localizações",
        });
        b.addEventListener("click", () => { activeTab = t; renderTabs(); loadActive(); });
        tabsRow.appendChild(b);
      });
    }

    async function ensureDeposit() {
      if (depositId) return depositId;
      depositId = session.depositId;
      if (!depositId) {
        const deposits = await API.deposits();
        if (!deposits?.length) throw new Error("Nenhum depósito vinculado.");
        depositId = deposits[0].id;
        session.setDepositId(depositId);
      }
      return depositId;
    }

    async function loadActive() {
      body.innerHTML = "";
      body.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Carregando…"]));
      try {
        await ensureDeposit();
        if (activeTab === "categorias") await renderCategories();
        else await renderLocations();
      } catch (err) {
        body.innerHTML = "";
        body.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, [err.message || "Erro."]));
      }
    }

    // ── Categorias ─────────────────────────────────────────────
    async function renderCategories() {
      const cats = await API.categories(depositId, { limite: 200 });
      body.innerHTML = "";

      const addBtn = el("button", { class: "btn btn-soft", style: "margin-bottom:14px", onclick: guardedClick(() => openCatModal(null, cats)) }, [
        el("i", { "data-lucide": "plus" }), "Nova categoria",
      ]);

      if (!cats.length) {
        body.append(addBtn, el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhuma categoria cadastrada."]));
        renderIcons(body);
        return;
      }

      const rows = cats.map(c => ({
        id: c.id,
        nome: c.nome,
        descricao: c.descricao || "—",
        ativo: c.ativo ? "Sim" : "Não",
        _raw: c,
      }));

      const table = DataTable({
        rows, pageSize: 10,
        columns: [
          { key: "nome", label: "Nome" },
          { key: "descricao", label: "Descrição" },
          { key: "ativo", label: "Ativo", render: (r) =>
            el("span", { class: `chip ${r.ativo === "Sim" ? "chip-success" : "chip-warning"}`, text: r.ativo })
          },
          { key: "acoes", label: "Ações", render: (r) =>
            el("div", { class: "pc-actions" }, [
              el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openCatModal(r._raw, cats)) },
                [el("i", { "data-lucide": "pencil" })]),
              el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => deleteCat(r._raw)) },
                [el("i", { "data-lucide": "trash-2" })]),
            ])
          },
        ],
      });
      body.append(addBtn, table.node);
      renderIcons(body);
    }

    function openCatModal(cat, allCats) {
      const isEdit = !!cat;
      const nomeEl = el("input", { class: "input", value: cat?.nome || "", placeholder: "Nome da categoria" });
      const descEl = el("input", { class: "input", value: cat?.descricao || "", placeholder: "Descrição (opcional)" });
      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? "Salvar" : "Criar"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? "Editar categoria" : "Nova categoria" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Nome *" }), nomeEl]),
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Descrição" }), descEl]),
          errEl,
        ]),
        el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
      ]);

      const backdrop = el("div", { class: "modal-backdrop" }, [card]);
      const close = () => backdrop.remove();
      backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
      cancelBtn.addEventListener("click", close);

      saveBtn.addEventListener("click", async () => {
        const nome = nomeEl.value.trim();
        if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
        errEl.textContent = ""; saveBtn.disabled = true;
        try {
          const payload = { nome, descricao: descEl.value.trim() || undefined };
          if (isEdit) await API.updateCategory(depositId, cat.id, payload);
          else await API.createCategory(depositId, payload);
          notify(isEdit ? "Categoria atualizada!" : "Categoria criada!", "success");
          close(); loadActive();
        } catch (err) {
          errEl.textContent = err.message || "Erro ao salvar.";
        } finally { saveBtn.disabled = false; }
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
      setTimeout(() => nomeEl.focus(), 80);
    }

    async function deleteCat(cat) {
      openModal({
        title: "Excluir categoria",
        body: `Remover categoria "${cat.nome}"?`,
        primaryLabel: "Excluir", danger: true,
        onConfirm: async () => {
          await API.deleteCategory(depositId, cat.id);
          notify("Categoria removida.", "warning");
          loadActive();
        },
      });
    }

    // ── Localizações ───────────────────────────────────────────
    async function renderLocations() {
      const locs = await API.locations(depositId, { limite: 200 });
      body.innerHTML = "";

      const addBtn = el("button", { class: "btn btn-soft", style: "margin-bottom:14px", onclick: guardedClick(() => openLocModal(null)) }, [
        el("i", { "data-lucide": "plus" }), "Nova localização",
      ]);

      if (!locs.length) {
        body.append(addBtn, el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhuma localização cadastrada."]));
        renderIcons(body); return;
      }

      const rows = locs.map(l => ({
        id: l.id,
        nome: l.nome,
        corredor: l.corredor || "—",
        prateleira: l.prateleira || "—",
        posicao: l.posicao || "—",
        ativo: l.ativo ? "Sim" : "Não",
        _raw: l,
      }));

      const table = DataTable({
        rows, pageSize: 10,
        columns: [
          { key: "nome", label: "Nome" },
          { key: "corredor", label: "Corredor" },
          { key: "prateleira", label: "Prateleira" },
          { key: "posicao", label: "Posição" },
          { key: "ativo", label: "Ativo", render: (r) =>
            el("span", { class: `chip ${r.ativo === "Sim" ? "chip-success" : "chip-warning"}`, text: r.ativo })
          },
          { key: "acoes", label: "Ações", render: (r) =>
            el("div", { class: "pc-actions" }, [
              el("button", { class: "icon-btn", title: "Editar", onclick: guardedClick(() => openLocModal(r._raw)) },
                [el("i", { "data-lucide": "pencil" })]),
              el("button", { class: "icon-btn", title: "Excluir", onclick: guardedClick(() => deleteLoc(r._raw)) },
                [el("i", { "data-lucide": "trash-2" })]),
            ])
          },
        ],
      });
      body.append(addBtn, table.node);
      renderIcons(body);
    }

    function openLocModal(loc) {
      const isEdit = !!loc;

      // Standardized options
      const TORRES     = ["Torre A", "Torre B", "Torre C"];
      const CORREDORES = ["1", "2", "3", "4"];
      const PRATELEIRAS = ["1", "2", "3", "4", "5"];
      const POSICOES   = ["A1", "A2", "A3", "B1", "B2", "B3"];

      function makeSelect(opts, val, emptyLabel) {
        return el("select", { class: "select" }, [
          el("option", { value: "", text: emptyLabel }),
          ...opts.map(o => {
            const opt = el("option", { value: o, text: o });
            if (o === val) opt.selected = true;
            return opt;
          }),
        ]);
      }

      const nomeEl = el("input", { class: "input", value: loc?.nome || "", placeholder: "Nome da localização (ex: Torre A / Corredor 1 / Prateleira 2 / A1)" });
      const f = {
        torre:      makeSelect(TORRES,      loc?.torre || "",      "Selecione a torre"),
        corredor:   makeSelect(CORREDORES,  loc?.corredor || "",   "Selecione o corredor"),
        prateleira: makeSelect(PRATELEIRAS, loc?.prateleira || "", "Selecione a prateleira"),
        posicao:    makeSelect(POSICOES,    loc?.posicao || "",    "Selecione a posição"),
      };
      const errEl = el("div", { class: "error-text" });
      const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? " Salvar" : " Criar"]);
      const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

      // Auto-fill nome when selects change
      function autoNome() {
        const parts = [f.torre.value, f.corredor.value ? "Corredor " + f.corredor.value : "",
          f.prateleira.value ? "Prateleira " + f.prateleira.value : "", f.posicao.value].filter(Boolean);
        if (parts.length > 0 && !nomeEl.value) nomeEl.value = parts.join(" / ");
      }
      [f.torre, f.corredor, f.prateleira, f.posicao].forEach(s => s.addEventListener("change", autoNome));

      const card = el("div", { class: "modal" }, [
        el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? "Editar localização" : "Nova localização" })]),
        el("div", { class: "product-modal-body" }, [
          el("div", { class: "field" }, [el("label", { class: "field-label", text: "Nome da localização *" }), nomeEl]),
          el("div", { class: "form-grid-2" }, [
            el("div", { class: "field" }, [el("label", { class: "field-label", text: "Torre" }), f.torre]),
            el("div", { class: "field" }, [el("label", { class: "field-label", text: "Corredor" }), f.corredor]),
            el("div", { class: "field" }, [el("label", { class: "field-label", text: "Prateleira" }), f.prateleira]),
            el("div", { class: "field" }, [el("label", { class: "field-label", text: "Posição" }), f.posicao]),
          ]),
          errEl,
        ]),
        el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
      ]);

      const backdrop = el("div", { class: "modal-backdrop" }, [card]);
      const close = () => backdrop.remove();
      backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
      cancelBtn.addEventListener("click", close);

      saveBtn.addEventListener("click", async () => {
        const nome = nomeEl.value.trim();
        if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
        errEl.textContent = ""; saveBtn.disabled = true;
        try {
          const payload = {
            nome,
            torre:      f.torre.value || undefined,
            corredor:   f.corredor.value || undefined,
            prateleira: f.prateleira.value || undefined,
            posicao:    f.posicao.value || undefined,
          };
          if (isEdit) await API.updateLocation(depositId, loc.id, payload);
          else await API.createLocation(depositId, payload);
          notify(isEdit ? "Localização atualizada!" : "Localização criada!", "success");
          close(); loadActive();
        } catch (err) {
          errEl.textContent = err.message || "Erro ao salvar.";
        } finally { saveBtn.disabled = false; }
      });

      document.body.appendChild(backdrop);
      renderIcons(backdrop);
      setTimeout(() => nomeEl.focus(), 80);
    }

    async function deleteLoc(loc) {
      openModal({
        title: "Excluir localização",
        body: `Remover localização "${loc.nome}"?`,
        primaryLabel: "Excluir", danger: true,
        onConfirm: async () => {
          await API.deleteLocation(depositId, loc.id);
          notify("Localização removida.", "warning");
          loadActive();
        },
      });
    }

    renderTabs();
    loadActive();
  });
}
