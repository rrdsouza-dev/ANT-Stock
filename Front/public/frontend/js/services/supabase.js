/**
 * Supabase client placeholder. When integration time comes:
 *
 *   import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
 *   export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
 *
 * Until then we expose a no-op stub so pages can import it safely.
 */

export const supabase = {
  configured: false,
  auth: {
    async signInWithPassword() { throw new Error("Supabase not configured (frontend only)."); },
    async signUp() { throw new Error("Supabase not configured (frontend only)."); },
    async signOut() { return { error: null }; },
    onAuthStateChange() { return { data: { subscription: { unsubscribe() {} } } }; },
  },
  from() {
    return {
      select: async () => ({ data: [], error: null }),
      insert: async () => ({ data: null, error: null }),
      update: async () => ({ data: null, error: null }),
      delete: async () => ({ data: null, error: null }),
    };
  },
};