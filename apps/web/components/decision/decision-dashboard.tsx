"use client";

import type { DecisionResult, OptionResult, RiskLevel } from "@/lib/types";

import { RadarChart } from "./radar-chart";

export function DecisionDashboard({
  result,
  onReset,
}: {
  result: DecisionResult;
  onReset: () => void;
}) {
  const winner = result.options.find((o) => o.is_winner) ?? result.options[0];
  const criteriaNames = result.criteria.map((c) => c.name);

  return (
    <div className="mx-auto w-full max-w-3xl text-left">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h2 className="text-lg font-medium text-muted-foreground">{result.title}</h2>
        <button
          type="button"
          onClick={onReset}
          className="shrink-0 rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground transition hover:text-foreground"
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
          <div className="text-right">
            <p className="text-2xl font-semibold tabular-nums">{Math.round(result.confidence)}%</p>
            <p className="text-[10px] uppercase tracking-wide text-muted-foreground">confidence</p>
          </div>
        </div>
        <p className="mt-4 text-pretty text-sm text-muted-foreground">{result.recommendation}</p>
      </div>

      {/* Scores + radar */}
      <section className="mt-6 grid gap-6 sm:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-medium">Comparison</h3>
          <div className="space-y-3">
            {result.options.map((option) => (
              <ScoreBar key={option.name} option={option} />
            ))}
          </div>
        </div>
        {criteriaNames.length >= 3 && (
          <div>
            <h3 className="mb-1 text-sm font-medium">Criteria radar</h3>
            <RadarChart criteria={criteriaNames} options={result.options} />
          </div>
        )}
      </section>

      {/* Risk + cost per option */}
      <section className="mt-6 grid gap-4 sm:grid-cols-2">
        {result.options.map((option) => (
          <div key={option.name} className="rounded-xl border border-border bg-card/40 p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-medium">{option.name}</p>
              {option.risk_level && <RiskBadge level={option.risk_level} />}
            </div>
            <dl className="space-y-1 text-xs text-muted-foreground">
              {option.upfront_cost != null && (
                <Row label="Upfront" value={`$${option.upfront_cost.toLocaleString()}`} />
              )}
              {option.long_term_value != null && (
                <Row label="Long-term value" value={`${option.long_term_value.toFixed(0)}/10`} />
              )}
              {option.fit != null && <Row label="Fit" value={`${option.fit.toFixed(0)}/10`} />}
              {option.regret_risk != null && (
                <Row label="Regret risk" value={`${option.regret_risk.toFixed(0)}/10`} />
              )}
            </dl>
            {option.risks.length > 0 && (
              <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                {option.risks.slice(0, 2).map((r) => (
                  <li key={r.description}>· {r.description}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
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
                  <span>−</span> {c}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Evidence */}
      {result.evidence.length > 0 && (
        <section className="mt-6 rounded-xl border border-border bg-card/40 p-4">
          <h3 className="mb-2 text-sm font-medium">Evidence</h3>
          <ul className="space-y-1.5 text-xs text-muted-foreground">
            {result.evidence.map((e) => (
              <li key={e.claim} className="flex items-start gap-2">
                <span
                  className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                  style={{ opacity: Math.max(0.25, e.credibility) }}
                />
                <span>{e.claim}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Reasoning */}
      <section className="mt-6 rounded-xl border border-border bg-card/40 p-4">
        <h3 className="mb-2 text-sm font-medium">Why</h3>
        <p className="text-pretty text-sm text-muted-foreground">{result.reasoning}</p>
        {result.verifier_issues.length > 0 && (
          <p className="mt-3 text-xs text-amber-400">
            Verifier flagged: {result.verifier_issues.join("; ")}
          </p>
        )}
      </section>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt>{label}</dt>
      <dd className="tabular-nums text-foreground">{value}</dd>
    </div>
  );
}

function RiskBadge({ level }: { level: RiskLevel }) {
  const styles: Record<RiskLevel, string> = {
    low: "border-emerald-500/40 text-emerald-400",
    medium: "border-amber-500/40 text-amber-400",
    high: "border-rose-500/40 text-rose-400",
  };
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[10px] uppercase ${styles[level]}`}>
      {level} risk
    </span>
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
