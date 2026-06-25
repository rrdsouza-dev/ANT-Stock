/**
 * Modal de produto (criar/editar) + Modal de movimentação + Modal pós-escaneamento.
 * Localização padronizada via selects (Torre / Corredor / Prateleira / Posição).
 */

import { el, renderIcons } from "../utils/helpers.js";
import { notify } from "./notifications.js";
import { API } from "../services/api.js";
import { LocalDB } from "../services/localInventoryStore.js";

// ── Opções padronizadas de localização ─────────────────────────
const TORRES     = ["Torre A", "Torre B", "Torre C"];
const CORREDORES = ["Corredor 1", "Corredor 2", "Corredor 3"];
const PRATELEIRAS = ["Prateleira 1", "Prateleira 2", "Prateleira 3", "Prateleira 4", "Prateleira 5"];
const POSICOES   = ["A1", "A2", "A3", "B1", "B2", "B3"];
const UNIDADES   = ["UN", "CX", "KG", "L", "M", "PC", "PAR", "FD", "RL"];

function makeSelect(items, selected, emptyLabel) {
  const s = el("select", { class: "select" }, [
    el("option", { value: "", text: emptyLabel }),
    ...items.map(i => {
      const id = (typeof i === "object") ? i.id : i;
      const txt = (typeof i === "object") ? (i.nome || i.name || i.id) : i;
      const opt = el("option", { value: id, text: txt });
      if (id === selected) opt.selected = true;
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

// ── Modal Principal de Produto ──────────────────────────────────
export function openProductModal({ depositId, product = null, categories = [], locations = [], onSave }) {
  const isEdit = !!product;
  const localDetail = isEdit ? (LocalDB.getLocationDetail(product.id) || {}) : {};

  const fields = {
    nome:       el("input", { class: "input", value: product?.nome || "", placeholder: "Nome do produto" }),
    codigo:     el("input", { class: "input", value: product?.codigo || "", placeholder: "EAN, SKU, QR…" }),
    qty_min:    el("input", { class: "input", type: "number", value: String(product?.quantidade_minima ?? 0), min: "0", placeholder: "0" }),
    categoria:  makeSelect(categories, product?.categoria_id, "Sem categoria"),
    unidade:    makeSelect(UNIDADES, product?.unidade_medida || "", "Unidade de medida"),
    qty_caixa:  el("input", { class: "input", type: "number", value: String(product?.quantidade_por_caixa ?? ""), min: "1", placeholder: "Ex.: 12" }),
    validade:   el("input", { class: "input", value: product?.validade || "", placeholder: "MM/AAAA" }),
    obs:        el("textarea", { class: "input", style: "height:72px;resize:vertical", placeholder: "Observações internas" }),

    // Localização padronizada
    torre:      makeSelect(TORRES, localDetail.torre || "", "Selecione a torre"),
    corredor:   makeSelect(CORREDORES, localDetail.corredor || "", "Selecione o corredor"),
    prateleira: makeSelect(PRATELEIRAS, localDetail.prateleira || "", "Selecione a prateleira"),
    posicao:    makeSelect(POSICOES, localDetail.posicao || "", "Selecione a posição"),

    // Backend location list (optional)
    localizacao: makeSelect(locations, product?.localizacao_id, "Localização do sistema"),
  };
  if (product?.observacoes || localDetail.observacoes) {
    fields.obs.value = product?.observacoes || localDetail.observacoes || "";
  }

  const errEl = el("div", { class: "error-text" });

  const body = el("div", { class: "product-modal-body" }, [
    section("Identificação", [
      field("Nome *", fields.nome),
      field("Código (EAN / SKU / QR)", fields.codigo),
      field("Unidade de medida", fields.unidade),
      field("Qtd. por caixa", fields.qty_caixa),
      field("Validade", fields.validade),
      field("Qtd. mínima", fields.qty_min),
      field("Categoria", fields.categoria),
    ]),
    section("Localização Física", [
      el("div", { class: "form-grid-2" }, [
        field("Torre", fields.torre),
        field("Corredor", fields.corredor),
        field("Prateleira", fields.prateleira),
        field("Posição", fields.posicao),
      ]),
      field("Localização do sistema", fields.localizacao),
    ]),
    section("Observações", [
      field("Observações", fields.obs),
    ]),
    errEl,
  ]);

  const saveBtn = el("button", { class: "btn btn-primary" }, [
    el("i", { "data-lucide": "save" }),
    isEdit ? " Salvar alterações" : " Criar produto",
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
        unidade_medida: fields.unidade.value || undefined,
        quantidade_por_caixa: parseInt(fields.qty_caixa.value) || undefined,
        validade: fields.validade.value.trim() || undefined,
        observacoes: fields.obs.value.trim() || undefined,
      };

      let saved;
      if (isEdit) {
        saved = await API.updateProduct(depositId, product.id, payload);
      } else {
        saved = await API.createProduct(depositId, payload);
      }

      // Save local logistic detail
      const localPayload = {
        torre:      fields.torre.value,
        corredor:   fields.corredor.value,
        prateleira: fields.prateleira.value,
        posicao:    fields.posicao.value,
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

// ── Modal pós-escaneamento ──────────────────────────────────────
// Abre quando um código de barras é escaneado.
// - Produto encontrado: mostra detalhes + botões de entrada/saída
// - Produto não encontrado: abre cadastro rápido
export function openScanModal({ depositId, code, products = [], categories = [], locations = [], onSave }) {
  const found = products.find(p => p.codigo === code || p.code === code);

  if (found) {
    _openFoundModal({ depositId, product: found, categories, locations, onSave });
  } else {
    _openNotFoundModal({ depositId, code, categories, locations, onSave });
  }
}

function _openFoundModal({ depositId, product, categories, locations, onSave }) {
  const localDetail = LocalDB.getLocationDetail(product.id) || {};
  const locStr = [localDetail.torre, localDetail.corredor, localDetail.prateleira, localDetail.posicao]
    .filter(Boolean).join(" › ") || product.localizacao_id || "—";

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("span", { class: "badge badge-success", text: "Produto encontrado" }),
      el("h3", { text: product.nome || product.name }),
    ]),
    el("div", { class: "product-modal-body" }, [
      el("div", { class: "scan-info-grid" }, [
        infoRow("Código", product.codigo || product.code || "—"),
        infoRow("Categoria", product.categoria_id ? (categories.find(c => c.id === product.categoria_id)?.nome || product.categoria_id) : "—"),
        infoRow("Localização", locStr),
        infoRow("Validade", product.validade || "—"),
        infoRow("Unidade", product.unidade_medida || "—"),
        infoRow("Qtd. por caixa", product.quantidade_por_caixa || "—"),
      ]),
    ]),
    el("div", { class: "modal-actions" }, [
      el("button", { class: "btn btn-ghost", text: "Fechar", onclick: () => backdrop.remove() }),
      el("button", { class: "btn btn-secondary", text: "Registrar Saída", onclick: () => {
        backdrop.remove();
        openExitModal({ depositId, product, products: [product], onSave });
      }}),
      el("button", { class: "btn btn-primary", text: "Registrar Entrada", onclick: () => {
        backdrop.remove();
        openEntryModal({ depositId, product, locations, onSave });
      }}),
    ]),
  ]);

  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) backdrop.remove(); });
  document.body.appendChild(backdrop);
  renderIcons(backdrop);
}

function _openNotFoundModal({ depositId, code, categories, locations, onSave }) {
  const fields = {
    nome:      el("input", { class: "input", placeholder: "Nome do produto *" }),
    codigo:    el("input", { class: "input", value: code, placeholder: "Código de barras" }),
    categoria: makeSelect(categories, null, "Sem categoria"),
    unidade:   makeSelect(UNIDADES, "", "Unidade de medida"),
    qty_caixa: el("input", { class: "input", type: "number", min: "1", placeholder: "Qtd. por caixa" }),
    validade:  el("input", { class: "input", placeholder: "Validade (MM/AAAA)" }),
    obs:       el("textarea", { class: "input", style: "height:60px;resize:vertical", placeholder: "Observações" }),
  };
  const errEl = el("div", { class: "error-text" });

  const saveBtn = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "plus" }), " Cadastrar produto"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("span", { class: "badge badge-warning", text: "Produto não encontrado" }),
      el("h3", { text: "Cadastro Rápido" }),
      el("p", { class: "muted", style: "font-size:0.85em", text: `Código: ${code}` }),
    ]),
    el("div", { class: "product-modal-body" }, [
      field("Nome *", fields.nome),
      field("Código de barras", fields.codigo),
      field("Categoria", fields.categoria),
      field("Unidade de medida", fields.unidade),
      field("Qtd. por caixa", fields.qty_caixa),
      field("Validade", fields.validade),
      field("Observações", fields.obs),
      errEl,
    ]),
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
        categoria_id: fields.categoria.value || undefined,
        unidade_medida: fields.unidade.value || undefined,
        quantidade_por_caixa: parseInt(fields.qty_caixa.value) || undefined,
        validade: fields.validade.value.trim() || undefined,
        observacoes: fields.obs.value.trim() || undefined,
      };
      await API.createProduct(depositId, payload);
      notify("Produto cadastrado com sucesso!", "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao cadastrar produto.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  setTimeout(() => fields.nome.focus(), 80);
}

// ── Modal de Entrada ──────────────────────────────────────────
export function openEntryModal({ depositId, product = null, products = [], locations = [], onSave }) {
  const productSelect = product
    ? null
    : makeSelect(products.map(p => ({ id: p.id, nome: `${p.nome || p.name} (${p.codigo || p.code || ""})` })), null, "Selecione o produto");

  const qtyEl       = el("input", { class: "input", type: "number", value: "1", min: "1", placeholder: "Quantidade recebida" });
  const qtyCaixaEl  = el("input", { class: "input", type: "number", min: "1", placeholder: "Qtd. por caixa" });
  const validadeEl  = el("input", { class: "input", placeholder: "Validade (MM/AAAA)" });
  const torre       = makeSelect(TORRES, "", "Selecione a torre");
  const corredor    = makeSelect(CORREDORES, "", "Selecione o corredor");
  const prateleira  = makeSelect(PRATELEIRAS, "", "Selecione a prateleira");
  const posicao     = makeSelect(POSICOES, "", "Selecione a posição");
  const obsEl       = el("input", { class: "input", placeholder: "Observação (opcional)" });
  const errEl       = el("div", { class: "error-text" });

  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "arrow-down-circle" }), " Registrar Entrada"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const headerTitle = product ? `Entrada — ${product.nome || product.name}` : "Registrar Entrada";

  const bodyChildren = [];
  if (!product) bodyChildren.push(field("Produto *", productSelect));
  bodyChildren.push(
    field("Quantidade recebida *", qtyEl),
    field("Qtd. por caixa", qtyCaixaEl),
    field("Validade", validadeEl),
    section("Localização", [
      el("div", { class: "form-grid-2" }, [
        field("Torre", torre),
        field("Corredor", corredor),
        field("Prateleira", prateleira),
        field("Posição", posicao),
      ]),
    ]),
    field("Observação", obsEl),
    errEl,
  );

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [el("h3", { text: headerTitle })]),
    el("div", { class: "product-modal-body" }, bodyChildren),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  const close = () => backdrop.remove();
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const productId = product?.id || productSelect?.value;
    const qty = parseInt(qtyEl.value);
    if (!productId) { errEl.textContent = "Selecione um produto."; return; }
    if (!qty || qty < 1) { errEl.textContent = "Quantidade inválida."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      const payload = {
        produto_id: productId,
        quantidade: qty,
        observacao: obsEl.value.trim() || undefined,
      };
      await API.stockEntry(depositId, payload);

      // Update local location detail
      if (product?.id && (torre.value || corredor.value || prateleira.value || posicao.value)) {
        LocalDB.saveLocationDetail(product.id, {
          torre: torre.value, corredor: corredor.value,
          prateleira: prateleira.value, posicao: posicao.value,
        });
      }

      // Update product validade/qty_caixa if filled
      if (product?.id && (validadeEl.value || qtyCaixaEl.value)) {
        await API.updateProduct(depositId, product.id, {
          validade: validadeEl.value.trim() || undefined,
          quantidade_por_caixa: parseInt(qtyCaixaEl.value) || undefined,
        }).catch(() => {});
      }

      notify("Entrada registrada com sucesso!", "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao registrar entrada.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  return close;
}

// ── Modal de Saída ────────────────────────────────────────────
export function openExitModal({ depositId, product = null, products = [], onSave }) {
  const productSelect = product
    ? null
    : makeSelect(products.map(p => ({ id: p.id, nome: `${p.nome || p.name} (${p.codigo || p.code || ""})` })), null, "Selecione o produto");

  const qtyEl     = el("input", { class: "input", type: "number", value: "1", min: "1", placeholder: "Quantidade retirada" });
  const destinoEl = el("input", { class: "input", placeholder: "Destino (ex.: Sala 3, Professor João)" });
  const obsEl     = el("input", { class: "input", placeholder: "Observação (opcional)" });
  const errEl     = el("div", { class: "error-text" });

  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "arrow-up-circle" }), " Registrar Saída"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const headerTitle = product ? `Saída — ${product.nome || product.name}` : "Registrar Saída";

  const bodyChildren = [];
  if (!product) bodyChildren.push(field("Produto *", productSelect));
  bodyChildren.push(
    field("Quantidade retirada *", qtyEl),
    field("Destino", destinoEl),
    field("Observação", obsEl),
    errEl,
  );

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [el("h3", { text: headerTitle })]),
    el("div", { class: "product-modal-body" }, bodyChildren),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  const close = () => backdrop.remove();
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const productId = product?.id || productSelect?.value;
    const qty = parseInt(qtyEl.value);
    if (!productId) { errEl.textContent = "Selecione um produto."; return; }
    if (!qty || qty < 1) { errEl.textContent = "Quantidade inválida."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      const obs = [destinoEl.value.trim(), obsEl.value.trim()].filter(Boolean).join(" | ");
      await API.stockExit(depositId, {
        produto_id: productId,
        quantidade: qty,
        observacao: obs || undefined,
      });
      notify("Saída registrada com sucesso!", "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao registrar saída.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  return close;
}

// ── Movement Modal (combined, backward compat) ────────────────
export function openMovementModal({ depositId, products = [], onSave, initialCode = "" }) {
  const matched = initialCode
    ? products.find(p => p.code === initialCode || p.codigo === initialCode)
    : null;

  if (matched) {
    openEntryModal({ depositId, product: matched, products, onSave });
  } else {
    openEntryModal({ depositId, products, onSave });
  }
}

// ── Location badge ────────────────────────────────────────────
export function LocationDetailBadge(productId) {
  const detail = LocalDB.getLocationDetail(productId);
  if (!detail) return null;

  const parts = [
    detail.torre,
    detail.corredor,
    detail.prateleira,
    detail.posicao,
  ].filter(Boolean);

  if (parts.length === 0) return null;

  return el("div", { class: "location-badge" }, [
    el("i", { "data-lucide": "map-pin", style: "width:12px;height:12px;margin-right:4px" }),
    parts.join(" › "),
  ]);
}

// ── Helpers ───────────────────────────────────────────────────
function infoRow(label, value) {
  return el("div", { class: "scan-info-row" }, [
    el("span", { class: "scan-info-label muted", text: label }),
    el("span", { class: "scan-info-value", text: String(value) }),
  ]);
}
