/**
 * Front-end security helpers. These simulate protections that will be
 * mirrored on the FastAPI backend later.
 */

const KEY = "antstock:security";

const read = () => {
  try { return JSON.parse(localStorage.getItem(KEY) || "{}"); }
  catch { return {}; }
};
const write = (v) => localStorage.setItem(KEY, JSON.stringify(v));

/** Debounce wrapper that also disables the button while running. */
export function guardedClick(fn, { cooldown = 800 } = {}) {
  let busy = false;
  return async (e) => {
    if (busy) { e?.preventDefault?.(); return; }
    busy = true;
    const btn = e?.currentTarget;
    if (btn) btn.setAttribute("disabled", "");
    try {
      await fn(e);
    } finally {
      setTimeout(() => {
        busy = false;
        if (btn) btn.removeAttribute("disabled");
      }, cooldown);
    }
  };
}

/** Login attempt rate limit: 5 attempts / 60s, then 60s lockout. */
export function loginAttempt() {
  const s = read();
  const now = Date.now();
  const arr = (s.attempts || []).filter((t) => now - t < 60_000);
  if (s.lockUntil && now < s.lockUntil) {
    return { ok: false, remaining: 0, lockSec: Math.ceil((s.lockUntil - now) / 1000) };
  }
  arr.push(now);
  if (arr.length >= 5) {
    s.lockUntil = now + 60_000;
    s.attempts = [];
    write(s);
    return { ok: false, remaining: 0, lockSec: 60 };
  }
  s.attempts = arr;
  write(s);
  return { ok: true, remaining: 5 - arr.length, lockSec: 0 };
}

export function clearLoginAttempts() {
  const s = read(); s.attempts = []; s.lockUntil = 0; write(s);
}

/** Throttle a request (e.g. resend code) to once per `seconds`. */
export function canRequest(name, seconds = 30) {
  const s = read();
  const map = s.timers || {};
  const now = Date.now();
  if (map[name] && now < map[name]) return { ok: false, wait: Math.ceil((map[name] - now) / 1000) };
  map[name] = now + seconds * 1000;
  s.timers = map;
  write(s);
  return { ok: true };
}

/** Best-effort XSS guard for user-provided strings before rendering. */
export function sanitize(str) {
  return String(str ?? "").replace(/[<>]/g, "");
}