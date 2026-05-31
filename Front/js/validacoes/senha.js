export function avaliarSenha(senha, email = "") {
  const regras = [
    senha.length >= 6,
    /[A-ZÀ-Ú]/.test(senha),
    /\d/.test(senha),
    senha.toLowerCase() !== String(email).toLowerCase(),
  ];
  const pontos = regras.filter(Boolean).length;
  return {
    valida: pontos === regras.length,
    pontos,
    mensagem: pontos === 4 ? "Senha forte" : "Use 6 caracteres, 1 maiuscula e 1 numero.",
  };
}
