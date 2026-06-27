// BFF proxy for clarifying questions (non-streaming JSON).

export const runtime = "nodejs";

export async function POST(req: Request): Promise<Response> {
  const { query } = (await req.json()) as { query?: string };

  if (!query || query.trim().length === 0) {
    return new Response(JSON.stringify({ questions: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  const baseUrl = process.env.AI_SERVICE_URL ?? "http://localhost:8000";
  const token = process.env.AI_SERVICE_TOKEN ?? "dev-internal-token";

  try {
    const upstream = await fetch(`${baseUrl}/clarify`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Service-Token": token },
      body: JSON.stringify({ query }),
    });
    if (!upstream.ok) throw new Error("clarify failed");
    return new Response(await upstream.text(), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    // Clarification is best-effort: fall back to no questions.
    return new Response(JSON.stringify({ questions: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
}
