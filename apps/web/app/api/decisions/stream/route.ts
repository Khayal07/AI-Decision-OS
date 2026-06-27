// BFF proxy: forwards a decision query to the AI service and streams the
// Server-Sent Events back to the browser. The service token never leaves the server.

export const runtime = "nodejs";

export async function POST(req: Request): Promise<Response> {
  const { query } = (await req.json()) as { query?: string };

  if (!query || query.trim().length === 0) {
    return new Response(JSON.stringify({ error: "query is required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const baseUrl = process.env.AI_SERVICE_URL ?? "http://localhost:8000";
  const token = process.env.AI_SERVICE_TOKEN ?? "dev-internal-token";

  const upstream = await fetch(`${baseUrl}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Service-Token": token,
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ query }),
  });

  if (!upstream.ok || !upstream.body) {
    return new Response(JSON.stringify({ error: "ai service error" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
