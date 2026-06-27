"use client";

import type { DecisionResult, OptionResult } from "@/lib/types";

export function DecisionDashboard({
  result,
  onReset,
}: {
  result: DecisionResult;
  onReset: () => void;
}) {
  const winner = result.options.find((o) => o.is_winner) ?? result.options[0];

  return (
    <div className="mx-auto w-full max-w-3xl text-left">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-lg font-medium text-muted-foreground">{result.title}</h2>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground transition hover:text-foreground"
        >
          New decision
        </button>
      </div>

      {/* Winner */}
      <div className="rounded-2xl border border-accent/40 bg-card/60 p-6 shadow-xl shadow-black/20">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-accent">Recommended</p>
            <p className="mt-1 text-2xl font-semibold">{winner.name}</p>
          </div>
          <ConfidenceMeter value={result.confidence} />
        </div>
        <p className="mt-4 text-pretty text-sm text-muted-foreground">{result.recommendation}</p>
      </div>

      {/* Scores */}
      <section className="mt-6">
        <h3 className="mb-3 text-sm font-medium">Comparison</h3>
        <div className="space-y-3">
          {result.options.map((option) => (
            <ScoreBar key={option.name} option={option} />
          ))}
        </div>
      </section>

      {/* Pros & cons */}
      <section className="mt-6 grid gap-4 sm:grid-cols-2">
        {result.options.map((option) => (
          <div key={option.name} className="rounded-xl border border-border bg-card/40 p-4">
            <p className="mb-2 text-sm font-medium">{option.name}</p>
            <ul className="space-y-1 text-xs">
              {option.pros.map((p) => (
                <li key={p} className="text-foreground">
                  <span className="text-accent">+</span> {p}
                </li>
              ))}
              {option.cons.map((c) => (
                <li key={c} className="text-muted-foreground">
                  <span className="text-muted-foreground">−</span> {c}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Reasoning */}
      <section className="mt-6 rounded-xl border border-border bg-card/40 p-4">
        <h3 className="mb-2 text-sm font-medium">Why</h3>
        <p className="text-pretty text-sm text-muted-foreground">{result.reasoning}</p>
      </section>
    </div>
  );
}

function ConfidenceMeter({ value }: { value: number }) {
  return (
    <div className="text-right">
      <p className="text-2xl font-semibold tabular-nums">{Math.round(value)}%</p>
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">confidence</p>
    </div>
  );
}

function ScoreBar({ option }: { option: OptionResult }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className={option.is_winner ? "font-medium text-foreground" : "text-muted-foreground"}>
          {option.rank}. {option.name}
        </span>
        <span className="tabular-nums text-muted-foreground">
          {option.overall_score.toFixed(0)}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className={option.is_winner ? "h-full bg-accent" : "h-full bg-muted-foreground/40"}
          style={{ width: `${Math.min(100, option.overall_score)}%` }}
        />
      </div>
    </div>
  );
}
