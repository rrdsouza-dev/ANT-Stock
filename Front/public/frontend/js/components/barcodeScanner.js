/**
 * FASE 3 — Leitor de código de barras USB (modo teclado).
 *
 * Leitores USB se comportam como teclado: digitam o código e pressionam Enter.
 * Implementamos:
 *  - Campo com foco automático
 *  - Captura via "keydown" global (modo background) ou campo visível
 *  - Debounce para filtrar digitação humana vs. leitura rápida do scanner
 *  - Callback com o código lido
 *  - Histórico de leituras (via LocalDB)
 */

import { el, renderIcons } from "../utils/helpers.js";
import { notify } from "./notifications.js";
import { LocalDB } from "../services/localInventoryStore.js";

const SCANNER_MIN_SPEED_MS = 60;   // tempo máximo entre chars de um scanner
const SCANNER_MIN_LEN = 3;         // tamanho mínimo para considerar código válido

/**
 * Cria um widget de leitura de código de barras.
 *
 * @param {function} onScan - callback({ code }) chamado quando código é lido
 * @param {object}   opts
 *   opts.autoFocus  {boolean} foca o campo ao montar (default true)
 *   opts.background {boolean} captura globalmente sem campo visível (default false)
 *   opts.label      {string}  texto do campo
 */
export function BarcodeScanner({ onScan, autoFocus = true, background = false, label = "Código de barras / QR" } = {}) {
  let buffer = "";
  let lastKeyTime = 0;

  // ── Campo visível ──────────────────────────────────────────
  const input = el("input", {
    class: "input barcode-input",
    placeholder: "Escaneie ou digite o código…",
    autocomplete: "off",
    spellcheck: "false",
  });

  const statusEl = el("div", { class: "barcode-status muted", text: "Aguardando leitura…" });
  const historyList = el("ul", { class: "barcode-history-list" });

  // ── Sample codes for simulation ──────────────────────────────
  const SAMPLE_CODES = ["7891234567890", "7898765432100", "7890001122334", "SIM-TEST-001", "SIM-TEST-002"];
  let simIdx = 0;

  const simBtn = el("button", {
    type: "button",
    class: "btn btn-soft btn-simulate",
    title: "Simular escaneamento (para testes sem leitor físico)",
  }, [
    el("i", { "data-lucide": "scan-line" }),
    " Simular Escaneamento",
  ]);

  simBtn.addEventListener("click", () => {
    const code = SAMPLE_CODES[simIdx % SAMPLE_CODES.length];
    simIdx++;
    input.value = code;
    handleCode(code);
  });

  const wrapper = el("div", { class: "barcode-scanner-widget" }, [
    el("label", { class: "field-label", text: label }),
    el("div", { class: "barcode-row" }, [
      el("div", { class: "barcode-icon" }, [el("i", { "data-lucide": "scan-barcode" })]),
      input,
      el("button", {
        class: "btn btn-soft",
        title: "Limpar",
        onclick: () => { input.value = ""; input.focus(); statusEl.textContent = "Aguardando leitura…"; },
      }, [el("i", { "data-lucide": "x" })]),
    ]),
    el("div", { class: "barcode-simulate-row" }, [simBtn]),
    statusEl,
    el("div", { class: "barcode-history" }, [
      el("div", { class: "barcode-history-title muted", text: "Últimas leituras" }),
      historyList,
    ]),
  ]);

  renderIcons(wrapper);

  // Load history
  function refreshHistory() {
    const history = LocalDB.barcodeHistory.list()
      .sort((a, b) => b.timestamp.localeCompare(a.timestamp))
      .slice(0, 6);
    historyList.innerHTML = "";
    if (history.length === 0) {
      historyList.appendChild(el("li", { class: "muted", style: "padding:6px 0;font-size:0.82em" }, ["Nenhuma leitura ainda."]));
      return;
    }
    for (const h of history) {
      const li = el("li", { class: "barcode-history-item" + (h.found ? "" : " not-found") }, [
        el("span", { class: "barcode-code", text: h.code }),
        el("span", { class: "barcode-product", text: h.found ? h.productName : "Não encontrado" }),
        el("span", { class: "barcode-time muted", text: h.timestamp.slice(11, 19) }),
      ]);
      historyList.appendChild(li);
    }
  }

  refreshHistory();

  // ── Core scan handler ──────────────────────────────────────
  function handleCode(code) {
    code = code.trim();
    if (code.length < SCANNER_MIN_LEN) return;

    statusEl.textContent = `Lido: ${code}`;
    statusEl.className = "barcode-status scanning";

    onScan?.({ code, refresh: refreshHistory });

    input.value = "";
    setTimeout(() => {
      statusEl.className = "barcode-status muted";
      statusEl.textContent = "Aguardando leitura…";
    }, 2000);
  }

  // ── Visible input handler (Enter submits) ──────────────────
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleCode(input.value);
    }
  });

  // ── Background global capture (scanner speed detection) ───
  if (background) {
    let globalBuffer = "";
    let globalTimer = null;
    document.addEventListener("keydown", (e) => {
      // Ignore if focus is on a different input
      if (document.activeElement !== document.body && document.activeElement !== wrapper) return;
      const now = Date.now();
      if (now - lastKeyTime > 300) globalBuffer = "";
      lastKeyTime = now;
      if (e.key === "Enter") {
        if (globalBuffer.length >= SCANNER_MIN_LEN) handleCode(globalBuffer);
        globalBuffer = "";
        return;
      }
      if (e.key.length === 1) globalBuffer += e.key;
      clearTimeout(globalTimer);
      globalTimer = setTimeout(() => {
        if (globalBuffer.length >= SCANNER_MIN_LEN) {
          // Only auto-submit if typed fast (scanner) not slow (human)
        }
        globalBuffer = "";
      }, 150);
    });
  }

  if (autoFocus) setTimeout(() => input.focus(), 80);

  return { node: wrapper, input, refreshHistory };
}
