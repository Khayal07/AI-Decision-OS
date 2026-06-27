"use client";

import type { AgentStatus } from "@/lib/types";

const STEPS = [
  "Understanding the decision",
  "Scoring the options",
  "Gathering evidence",
  "Assessing risks",
  "Analyzing costs",
  "Checking fit & regret",
  "Weighing the verdict",
  "Verifying consistency",
  "Finalizing recommendation",
];

export function ThinkingTimeline({ statuses }: { statuses: AgentStatus[] }) {
  const done = new Set(statuses.map((s) => s.label));
  const currentIndex = STEPS.findIndex((s) => !done.has(s));

  return (
    <ol className="mx-auto mt-10 w-full max-w-md space-y-3 text-left">
      {STEPS.map((step, i) => {
        const isDone = done.has(step);
        const isCurrent = i === currentIndex;
        return (
          <li key={step} className="flex items-center gap-3">
            <span
              className={[
                "flex h-5 w-5 items-center justify-center rounded-full border text-[10px]",
                isDone
                  ? "border-accent bg-accent text-accent-foreground"
                  : isCurrent
                    ? "animate-pulse border-accent text-accent"
                    : "border-border text-muted-foreground",
              ].join(" ")}
            >
              {isDone ? "✓" : i + 1}
            </span>
            <span className={isDone || isCurrent ? "text-foreground" : "text-muted-foreground"}>
              {step}
              {isCurrent ? "…" : ""}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
