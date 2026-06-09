export const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export const isEmail = (v) => emailRegex.test(String(v || "").trim());

export function passwordScore(pw) {
  let s = 0;
  if (!pw) return 0;
  if (pw.length >= 8) s++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) s++;
  if (/\d/.test(pw)) s++;
  if (/[^A-Za-z0-9]/.test(pw) && pw.length >= 10) s++;
  return s; // 0..4
}

export function validatePassword(pw) {
  if (!pw) return "Informe a senha.";
  if (pw.length < 8) return "A senha deve ter ao menos 8 caracteres.";
  if (!/[A-Z]/.test(pw)) return "Inclua ao menos uma letra maiúscula.";
  if (!/\d/.test(pw)) return "Inclua ao menos um número.";
  return null;
}

export function validateEmail(v) {
  if (!v) return "Informe seu e-mail.";
  if (!isEmail(v)) return "E-mail inválido.";
  return null;
}

export function required(v, label = "Campo") {
  if (!String(v ?? "").trim()) return `${label} é obrigatório.`;
  return null;
}

/* Common input masks */
export function maskPhone(v) {
  const d = String(v || "").replace(/\D/g, "").slice(0, 11);
  if (d.length <= 10) return d.replace(/(\d{0,2})(\d{0,4})(\d{0,4}).*/, (_, a, b, c) =>
    [a && `(${a}`, a && a.length === 2 ? ") " : "", b, c && `-${c}`].filter(Boolean).join(""));
  return d.replace(/(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
}