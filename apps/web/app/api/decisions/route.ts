// Persist and list decisions for the current (possibly anonymous) user.
// Uses the user's Supabase session, so RLS scopes everything to them.

import { createClient } from "@/lib/supabase/server";
import type { DecisionResult } from "@/lib/types";

export const runtime = "nodejs";

export async function POST(req: Request): Promise<Response> {
  const body = (await req.json()) as { result?: DecisionResult; raw_input?: string };
  const result = body.result;
  if (!result) return Response.json({ error: "result required" }, { status: 400 });

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return Response.json({ error: "not authenticated" }, { status: 401 });

  const { data, error } = await supabase
    .from("decisions")
    .insert({
      user_id: user.id,
      title: result.title,
      raw_input: body.raw_input ?? result.title,
      decision_type: result.decision_type,
      status: "done",
      confidence: result.confidence,
      result_json: result,
    })
    .select("id")
    .single();

  if (error) return Response.json({ error: error.message }, { status: 500 });
  return Response.json({ id: data.id });
}

export async function GET(): Promise<Response> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("decisions")
    .select("id,title,confidence,created_at,winner:result_json->>winner")
    .order("created_at", { ascending: false })
    .limit(50);

  if (error) return Response.json({ error: error.message }, { status: 500 });
  return Response.json({ decisions: data ?? [] });
}
