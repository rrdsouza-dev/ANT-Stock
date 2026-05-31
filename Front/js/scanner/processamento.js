import { limparCodigo, validarCodigoBarras } from "../validacoes/codigo-barras.js";

export function processarCodigo(valor) {
  const codigo = limparCodigo(valor);
  return validarCodigoBarras(codigo);
}
