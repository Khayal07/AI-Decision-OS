// Deterministic re-scoring for instant "what-if" simulation.
// Mirrors app/scoring/aggregate.py: weighted criterion scores -> 0..100, re-ranked.
// Runs client-side so weight changes recompute instantly (no LLM round-trip).

import type { OptionResult } from "./types";

export function recomputeScores(
  options: OptionResult[],
  weights: Record<string, number>,
): OptionResult[] {
  const total = Object.values(weights).reduce((a, b) => a + b, 0) || 1;

  const scored = options.map((option) => {
    const weighted = Object.entries(weights).reduce(
      (sum, [name, weight]) => sum + (weight / total) * (option.criterion_scores[name] ?? 0),
      0,
    );
    return { ...option, overall_score: Math.round(weighted * 10 * 100) / 100 };
  });

  scored.sort((a, b) => b.overall_score - a.overall_score);
  return scored.map((option, index) => ({
    ...option,
    rank: index + 1,
    is_winner: index === 0,
  }));
}
