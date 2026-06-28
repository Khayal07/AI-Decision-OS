// Minimal Server-Sent Events reader over a fetch response stream.

export type SSEvent = { event: string; data: string };

export async function* readSSE(response: Response): AsyncGenerator<SSEvent> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    // Normalize CRLF → LF so events split reliably regardless of server style.
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");

    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";

    for (const chunk of chunks) {
      let event = "message";
      let data = "";
      for (const line of chunk.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (data) yield { event, data };
    }
  }
}
