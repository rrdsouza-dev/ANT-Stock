export function qs(seletor, raiz = document) {
  return raiz.querySelector(seletor);
}

export function qsa(seletor, raiz = document) {
  return [...raiz.querySelectorAll(seletor)];
}

export function navegar(rota) {
  window.location.hash = rota;
}

export function toast(mensagem) {
  const item = document.createElement("div");
  item.className = "toast fade-in";
  item.textContent = mensagem;
  document.body.appendChild(item);
  setTimeout(() => item.remove(), 3600);
}

export function formatarData(data) {
  return new Intl.DateTimeFormat("pt-BR").format(new Date(data));
}

export function dinheiroNumero(numero) {
  return new Intl.NumberFormat("pt-BR").format(numero);
}
