"use client";

import type { OptionResult } from "@/lib/types";

type Series = { name: string; values: number[]; winner: boolean };

const MAX = 10;
const SIZE = 280;
const CENTER = SIZE / 2;
const RADIUS = SIZE / 2 - 44;

function point(index: number, count: number, value: number) {
  const angle = -Math.PI / 2 + (index * 2 * Math.PI) / count;
  const r = (Math.max(0, Math.min(MAX, value)) / MAX) * RADIUS;
  return [CENTER + r * Math.cos(angle), CENTER + r * Math.sin(angle)] as const;
}

function axisPoint(index: number, count: number, factor: number) {
  const angle = -Math.PI / 2 + (index * 2 * Math.PI) / count;
  return [CENTER + factor * RADIUS * Math.cos(angle), CENTER + factor * RADIUS * Math.sin(angle)] as const;
}

/** Lightweight dependency-free radar chart comparing options across criteria. */
export function RadarChart({
  criteria,
  options,
}: {
  criteria: string[];
  options: OptionResult[];
}) {
  const count = criteria.length;
  if (count < 3) return null;

  const series: Series[] = options.map((o) => ({
    name: o.name,
    winner: o.is_winner,
    values: criteria.map((c) => o.criterion_scores[c] ?? 0),
  }));

  return (
    <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="mx-auto h-72 w-72" role="img" aria-label="Criteria radar">
      {/* rings */}
      {[0.25, 0.5, 0.75, 1].map((factor) => (
        <polygon
          key={factor}
          points={criteria
            .map((_, i) => axisPoint(i, count, factor).join(","))
            .join(" ")}
          className="fill-none stroke-border"
          strokeWidth={1}
        />
      ))}
      {/* axes + labels */}
      {criteria.map((label, i) => {
        const [x, y] = axisPoint(i, count, 1);
        const [lx, ly] = axisPoint(i, count, 1.18);
        return (
          <g key={label}>
            <line x1={CENTER} y1={CENTER} x2={x} y2={y} className="stroke-border" strokeWidth={1} />
            <text
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-muted-foreground text-[9px]"
            >
              {label}
            </text>
          </g>
        );
      })}
      {/* series */}
      {series.map((s) => (
        <polygon
          key={s.name}
          points={s.values.map((v, i) => point(i, count, v).join(",")).join(" ")}
          className={
            s.winner
              ? "fill-accent/25 stroke-accent"
              : "fill-muted-foreground/10 stroke-muted-foreground/60"
          }
          strokeWidth={1.5}
        />
      ))}
    </svg>
  );
}
