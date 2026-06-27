"use client";

import { useState } from "react";

const EXAMPLES = [
  "MacBook Air or MacBook Pro?",
  "Should I rent or buy a house?",
  "Which framework should I learn?",
  "Which job offer should I accept?",
];

/**
 * The single-input decision capture.
 * Phase 0: visual + interactive shell only. The analyze flow is wired in Phase 1
 * (POST /api/decisions → SSE stream → dashboard).
 */
export function DecisionInput() {
  const [value, setValue] = useState("");
  const canSubmit = value.trim().length > 3;

  return (
    <div className="w-full">
      <div className="group relative rounded-2xl border border-border bg-card/60 p-2 shadow-2xl shadow-black/20 backdrop-blur transition focus-within:border-accent/60">
        <div className="flex items-center gap-2">
          <input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Describe your decision…"
            aria-label="Describe your decision"
            className="w-full bg-transparent px-4 py-3.5 text-base text-foreground outline-none placeholder:text-muted-foreground"
          />
          <button
            type="button"
            disabled={!canSubmit}
            className="shrink-0 rounded-xl bg-accent px-5 py-3 text-sm font-medium text-accent-foreground transition enabled:hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Analyze
          </button>
        </div>
      </div>

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
    </div>
  );
}
