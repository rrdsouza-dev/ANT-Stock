import { login } from "./auth/auth.js";
import { normalizarCodigo, redefinirSenha, solicitarCodigo, validarCodigo } from "./auth/recuperar-senha.js";
import { DEPOSITOS } from "./config/config.js";
import { obterDeposito, obterUsuario, salvarDeposito } from "./core/storage.js";
import { qs, toast } from "./core/utils.js";
import { carregarEstoque } from "./features/estoque.js";
import { carregarMovimentacoes, ligarMovimentacaoNova } from "./features/movimentacoes.js";
import { carregarPedidos } from "./features/pedidos.js";
import { carregarPerfil } from "./features/perfil.js";
import { ligarProdutoNovo } from "./features/produto.js";
import { ligarNav, sidebar } from "./ui/nav.js";

const app = document.getElementById("app");
const recoveryImagePath = "./public/assets/images/recuperacao-senha.png";

function hero() {
  return `
    <section class="auth-card">
      <div class="hero-illustration">
        <div class="hero-scene">
          <div class="bubble bubble-left">▤<br><strong>Estoque</strong></div>
          <div class="bubble bubble-right">▦<br><strong>Picking</strong></div>
          <div class="person"><div class="heart">♡</div><div class="legs"></div></div>
          <div class="mini-card"><strong>ANT Stock -</strong><span class="muted">Picking</span><br><br><span class="status-pill">84%</span></div>
        </div>
        <div class="progress-dot"><span></span><span></span><span></span><span></span></div>
        <p class="hero-copy">Torne seu trabalho mais facil e organizado com o <strong>ANT Stock</strong></p>
      </div>
    </section>
  `;
}

function recoveryImage() {
  return `
    <section class="auth-card auth-image-card">
      <img class="auth-fixed-image" src="${recoveryImagePath}" alt="Recuperacao de senha ANT Stock" onerror="this.hidden=true; this.nextElementSibling.hidden=false;">
      <div class="auth-image-placeholder" hidden>
        Envie a imagem de recuperacao para<br>
        Front/public/assets/images/recuperacao-senha.png
      </div>
    </section>
  `;
}

function renderLogin() {
  app.innerHTML = `
    <main class="auth-page fade-in">
      <section class="auth-panel">
        <div class="logo"><span class="logo-mark"><span></span></span><span>ANT<br>Stock</span></div>
        <form class="auth-form" id="login-form">
          <h1>Bem-vindo de volta!</h1>
          <p>Simplifique sua gestao de estoque e impulsione a produtividade da turma de logistica com o ANT Stock.</p>
          <input class="field" name="email" type="email" placeholder="Email" autocomplete="email" required>
          <div class="password-wrap">
            <input class="field" id="senha" name="senha" type="password" placeholder="Senha" autocomplete="current-password" required>
            <button class="icon-btn" id="toggle-senha" type="button" title="Mostrar senha">◌</button>
          </div>
          <a class="auth-link" href="#/recuperar-senha">Esqueceu a senha?</a>
          <button class="btn btn-primary" type="submit">Entrar</button>
        </form>
      </section>
      ${hero()}
    </main>
  `;
  qs("#toggle-senha").addEventListener("click", () => {
    const senha = qs("#senha");
    senha.type = senha.type === "password" ? "text" : "password";
  });
  qs("#login-form").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const dados = Object.fromEntries(new FormData(evento.currentTarget));
    try {
      await login(dados.email, dados.senha);
    } catch (erro) {
      toast(erro.message);
    }
  });
}

function renderRecuperarSenha() {
  app.innerHTML = `
    <main class="auth-page fade-in">
      <section class="auth-panel">
        <div class="logo"><span class="logo-mark"><span></span></span><span>ANT<br>Stock</span></div>
        <form class="auth-form step-card" id="reset-form">
          <span class="minimal-detail" aria-hidden="true"></span>
          <h1>Esqueceu sua senha?</h1>
          <p>Informe o email cadastrado para receber um codigo seguro de recuperacao.</p>
          <input class="field" name="email" type="email" placeholder="Email" required>
          <span class="form-helper">Use o email de professor ou gestao vinculado ao ANT Stock.</span>
          <button class="btn btn-primary" type="submit">Enviar codigo</button>
          <a class="auth-link" href="#/login">Voltar ao login</a>
        </form>
      </section>
      ${recoveryImage()}
    </main>
  `;
  qs("#reset-form").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const dados = Object.fromEntries(new FormData(evento.currentTarget));
    try {
      await solicitarCodigo(dados.email);
    } catch (erro) {
      toast(erro.message);
    }
  });
}

function renderValidarCodigo() {
  const email = sessionStorage.getItem("ant_reset_email") || "";
  app.innerHTML = `
    <main class="auth-page auth-page-centered fade-in">
      <form class="auth-form step-card" id="codigo-form">
        <span class="minimal-detail" aria-hidden="true"></span>
        <h1>Codigo de recuperacao</h1>
        <p>Digite os 6 numeros enviados para ${email || "seu email"}.</p>
        <input class="field recovery-code" id="codigo-recuperacao" name="codigo" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" placeholder="000000" required>
        <span class="form-helper" id="codigo-helper">Apenas numeros. O codigo expira em 15 minutos.</span>
        <button class="btn btn-primary" type="submit">Continuar</button>
        <a class="auth-link" href="#/recuperar-senha">Enviar outro codigo</a>
      </form>
    </main>
  `;
  const campo = qs("#codigo-recuperacao");
  campo.addEventListener("input", () => {
    campo.value = normalizarCodigo(campo.value);
  });
  campo.addEventListener("beforeinput", (evento) => {
    if (evento.data && /\D/.test(evento.data)) {
      evento.preventDefault();
    }
    if (evento.data && campo.value.length >= 6 && campo.selectionStart === campo.selectionEnd) {
      evento.preventDefault();
    }
  });
  qs("#codigo-form").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try {
      await validarCodigo(email, campo.value);
    } catch (erro) {
      toast(erro.message);
    }
  });
}

function renderNovaSenha() {
  const email = sessionStorage.getItem("ant_reset_email") || "";
  const codigo = sessionStorage.getItem("ant_reset_codigo") || "";
  app.innerHTML = `
    <main class="auth-page fade-in">
      <section class="auth-panel">
        <form class="auth-form step-card" id="nova-senha-form">
          <span class="minimal-detail" aria-hidden="true"></span>
          <h1>Nova senha</h1>
          <p>Crie uma senha forte para proteger o acesso ao estoque.</p>
          <input class="field" name="senha" type="password" placeholder="Nova senha" required>
          <input class="field" name="confirmar" type="password" placeholder="Confirmar senha" required>
          <div class="strength"><span id="strength-bar"></span></div>
          <button class="btn btn-primary" type="submit">Redefinir senha</button>
        </form>
      </section>
      ${recoveryImage()}
    </main>
  `;
  qs("#nova-senha-form").addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const dados = Object.fromEntries(new FormData(evento.currentTarget));
    if (dados.senha !== dados.confirmar) {
      toast("As senhas nao conferem.");
      return;
    }
    try {
      await redefinirSenha(email, codigo, dados.senha);
    } catch (erro) {
      toast(erro.message);
    }
  });
}

function shell(rota, conteudo) {
  app.innerHTML = `
    <main class="app-shell fade-in">
      ${sidebar(rota)}
      <section class="main">
        <header class="topbar">
          <div class="search"><input type="search" placeholder="Buscar produtos ou turmas"></div>
          <div class="top-actions">
            <button class="icon-btn" title="Notificacoes">♧</button>
            <div class="avatar" title="Usuario"></div>
            <button class="icon-btn" id="logout-top" title="Sair">↪</button>
          </div>
        </header>
        ${conteudo}
      </section>
    </main>
  `;
  ligarNav();
  qs("#logout-top")?.addEventListener("click", () => qs("#logout")?.click());
}

function dashboard(titulo, professor = false) {
  const usuario = obterUsuario();
  if (!obterDeposito()) salvarDeposito(professor ? DEPOSITOS.turma2 : DEPOSITOS.gestao);
  shell(professor ? "dashboard-professor" : "dashboard-gestao", `
    <div class="page-head">
      <div>
        <h1>${titulo}</h1>
        <p class="muted">Olá, ${usuario?.nome || usuario?.email || "usuario"}. Acompanhe os indicadores principais.</p>
      </div>
      ${professor ? `<div class="tabs"><button class="active">2º Ano</button><button>3º Ano</button></div>` : ""}
    </div>
    <section class="grid grid-3">
      <article class="card metric"><span class="muted">Produtos ativos</span><strong>128</strong><span class="status-pill">+12 este mes</span></article>
      <article class="card metric"><span class="muted">Movimentacoes</span><strong>342</strong><span class="status-pill">Estavel</span></article>
      <article class="card metric"><span class="muted">Estoque baixo</span><strong>9</strong><span class="status-pill">Revisar</span></article>
    </section>
    <section class="grid grid-2" style="margin-top: 22px">
      <article class="card"><h2>Distribuicao de Estoque por Categoria</h2><div class="chart-pie"></div><p class="muted">Eletronicos · Material Didatico · Moveis</p></article>
      <article class="card"><h2>Eficiencia Picking por Turma</h2><div class="bars">${[70, 62, 76, 54, 64, 78, 72].map((h) => `<span class="bar" style="height:${h}%"></span>`).join("")}</div></article>
    </section>
  `);
}

function renderEstoque() {
  shell("estoque", `
    <div class="page-head"><h1>Estoque</h1><a class="btn btn-primary" href="#/produto-novo">+ Novo Produto</a></div>
    <div class="filters"><button class="filter-chip">Categoria</button><button class="filter-chip">Status</button><button class="filter-chip">Codigo</button></div>
    <article class="card table-card">
      <div class="table-head"><h2>Produtos</h2><button class="icon-btn">⌕</button></div>
      <table><thead><tr><th>Codigo</th><th>Nome</th><th>Categoria</th><th>Quantidade</th><th>Minimo</th><th>Status</th><th>Acoes</th></tr></thead><tbody id="produtos-tbody"></tbody></table>
    </article>
  `);
  carregarEstoque();
}

function renderProdutoNovo() {
  shell("estoque", `
    <div class="page-head"><h1>Novo Produto</h1><a class="btn btn-secondary" href="#/estoque">Cancelar</a></div>
    <form class="card form-grid" id="produto-form">
      <label class="wide scanner-box">Codigo de barras
        <input class="field field-box" id="codigo" name="codigo" placeholder="Digite ou escaneie o codigo" required>
        <button class="btn btn-secondary" id="validar-codigo" type="button">Validar codigo</button>
      </label>
      <label>Nome<input class="field field-box" name="nome" required></label>
      <label>Categoria<select class="field field-box" name="categoria_id"><option value="">Sem categoria</option></select></label>
      <label>Quantidade minima<input class="field field-box" name="quantidade_minima" type="number" min="0" value="0"></label>
      <label>Localizacao<input class="field field-box" name="localizacao" placeholder="A1, Prateleira 2"></label>
      <button class="btn btn-primary wide" type="submit">Salvar</button>
    </form>
  `);
  ligarProdutoNovo();
}

function renderMovimentacoes() {
  shell("movimentacoes", `
    <div class="page-head"><h1>Movimentacoes</h1><a class="btn btn-primary" href="#/movimentacao-nova">+ Nova Movimentacao</a></div>
    <article class="card table-card">
      <table><thead><tr><th>Data</th><th>Produto</th><th>Tipo</th><th>Quantidade</th><th>Usuario</th><th>Observacao</th></tr></thead><tbody id="movimentacoes-tbody"></tbody></table>
    </article>
  `);
  carregarMovimentacoes();
}

function renderMovimentacaoNova() {
  shell("movimentacoes", `
    <div class="page-head"><h1>Nova Movimentacao</h1><a class="btn btn-secondary" href="#/movimentacoes">Cancelar</a></div>
    <form class="card form-grid" id="movimentacao-form">
      <label class="wide scanner-box">Codigo do produto<input class="field field-box" name="codigo" required><div class="camera-preview">Camera pronta para scanner</div></label>
      <label>Tipo<select class="field field-box" name="tipo"><option value="entrada">Entrada</option><option value="saida">Saida</option></select></label>
      <label>Quantidade<input class="field field-box" name="quantidade" type="number" min="1" required></label>
      <label class="wide">Observacao<textarea class="field field-box" name="observacao"></textarea></label>
      <button class="btn btn-primary wide" type="submit">Registrar</button>
    </form>
  `);
  ligarMovimentacaoNova();
}

function renderPedidos() {
  shell("pedidos", `
    <div class="page-head"><h1>Pedidos</h1><button class="btn btn-primary">+ Novo Pedido</button></div>
    <article class="card table-card"><table><thead><tr><th>ID</th><th>Data</th><th>Itens</th><th>Status</th><th>Acoes</th></tr></thead><tbody id="pedidos-tbody"></tbody></table></article>
  `);
  carregarPedidos();
}

function renderRelatorios() {
  shell("relatorios", `
    <div class="page-head"><h1>Relatorios Logisticos</h1><div><button class="btn btn-primary">Exportar PDF</button> <button class="btn btn-primary">Exportar Excel</button></div></div>
    <div class="filters"><button class="filter-chip">Data/10s</button><button class="filter-chip">Categoria</button><button class="filter-chip">#108981</button></div>
    <section class="grid grid-2"><article class="card"><h2>Distribuicao de Estoque por Categoria</h2><div class="chart-pie"></div></article><article class="card"><h2>Eficiencia Picking por Turma</h2><div class="bars">${[70, 62, 76, 54, 64, 78, 72].map((h) => `<span class="bar" style="height:${h}%"></span>`).join("")}</div></article></section>
    <article class="card table-card"><div class="table-head"><h2>Relatorios Recentes</h2></div><table><thead><tr><th>Tipo</th><th>Periodo</th><th>Status</th><th>Acoes</th></tr></thead><tbody><tr><td>Estoque Minimo - Turma Logistica</td><td>01/05/2026 - 31/05/2026</td><td><span class="status-pill">Concluido</span></td><td><button class="btn btn-secondary">Visualizar</button></td></tr></tbody></table></article>
  `);
}

function renderPerfil() {
  shell("perfil", `
    <div class="page-head"><h1>Perfil</h1></div>
    <form class="card form-grid" id="perfil-form">
      <label>Nome<input class="field field-box" id="perfil-nome" name="nome"></label>
      <label>Email<input class="field field-box" id="perfil-email" readonly></label>
      <label>Perfil<input class="field field-box" id="perfil-tipo" readonly></label>
      <label>Nova senha<input class="field field-box" name="senha" type="password"></label>
      <button class="btn btn-primary wide" type="submit">Salvar</button>
    </form>
  `);
  carregarPerfil();
}

export function router() {
  const rota = (window.location.hash.replace("#/", "") || "login").split("?")[0];
  const publicas = ["login", "recuperar-senha", "validar-codigo", "nova-senha"];
  if (!publicas.includes(rota) && !obterUsuario()) {
    renderLogin();
    return;
  }
  const rotas = {
    login: renderLogin,
    "recuperar-senha": renderRecuperarSenha,
    "validar-codigo": renderValidarCodigo,
    "nova-senha": renderNovaSenha,
    "dashboard-gestao": () => dashboard("Dashboard Gestao"),
    "dashboard-professor": () => dashboard("Dashboard Professor", true),
    estoque: renderEstoque,
    "produto-novo": renderProdutoNovo,
    movimentacoes: renderMovimentacoes,
    "movimentacao-nova": renderMovimentacaoNova,
    pedidos: renderPedidos,
    relatorios: renderRelatorios,
    perfil: renderPerfil,
  };
  (rotas[rota] || renderLogin)();
}
