import { createClient } from "@/lib/supabase/server";

export const runtime = "nodejs";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<Response> {
  const { id } = await params;
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("decisions")
    .select("result_json")
    .eq("id", id)
    .single();

  if (error || !data?.result_json) {
    return Response.json({ error: "not found" }, { status: 404 });
  }
  return Response.json({ result: data.result_json });
}
