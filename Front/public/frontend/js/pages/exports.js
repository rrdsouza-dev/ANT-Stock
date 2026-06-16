import { el, renderIcons } from "../utils/helpers.js";
import { AppShell } from "./_shell.js";
import { API } from "../services/api.js";
import { session } from "../services/store.js";
import { exportExcel } from "../utils/exportExcel.js";
import { exportTxt } from "../utils/exportTxt.js";
import { notify } from "../components/notifications.js";
import { guardedClick } from "../utils/security.js";

export function ExportsPage(root, ctx) {
  AppShell(root, ctx.path, (content) => {
    const head = el("div", { class: "page-head" }, [
      el("div", {}, [
        el("h1", { text: "Exportações" }),
        el("p", { class: "muted", text: "Exporte os dados reais do sistema para uso externo." }),
      ]),
    ]);

    const grid = el("div", { class: "product-grid" });
    const statusMsg = el("div", { class: "muted", style: "padding:20px;text-align:center" }, ["Carregando dados..."]);
    grid.appendChild(statusMsg);

    content.append(head, grid);
    renderIcons(content);

    async function loadExports() {
      try {
        let depositId = session.depositId;
        if (!depositId) {
          const deposits = await API.deposits();
          if (!deposits || deposits.length === 0) {
            grid.innerHTML = "";
            grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Nenhum depósito vinculado ao usuário."]));
            return;
          }
          depositId = deposits[0].id;
          session.setDepositId(depositId);
        }

        const [products, movements, orders, categories, locations] = await Promise.all([
          API.products(depositId, { limite: 200 }).catch(() => []),
          API.movements(depositId, { limite: 200 }).catch(() => []),
          API.orders(depositId, { limite: 200 }).catch(() => []),
          API.categories(depositId, { limite: 200 }).catch(() => []),
          API.locations(depositId, { limite: 200 }).catch(() => []),
        ]);

        const dataSets = [
          {
            key: "produtos",
            label: "Estoque (produtos)",
            rows: products.map(p => ({
              id: p.id,
              nome: p.nome,
              codigo: p.codigo || "",
              quantidade_minima: p.quantidade_minima,
              ativo: p.ativo ? "Sim" : "Não",
              criado_em: p.criado_em ? p.criado_em.slice(0, 10) : "",
              atualizado_em: p.atualizado_em ? p.atualizado_em.slice(0, 10) : "",
            })),
          },
          {
            key: "movimentacoes",
            label: "Movimentações logísticas",
            rows: movements.map(m => ({
              id: m.id,
              tipo: m.tipo,
              produto_id: m.produto_id,
              quantidade: m.quantidade,
              observacao: m.observacao || "",
              movimentado_em: m.movimentado_em ? m.movimentado_em.slice(0, 10) : "",
            })),
          },
          {
            key: "pedidos",
            label: "Pedidos",
            rows: orders.map(o => ({
              id: o.id,
              status: o.status,
              observacao: o.observacao || "",
              criado_em: o.criado_em ? o.criado_em.slice(0, 10) : "",
            })),
          },
          {
            key: "categorias",
            label: "Categorias",
            rows: categories.map(c => ({
              id: c.id,
              nome: c.nome,
              descricao: c.descricao || "",
              ativo: c.ativo ? "Sim" : "Não",
            })),
          },
          {
            key: "localizacoes",
            label: "Localizações",
            rows: locations.map(l => ({
              id: l.id,
              nome: l.nome,
              corredor: l.corredor || "",
              prateleira: l.prateleira || "",
              posicao: l.posicao || "",
              ativo: l.ativo ? "Sim" : "Não",
            })),
          },
        ];

        grid.innerHTML = "";
        for (const ds of dataSets) {
          grid.appendChild(el("div", { class: "card card-pad" }, [
            el("h3", { text: ds.label }),
            el("p", { class: "muted", style: "margin:6px 0 16px", text: `${ds.rows.length} registro(s) disponíveis para exportação.` }),
            el("div", { style: "display:flex;gap:10px;flex-wrap:wrap" }, [
              el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
                exportTxt(ds.rows, `${ds.key}.txt`);
                notify("TXT exportado.", "success");
              }) }, [el("i", { "data-lucide": "file-text" }), "TXT"]),
              el("button", { class: "btn btn-primary", onclick: guardedClick(() => {
                exportExcel(ds.rows, `${ds.key}.xlsx`, ds.label);
                notify("Excel exportado.", "success");
              }) }, [el("i", { "data-lucide": "sheet" }), "Excel"]),
            ]),
          ]));
        }
        renderIcons(grid);
      } catch (err) {
        grid.innerHTML = "";
        grid.appendChild(el("div", { class: "muted", style: "padding:30px;text-align:center" }, ["Erro ao carregar dados para exportação."]));
        notify(err.message || "Erro ao carregar exportações.", "error");
      }
    }

    loadExports();
  });
}
