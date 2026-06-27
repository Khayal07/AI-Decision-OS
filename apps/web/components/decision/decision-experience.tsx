"use client";

import { useState } from "react";

import { readSSE } from "@/lib/sse";
import type { AgentStatus, DecisionResult } from "@/lib/types";

import { DecisionDashboard } from "./decision-dashboard";
import { ThinkingTimeline } from "./thinking-timeline";

const EXAMPLES = [
  "MacBook Air or MacBook Pro?",
  "Should I rent or buy a house?",
  "Which framework should I learn?",
  "Which job offer should I accept?",
];

type Phase = "idle" | "running" | "done" | "error";

export function DecisionExperience() {
  const [value, setValue] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [statuses, setStatuses] = useState<AgentStatus[]>([]);
  const [result, setResult] = useState<DecisionResult | null>(null);
  const [error, setError] = useState("");

  const canSubmit = value.trim().length > 3 && phase !== "running";

  async function run() {
    setPhase("running");
    setStatuses([]);
    setResult(null);
    setError("");

    try {
      const res = await fetch("/api/decisions/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: value }),
      });
      if (!res.ok || !res.body) throw new Error("The analysis service is unavailable.");

      for await (const ev of readSSE(res)) {
        if (ev.event === "status") {
          setStatuses((prev) => [...prev, JSON.parse(ev.data) as AgentStatus]);
        } else if (ev.event === "result") {
          setResult(JSON.parse(ev.data) as DecisionResult);
        } else if (ev.event === "error") {
          setError((JSON.parse(ev.data) as { message?: string }).message ?? "Analysis failed.");
          setPhase("error");
          return;
        }
      }
      setPhase((prev) => (prev === "running" ? "done" : prev));
    } catch (err) {
      setError((err as Error).message);
      setPhase("error");
    }
  }

  function reset() {
    setPhase("idle");
    setValue("");
    setStatuses([]);
    setResult(null);
    setError("");
  }

  if (phase === "done" && result) {
    return <DecisionDashboard result={result} onReset={reset} />;
  }

  return (
    <div className="w-full">
      <div className="group relative rounded-2xl border border-border bg-card/60 p-2 shadow-2xl shadow-black/20 backdrop-blur transition focus-within:border-accent/60">
        <div className="flex items-center gap-2">
          <input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && canSubmit) run();
            }}
            disabled={phase === "running"}
            placeholder="Describe your decision…"
            aria-label="Describe your decision"
            className="w-full bg-transparent px-4 py-3.5 text-base text-foreground outline-none placeholder:text-muted-foreground disabled:opacity-60"
          />
          <button
            type="button"
            onClick={run}
            disabled={!canSubmit}
            className="shrink-0 rounded-xl bg-accent px-5 py-3 text-sm font-medium text-accent-foreground transition enabled:hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {phase === "running" ? "Analyzing…" : "Analyze"}
          </button>
        </div>
      </div>

      {phase === "idle" && (
        <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setValue(example)}
              className="rounded-full border border-border bg-muted/40 px-3.5 py-1.5 text-xs text-muted-foreground transition hover:border-accent/50 hover:text-foreground"
            >
              {example}
            </button>
          ))}
        </div>
      )}

      {phase === "running" && <ThinkingTimeline statuses={statuses} />}

      {phase === "error" && (
        <p className="mt-6 text-center text-sm text-muted-foreground">
          {error}{" "}
          <button type="button" onClick={reset} className="text-accent underline">
            try again
          </button>
        </p>
      )}
    </div>
  );
}
