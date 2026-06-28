"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Item = {
  id: string;
  title: string | null;
  confidence: number | null;
  created_at: string;
  winner: string | null;
};

export default function HistoryPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/decisions")
      .then((r) => r.json())
      .then((d) => setItems(d.decisions ?? []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl px-6 py-20">
      <h1 className="mb-6 text-2xl font-semibold tracking-tight">Your decisions</h1>

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No decisions yet.{" "}
          <Link href="/" className="text-accent underline">
            Make one
          </Link>
          .
        </p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/history/${item.id}`}
                className="flex items-center justify-between rounded-xl border border-border bg-card/40 px-4 py-3 transition hover:border-accent/50"
              >
                <span className="truncate text-sm">
                  {item.title ?? "Untitled"}
                  {item.winner && <span className="text-muted-foreground"> · {item.winner}</span>}
                </span>
                {item.confidence != null && (
                  <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                    {Math.round(item.confidence)}%
                  </span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
