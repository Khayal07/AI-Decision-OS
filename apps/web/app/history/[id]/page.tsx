"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DecisionDashboard } from "@/components/decision/decision-dashboard";
import type { DecisionResult } from "@/lib/types";

export default function SavedDecisionPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [result, setResult] = useState<DecisionResult | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    fetch(`/api/decisions/${id}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setResult(d.result as DecisionResult))
      .catch(() => setMissing(true));
  }, [id]);

  if (missing) {
    return (
      <main className="mx-auto min-h-screen max-w-2xl px-6 py-20 text-sm text-muted-foreground">
        Decision not found.
      </main>
    );
  }

  if (!result) {
    return (
      <main className="mx-auto min-h-screen max-w-2xl px-6 py-20 text-sm text-muted-foreground">
        Loading…
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-16">
      <DecisionDashboard result={result} onReset={() => router.push("/")} />
    </main>
  );
}
