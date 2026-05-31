export const produtosMock = [
  { id: "1", codigo: "ANT-1001", nome: "Arroz tipo 1", categoria: "Alimentos", quantidade: 240, quantidade_minima: 80, status: "OK" },
  { id: "2", codigo: "ANT-2048", nome: "Kit Arduino", categoria: "Eletronicos", quantidade: 18, quantidade_minima: 20, status: "Baixo" },
  { id: "3", codigo: "ANT-3300", nome: "Tecido algodao", categoria: "Texteis", quantidade: 86, quantidade_minima: 30, status: "OK" },
  { id: "4", codigo: "ANT-4412", nome: "Caderno de picking", categoria: "Material Didatico", quantidade: 120, quantidade_minima: 45, status: "OK" },
];

export const movimentacoesMock = [
  { data: "2026-05-18", produto: "Arroz tipo 1", tipo: "Entrada", quantidade: 80, usuario: "Gestao", observacao: "Reposicao mensal" },
  { data: "2026-05-22", produto: "Kit Arduino", tipo: "Saida", quantidade: 6, usuario: "Professor", observacao: "Aula pratica" },
  { data: "2026-05-29", produto: "Tecido algodao", tipo: "Entrada", quantidade: 30, usuario: "Professor", observacao: "Simulacao de recebimento" },
];

export const pedidosMock = [
  { id: "#108981", data: "2026-05-28", itens: 12, status: "Aberto" },
  { id: "#108982", data: "2026-05-29", itens: 7, status: "Separado" },
  { id: "#108983", data: "2026-05-30", itens: 16, status: "Concluido" },
];
