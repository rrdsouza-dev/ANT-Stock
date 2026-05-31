export function limparCodigo(codigo) {
  return String(codigo || "").replace(/[^\w-]/g, "").toUpperCase();
}

export function validarCodigoBarras(codigo) {
  const limpo = limparCodigo(codigo);
  return {
    valido: limpo.length >= 4 && limpo.length <= 80,
    codigo: limpo,
    mensagem: limpo.length < 4 ? "Informe ao menos 4 caracteres." : "Codigo valido.",
  };
}
