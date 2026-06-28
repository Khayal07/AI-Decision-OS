"use client";

import { useEffect } from "react";

import { createClient } from "@/lib/supabase/client";

/**
 * Ensures every visitor has a (anonymous) Supabase session so their decisions
 * can be saved and listed — no forced sign-up. Renders nothing.
 *
 * Requires anonymous sign-ins to be enabled in the Supabase project's Auth
 * settings, and NEXT_PUBLIC_SUPABASE_URL / _ANON_KEY to be set.
 */
export function AuthGate() {
  useEffect(() => {
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL) return;
    const supabase = createClient();
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) void supabase.auth.signInAnonymously();
    });
  }, []);

  return null;
}
