/**
 * FASE 1 + FASE 4 — Modal de criação/edição de produto com campos logísticos detalhados.
 *
 * Campos do backend: nome, codigo, categoria_id, localizacao_id, quantidade_minima
 * Campos locais extras (Fase 1): torre, corredor, prateleira, nivel, posicao,
 *   descricao_localizacao, observacoes — armazenados via LocalDB.locationDetails
 */

import { el, renderIcons } from "../utils/helpers.js";
import { notify } from "./notifications.js";
import { API } from "../services/api.js";
import { LocalDB } from "../services/localInventoryStore.js";

/**
 * @param {object}   opts
 * @param {string}   opts.depositId
 * @param {object}   [opts.product]     — produto existente para edição; null = criação
 * @param {Array}    [opts.categories]  — lista de categorias já carregadas
 * @param {Array}    [opts.locations]   — lista de localizações já carregadas
 * @param {function} opts.onSave        — callback após salvar com sucesso
 */
export function openProductModal({ depositId, product = null, categories = [], locations = [], onSave }) {
  const isEdit = !!product;
  const localDetail = isEdit ? (LocalDB.getLocationDetail(product.id) || {}) : {};

  // ── Fields ──────────────────────────────────────────────────
  const fields = {
    nome:       el("input", { class: "input", value: product?.nome || "", placeholder: "Nome do produto" }),
    codigo:     el("input", { class: "input", value: product?.codigo || "", placeholder: "EAN, SKU, QR…" }),
    qty_min:    el("input", { class: "input", type: "number", value: String(product?.quantidade_minima ?? 0), min: "0", placeholder: "0" }),
    categoria:  makeSelect(categories, product?.categoria_id, "Sem categoria"),
    localizacao: makeSelect(locations, product?.localizacao_id, "Sem localização"),

    // Local logistic extras
    torre:      el("input", { class: "input", value: localDetail.torre || "", placeholder: "Ex.: Torre A" }),
    corredor:   el("input", { class: "input", value: localDetail.corredor || "", placeholder: "Ex.: 2" }),
    prateleira: el("input", { class: "input", value: localDetail.prateleira || "", placeholder: "Ex.: 4" }),
    nivel:      el("input", { class: "input", value: localDetail.nivel || "", placeholder: "Ex.: B" }),
    posicao:    el("input", { class: "input", value: localDetail.posicao || "", placeholder: "Ex.: 18" }),
    desc_local: el("input", { class: "input", value: localDetail.descricao_localizacao || "", placeholder: "Descrição da localização" }),
    obs:        el("textarea", { class: "input", style: "height:72px;resize:vertical", placeholder: "Observações internas" }),
  };
  if (localDetail.observacoes) fields.obs.value = localDetail.observacoes;

  const errEl = el("div", { class: "error-text" });

  const body = el("div", { class: "product-modal-body" }, [
    section("Identificação", [
      field("Nome *", fields.nome),
      field("Código (EAN / SKU / QR)", fields.codigo),
      field("Qtd. mínima", fields.qty_min),
      field("Categoria", fields.categoria),
      field("Localização (backend)", fields.localizacao),
    ]),
    section("Localização Física Detalhada", [
      el("p", { class: "muted", style: "font-size:0.82em;margin-bottom:10px" }, [
        "Estes campos são armazenados localmente até a integração com o backend."
      ]),
      el("div", { class: "form-grid-3" }, [
        field("Torre", fields.torre),
        field("Corredor", fields.corredor),
        field("Prateleira", fields.prateleira),
        field("Nível", fields.nivel),
        field("Posição", fields.posicao),
      ]),
      field("Descrição da localização", fields.desc_local),
      field("Observações", fields.obs),
    ]),
    errEl,
  ]);

  // ── Buttons ─────────────────────────────────────────────────
  const saveBtn = el("button", { class: "btn btn-primary" }, [
    el("i", { "data-lucide": "save" }),
    isEdit ? "Salvar alterações" : "Criar produto",
  ]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const card = el("div", { class: "modal modal-lg" }, [
    el("div", { class: "modal-header" }, [
      el("h3", { text: isEdit ? `Editar: ${product.nome}` : "Novo Produto" }),
    ]),
    body,
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  const close = () => backdrop.remove();
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const nome = fields.nome.value.trim();
    if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;

    try {
      const payload = {
        nome,
        codigo: fields.codigo.value.trim() || undefined,
        quantidade_minima: parseInt(fields.qty_min.value) || 0,
        categoria_id: fields.categoria.value || undefined,
        localizacao_id: fields.localizacao.value || undefined,
      };

      let saved;
      if (isEdit) {
        saved = await API.updateProduct(depositId, product.id, payload);
      } else {
        saved = await API.createProduct(depositId, payload);
      }

      // Save local logistic detail
      const localPayload = {
        torre:      fields.torre.value.trim(),
        corredor:   fields.corredor.value.trim(),
        prateleira: fields.prateleira.value.trim(),
        nivel:      fields.nivel.value.trim(),
        posicao:    fields.posicao.value.trim(),
        descricao_localizacao: fields.desc_local.value.trim(),
        observacoes: fields.obs.value.trim(),
      };
      LocalDB.saveLocationDetail(saved?.id || product?.id, localPayload);

      notify(isEdit ? "Produto atualizado!" : "Produto criado!", "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao salvar produto.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  setTimeout(() => fields.nome.focus(), 80);
  return close;
}

// ── Location card (shown inside product card) ─────────────────
export function LocationDetailBadge(productId) {
  const detail = LocalDB.getLocationDetail(productId);
  if (!detail) return null;

  const parts = [
    detail.torre && `Torre ${detail.torre}`,
    detail.corredor && `Corredor ${detail.corredor}`,
    detail.prateleira && `Prat. ${detail.prateleira}`,
    detail.nivel && `Nível ${detail.nivel}`,
    detail.posicao && `Pos. ${detail.posicao}`,
  ].filter(Boolean);

  if (parts.length === 0 && !detail.descricao_localizacao) return null;

  return el("div", { class: "location-badge" }, [
    el("i", { "data-lucide": "map-pin", style: "width:12px;height:12px;margin-right:4px" }),
    parts.join(" › ") || detail.descricao_localizacao,
  ]);
}

// ── Movement Modal (entrada/saída) ──────────────────────────────
export function openMovementModal({ depositId, products = [], onSave, initialCode = "" }) {
  const productSelect = makeSelect(
    products.map(p => ({ id: p.id, nome: `${p.name} (${p.code})` })),
    null,
    "Selecione o produto"
  );

  // If initial code provided, pre-select matching product
  if (initialCode) {
    const match = products.find(p => p.code === initialCode || p.name.toLowerCase().includes(initialCode.toLowerCase()));
    if (match) productSelect.value = match.id;
  }

  const tipoEl = el("select", { class: "select" }, [
    el("option", { value: "entrada", text: "Entrada" }),
    el("option", { value: "saida", text: "Saída" }),
  ]);
  const qtyEl = el("input", { class: "input", type: "number", value: "1", min: "1", placeholder: "Quantidade" });
  const obsEl = el("input", { class: "input", placeholder: "Observação (opcional)" });
  const errEl = el("div", { class: "error-text" });

  const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "check" }), "Registrar"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [el("h3", { text: "Registrar Movimentação" })]),
    el("div", { class: "product-modal-body" }, [
      field("Produto *", productSelect),
      field("Tipo", tipoEl),
      field("Quantidade *", qtyEl),
      field("Observação", obsEl),
      errEl,
    ]),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  const close = () => backdrop.remove();
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const productId = productSelect.value;
    const qty = parseInt(qtyEl.value);
    if (!productId) { errEl.textContent = "Selecione um produto."; return; }
    if (!qty || qty < 1) { errEl.textContent = "Quantidade inválida."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      const tipo = tipoEl.value;
      const payload = { produto_id: productId, quantidade: qty, observacao: obsEl.value.trim() || undefined };
      if (tipo === "entrada") {
        await API.stockEntry(depositId, payload);
      } else {
        await API.stockExit(depositId, payload);
      }
      notify(`${tipo === "entrada" ? "Entrada" : "Saída"} registrada com sucesso!`, "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao registrar movimentação.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  return close;
}

// ── Helpers ─────────────────────────────────────────────────────
function makeSelect(items, selected, emptyLabel) {
  const s = el("select", { class: "select" }, [
    el("option", { value: "", text: emptyLabel }),
    ...items.map(i => {
      const opt = el("option", { value: i.id, text: i.nome || i.name || i.id });
      if (i.id === selected) opt.selected = true;
      return opt;
    }),
  ]);
  return s;
}

function field(label, input) {
  return el("div", { class: "field" }, [
    el("label", { class: "field-label", text: label }),
    input,
  ]);
}

function section(title, children) {
  return el("div", { class: "modal-section" }, [
    el("h4", { class: "modal-section-title", text: title }),
    ...children,
  ]);
}
