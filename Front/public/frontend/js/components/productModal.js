/**
 * productModal.js — Modais de produto, escaneamento, entrada e saída.
 * Localização totalmente padronizada por selects (sem texto livre).
 */

import { el, renderIcons } from "../utils/helpers.js";
import { notify } from "./notifications.js";
import { API } from "../services/api.js";

// ── Opções padronizadas ──────────────────────────────────────────
const TORRES      = ["Torre A", "Torre B", "Torre C"];
const CORREDORES  = ["1", "2", "3", "4"];
const PRATELEIRAS = ["1", "2", "3", "4", "5"];
const POSICOES    = ["A1", "A2", "A3", "B1", "B2", "B3"];
const UNIDADES    = ["UN", "CX", "KG", "L", "M", "PC", "PAR", "FD", "RL"];

// ── Helpers ──────────────────────────────────────────────────────
function mkSelect(opts, selected, emptyLabel) {
  const s = el("select", { class: "select" }, [
    el("option", { value: "", text: emptyLabel || "Selecione…" }),
    ...opts.map(o => {
      const id  = typeof o === "object" ? o.id  : o;
      const txt = typeof o === "object" ? (o.nome || o.name || o.id) : o;
      const opt = el("option", { value: id, text: txt });
      if (id === selected || o === selected) opt.selected = true;
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

function infoRow(label, value) {
  return el("div", { class: "scan-info-row" }, [
    el("span", { class: "scan-info-label muted", text: label }),
    el("span", { class: "scan-info-value", text: String(value ?? "—") }),
  ]);
}

function openBackdrop(card) {
  const backdrop = el("div", { class: "modal-backdrop" }, [card]);
  const close = () => backdrop.remove();
  backdrop.addEventListener("click", e => { if (e.target === backdrop) close(); });
  document.body.appendChild(backdrop);
  renderIcons(backdrop);
  return close;
}

// ── Modal de Produto (criar / editar) ────────────────────────────
export function openProductModal({ depositId, product = null, categories = [], locations = [], onSave }) {
  const isEdit = !!product;

  const f = {
    nome:       el("input", { class: "input", value: product?.nome || "", placeholder: "Nome do produto *" }),
    codigo:     el("input", { class: "input", value: product?.codigo || "", placeholder: "EAN / SKU / QR Code" }),
    lote:       el("input", { class: "input", value: product?.lote || "", placeholder: "Número do lote" }),
    qtd_min:    el("input", { class: "input", type: "number", min: "0", value: String(product?.quantidade_minima ?? 0) }),
    unidade:    mkSelect(UNIDADES, product?.unidade_medida || "", "Unidade de medida"),
    qty_caixa:  el("input", { class: "input", type: "number", min: "1", value: product?.quantidade_por_caixa || "" }),
    validade:   el("input", { class: "input", value: product?.validade || "", placeholder: "MM/AAAA" }),
    obs:        el("textarea", { class: "input", style: "height:64px;resize:vertical" }),
    categoria:  mkSelect(categories, product?.categoria_id, "Sem categoria"),
    localizacao: mkSelect(locations, product?.localizacao_id, "Sem localização"),
    torre:      mkSelect(TORRES,      product?.torre || "",      "Torre"),
    corredor:   mkSelect(CORREDORES,  product?.corredor || "",   "Corredor"),
    prateleira: mkSelect(PRATELEIRAS, product?.prateleira || "", "Prateleira"),
    posicao:    mkSelect(POSICOES,    product?.posicao || "",    "Posição"),
  };
  if (product?.observacoes) f.obs.value = product.observacoes;

  const errEl = el("div", { class: "error-text" });
  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "save" }), isEdit ? " Salvar alterações" : " Criar produto"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const card = el("div", { class: "modal modal-lg" }, [
    el("div", { class: "modal-header" }, [el("h3", { text: isEdit ? `Editar: ${product.nome}` : "Novo Produto" })]),
    el("div", { class: "product-modal-body" }, [
      el("div", { class: "modal-section" }, [
        el("h4", { class: "modal-section-title", text: "Identificação" }),
        field("Nome *", f.nome),
        field("Código (EAN / SKU / QR)", f.codigo),
        el("div", { class: "form-grid-2" }, [
          field("Lote", f.lote),
          field("Unidade de medida", f.unidade),
        ]),
        el("div", { class: "form-grid-2" }, [
          field("Qtd. por caixa", f.qty_caixa),
          field("Validade", f.validade),
        ]),
        field("Categoria", f.categoria),
        field("Observações", f.obs),
      ]),
      el("div", { class: "modal-section" }, [
        el("h4", { class: "modal-section-title", text: "Localização Física" }),
        el("div", { class: "form-grid-2" }, [
          field("Torre", f.torre),
          field("Corredor", f.corredor),
          field("Prateleira", f.prateleira),
          field("Posição", f.posicao),
        ]),
        field("Localização do sistema", f.localizacao),
      ]),
      errEl,
    ]),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const close = openBackdrop(card);
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const nome = f.nome.value.trim();
    if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      const payload = {
        nome,
        codigo:              f.codigo.value.trim() || undefined,
        quantidade_minima:   parseInt(f.qtd_min.value) || 0,
        categoria_id:        f.categoria.value || undefined,
        localizacao_id:      f.localizacao.value || undefined,
        unidade_medida:      f.unidade.value || undefined,
        quantidade_por_caixa: parseInt(f.qty_caixa.value) || undefined,
        lote:                f.lote.value.trim() || undefined,
        validade:            f.validade.value.trim() || undefined,
        observacoes:         f.obs.value.trim() || undefined,
      };
      if (isEdit) await API.updateProduct(depositId, product.id, payload);
      else        await API.createProduct(depositId, payload);
      notify(isEdit ? "Produto atualizado!" : "Produto criado!", "success");
      close();
      onSave?.();
    } catch (err) {
      errEl.textContent = err.message || "Erro ao salvar produto.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  setTimeout(() => f.nome.focus(), 80);
  return close;
}

// ── Modal de Visualização de Card (botão "Visualizar Card") ───────
// Abre o mesmo card que seria exibido após um escaneamento real.
// NÃO cria movimentações, NÃO altera dados.
export function openPreviewCard({ depositId, products = [], categories = [], onSave }) {
  // Use first product if available, otherwise show empty state
  const product = products[0] || null;
  const catMap  = Object.fromEntries(categories.map(c => [c.id, c.nome]));

  if (product) {
    _openFoundCard({ depositId, product, catMap, products, categories, onSave, isPreview: true });
  } else {
    // Show the "not found" quick registration card as preview
    _openNotFoundCard({ depositId, code: "EXEMPLO-001", categories, onSave, isPreview: true });
  }
}

// ── Modal pós-escaneamento ────────────────────────────────────────
// Chamado automaticamente ao escanear um código real.
export function openScanModal({ depositId, code, products = [], categories = [], locations = [], onSave }) {
  const found = products.find(p => p.codigo === code || p.code === code);
  const catMap = Object.fromEntries(categories.map(c => [c.id, c.nome]));
  if (found) {
    _openFoundCard({ depositId, product: found, catMap, products, categories, locations, onSave });
  } else {
    _openNotFoundCard({ depositId, code, categories, locations, onSave });
  }
}

// ── Card: produto encontrado ──────────────────────────────────────
function _openFoundCard({ depositId, product, catMap, products, categories, locations, onSave, isPreview = false }) {
  const qty = product.quantidade ?? product.quantity ?? "—";

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("span", { class: "badge badge-success", text: isPreview ? "Prévia do Card" : "Produto encontrado" }),
      el("h3", { text: product.nome || product.name }),
    ]),
    el("div", { class: "product-modal-body" }, [
      el("div", { class: "scan-info-grid" }, [
        infoRow("Código de barras", product.codigo || product.code || "—"),
        infoRow("Categoria",        catMap[product.categoria_id] || "—"),
        infoRow("Quantidade",       qty),
        infoRow("Unidade de medida", product.unidade_medida || "—"),
        infoRow("Lote",             product.lote || "—"),
        infoRow("Validade",          product.validade || "—"),
        infoRow("Localização",       product.localizacao_id || "—"),
        infoRow("Observações",       product.observacoes || "—"),
        infoRow("Data de cadastro",  product.criado_em ? product.criado_em.slice(0,10) : "—"),
      ]),
    ]),
    el("div", { class: "modal-actions" }, [
      el("button", { class: "btn btn-ghost", text: "Fechar", onclick: () => backdrop.remove() }),
      ...(isPreview ? [] : [
        el("button", { class: "btn btn-secondary", text: "Registrar Saída", onclick: () => {
          backdrop.remove();
          openExitModal({ depositId, product, products, onSave });
        }}),
        el("button", { class: "btn btn-primary", text: "Registrar Entrada", onclick: () => {
          backdrop.remove();
          openEntryModal({ depositId, product, products, locations, onSave });
        }}),
      ]),
    ]),
  ]);

  var backdrop;
  const close = () => backdrop.remove();
  backdrop = el("div", { class: "modal-backdrop" }, [card]);
  backdrop.addEventListener("click", e => { if (e.target === backdrop) close(); });
  document.body.appendChild(backdrop);
  renderIcons(backdrop);
}

// ── Card: produto NÃO encontrado (cadastro rápido) ────────────────
function _openNotFoundCard({ depositId, code, categories, locations, onSave, isPreview = false }) {
  const f = {
    nome:      el("input", { class: "input", placeholder: "Nome do produto *" }),
    codigo:    el("input", { class: "input", value: code, placeholder: "Código" }),
    categoria: mkSelect(categories, null, "Sem categoria"),
    unidade:   mkSelect(UNIDADES, "", "Unidade de medida"),
    lote:      el("input", { class: "input", placeholder: "Número do lote" }),
    qty_caixa: el("input", { class: "input", type: "number", min: "1", placeholder: "Qtd. por caixa" }),
    quantidade: el("input", { class: "input", type: "number", min: "0", value: "1", placeholder: "Quantidade inicial" }),
    validade:  el("input", { class: "input", placeholder: "Validade (MM/AAAA)" }),
    obs:       el("textarea", { class: "input", style: "height:56px;resize:vertical", placeholder: "Observações" }),
    torre:     mkSelect(TORRES,      "", "Torre"),
    corredor:  mkSelect(CORREDORES,  "", "Corredor"),
    prateleira:mkSelect(PRATELEIRAS, "", "Prateleira"),
    posicao:   mkSelect(POSICOES,    "", "Posição"),
  };

  // Pre-fill date/time
  const now = new Date();
  const dataEntrada = now.toLocaleDateString("pt-BR");
  const horaEntrada = now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

  const errEl = el("div", { class: "error-text" });
  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "plus" }), " Cadastrar e registrar entrada"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("span", { class: "badge badge-warning", text: isPreview ? "Prévia do Card" : "Produto não encontrado" }),
      el("h3", { text: "Cadastro Rápido" }),
      el("p", { class: "muted", style: "font-size:.83em;margin:2px 0 0" }, [
        `Código: ${code}  |  Data entrada: ${dataEntrada}  ${horaEntrada}`,
      ]),
    ]),
    el("div", { class: "product-modal-body" }, [
      field("Nome *", f.nome),
      el("div", { class: "form-grid-2" }, [
        field("Código de barras", f.codigo),
        field("Categoria", f.categoria),
      ]),
      el("div", { class: "form-grid-2" }, [
        field("Quantidade inicial", f.quantidade),
        field("Unidade de medida", f.unidade),
      ]),
      el("div", { class: "form-grid-2" }, [
        field("Lote", f.lote),
        field("Qtd. por caixa", f.qty_caixa),
      ]),
      el("div", { class: "form-grid-2" }, [
        field("Validade", f.validade),
      ]),
      el("div", { class: "modal-section" }, [
        el("h4", { class: "modal-section-title", text: "Localização" }),
        el("div", { class: "form-grid-2" }, [
          field("Torre", f.torre),
          field("Corredor", f.corredor),
          field("Prateleira", f.prateleira),
          field("Posição", f.posicao),
        ]),
      ]),
      field("Observações", f.obs),
      errEl,
    ]),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  var backdrop;
  const close = () => backdrop.remove();
  backdrop = el("div", { class: "modal-backdrop" }, [card]);
  backdrop.addEventListener("click", e => { if (e.target === backdrop) close(); });
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    if (isPreview) { close(); return; }
    const nome = f.nome.value.trim();
    if (!nome) { errEl.textContent = "Nome é obrigatório."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      const locNome = [
        f.torre.value ? f.torre.value : "",
        f.corredor.value ? "Corredor " + f.corredor.value : "",
        f.prateleira.value ? "Prateleira " + f.prateleira.value : "",
        f.posicao.value,
      ].filter(Boolean).join(" / ") || undefined;

      // 1. Create product
      const product = await API.createProduct(depositId, {
        nome,
        codigo:              f.codigo.value.trim() || undefined,
        categoria_id:        f.categoria.value || undefined,
        unidade_medida:      f.unidade.value || undefined,
        quantidade_por_caixa: parseInt(f.qty_caixa.value) || undefined,
        lote:                f.lote.value.trim() || undefined,
        validade:            f.validade.value.trim() || undefined,
        observacoes:         f.obs.value.trim() || undefined,
      });

      // 2. Register entry (if quantity > 0)
      const qty = parseInt(f.quantidade.value) || 0;
      if (qty > 0) {
        await API.stockEntry(depositId, {
          produto_id: product.id,
          quantidade: qty,
          observacao: `Cadastro rápido via escaneamento. ${f.obs.value.trim()}`.trim() || undefined,
        });
      }

      notify("Produto cadastrado e entrada registrada!", "success");
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
  setTimeout(() => f.nome.focus(), 80);
}

// ── Modal de Entrada ──────────────────────────────────────────────
export function openEntryModal({ depositId, product = null, products = [], locations = [], onSave }) {
  const productSelect = product ? null : mkSelect(
    products.map(p => ({ id: p.id || p.id, nome: `${p.nome || p.name} (${p.codigo || p.code || ""})` })),
    null, "Selecione o produto *"
  );

  const f = {
    qty:        el("input", { class: "input", type: "number", min: "1", value: "1", placeholder: "Quantidade recebida *" }),
    lote:       el("input", { class: "input", placeholder: "Número do lote" }),
    qty_caixa:  el("input", { class: "input", type: "number", min: "1", placeholder: "Qtd. por caixa" }),
    validade:   el("input", { class: "input", placeholder: "Validade (MM/AAAA)" }),
    obs:        el("input", { class: "input", placeholder: "Observação (opcional)" }),
    torre:      mkSelect(TORRES,      "", "Torre"),
    corredor:   mkSelect(CORREDORES,  "", "Corredor"),
    prateleira: mkSelect(PRATELEIRAS, "", "Prateleira"),
    posicao:    mkSelect(POSICOES,    "", "Posição"),
  };

  const errEl = el("div", { class: "error-text" });
  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "arrow-down-circle" }), " Registrar Entrada"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const bodyChildren = [];
  if (productSelect) bodyChildren.push(field("Produto *", productSelect));
  bodyChildren.push(
    el("div", { class: "form-grid-2" }, [
      field("Quantidade recebida *", f.qty),
      field("Lote", f.lote),
    ]),
    el("div", { class: "form-grid-2" }, [
      field("Qtd. por caixa", f.qty_caixa),
      field("Validade", f.validade),
    ]),
    el("div", { class: "modal-section" }, [
      el("h4", { class: "modal-section-title", text: "Localização" }),
      el("div", { class: "form-grid-2" }, [
        field("Torre", f.torre),
        field("Corredor", f.corredor),
        field("Prateleira", f.prateleira),
        field("Posição", f.posicao),
      ]),
    ]),
    field("Observação", f.obs),
    errEl,
  );

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("h3", { text: product ? `Entrada — ${product.nome || product.name}` : "Registrar Entrada" }),
    ]),
    el("div", { class: "product-modal-body" }, bodyChildren),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const close = openBackdrop(card);
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const productId = product?.id || productSelect?.value;
    const qty = parseInt(f.qty.value);
    if (!productId) { errEl.textContent = "Selecione um produto."; return; }
    if (!qty || qty < 1) { errEl.textContent = "Quantidade inválida."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      await API.stockEntry(depositId, {
        produto_id: productId,
        quantidade: qty,
        lote: f.lote.value.trim() || undefined,
        validade_lote: f.validade.value.trim() || undefined,
        observacao: f.obs.value.trim() || undefined,
      });

      // Update product fields if filled
      if (product?.id && (f.validade.value || f.qty_caixa.value || f.lote.value)) {
        await API.updateProduct(depositId, product.id, {
          lote: f.lote.value.trim() || undefined,
          validade: f.validade.value.trim() || undefined,
          quantidade_por_caixa: parseInt(f.qty_caixa.value) || undefined,
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

  return close;
}

// ── Modal de Saída ────────────────────────────────────────────────
export function openExitModal({ depositId, product = null, products = [], onSave }) {
  const productSelect = product ? null : mkSelect(
    products.map(p => ({ id: p.id, nome: `${p.nome || p.name} (${p.codigo || p.code || ""})` })),
    null, "Selecione o produto *"
  );

  const f = {
    qty:     el("input", { class: "input", type: "number", min: "1", value: "1", placeholder: "Quantidade retirada *" }),
    destino: el("input", { class: "input", placeholder: "Destino (ex: Sala 3, Professor João)" }),
    obs:     el("input", { class: "input", placeholder: "Observação (opcional)" }),
  };

  const errEl = el("div", { class: "error-text" });
  const saveBtn   = el("button", { class: "btn btn-primary" }, [el("i", { "data-lucide": "arrow-up-circle" }), " Registrar Saída"]);
  const cancelBtn = el("button", { class: "btn btn-ghost", text: "Cancelar" });

  const bodyChildren = [];
  if (productSelect) bodyChildren.push(field("Produto *", productSelect));
  bodyChildren.push(
    field("Quantidade retirada *", f.qty),
    field("Destino", f.destino),
    field("Observação", f.obs),
    errEl,
  );

  const card = el("div", { class: "modal" }, [
    el("div", { class: "modal-header" }, [
      el("h3", { text: product ? `Saída — ${product.nome || product.name}` : "Registrar Saída" }),
    ]),
    el("div", { class: "product-modal-body" }, bodyChildren),
    el("div", { class: "modal-actions" }, [cancelBtn, saveBtn]),
  ]);

  const close = openBackdrop(card);
  cancelBtn.addEventListener("click", close);

  saveBtn.addEventListener("click", async () => {
    const productId = product?.id || productSelect?.value;
    const qty = parseInt(f.qty.value);
    if (!productId) { errEl.textContent = "Selecione um produto."; return; }
    if (!qty || qty < 1) { errEl.textContent = "Quantidade inválida."; return; }
    errEl.textContent = "";
    saveBtn.disabled = true;
    try {
      await API.stockExit(depositId, {
        produto_id: productId,
        quantidade: qty,
        destino_texto: f.destino.value.trim() || undefined,
        observacao: f.obs.value.trim() || undefined,
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

  return close;
}

// ── openMovementModal (compat com inventory.js) ───────────────────
export function openMovementModal({ depositId, products = [], onSave, initialCode }) {
  const matched = initialCode ? products.find(p => p.code === initialCode || p.codigo === initialCode) : null;
  if (matched) {
    _openFoundCard({ depositId, product: matched, catMap: {}, products, categories: [], onSave });
  } else {
    openEntryModal({ depositId, products, onSave });
  }
}

// ── LocationDetailBadge (sem localStorage — usa dados do backend) ─
export function LocationDetailBadge(productId) {
  return null; // Localização exibida nos cards via API
}
