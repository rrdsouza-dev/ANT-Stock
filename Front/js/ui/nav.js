import { logout } from "../auth/auth.js";
import { obterUsuario } from "../core/storage.js";

const itensGestao = [
  ["dashboard-gestao", "⌂", "Dashboard"],
  ["estoque", "□", "Estoque"],
  ["movimentacoes", "↕", "Entradas/Saidas"],
  ["relatorios", "▣", "Relatorios"],
  ["perfil", "◉", "Perfil"],
];

const itensProfessor = [
  ["dashboard-professor", "⌂", "Dashboard"],
  ["estoque", "□", "Estoque"],
  ["movimentacoes", "↕", "Entradas/Saidas"],
  ["pedidos", "☑", "Pedidos"],
  ["perfil", "◉", "Perfil"],
];

export function sidebar(rotaAtual) {
  const usuario = obterUsuario();
  const itens = usuario?.perfil === "gestao" ? itensGestao : itensProfessor;
  return `
    <aside class="sidebar">
      <div class="logo"><span class="logo-mark"><span></span></span><span>ANT<br>Stock</span></div>
      <nav class="nav">
        ${itens.map(([rota, icone, label]) => `
          <a class="${rotaAtual === rota ? "active" : ""}" href="#/${rota}"><span>${icone}</span>${label}</a>
        `).join("")}
      </nav>
      <div class="sidebar-footer nav">
        <button type="button"><span>?</span>Suporte</button>
        <button type="button" id="logout"><span>↪</span>Log Out</button>
      </div>
    </aside>
  `;
}

export function ligarNav() {
  document.getElementById("logout")?.addEventListener("click", logout);
}
