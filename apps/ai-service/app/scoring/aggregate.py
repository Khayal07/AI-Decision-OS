"""Deterministic scoring math.

The LLM scores each option per criterion (0..10, 10 = best). The winner, weighted
overall scores, ranks, and a margin-based confidence are computed here in code —
not by the model — so results are reproducible and what-if simulation is instant.
"""

from app.schemas.decision import AnalyzerOutput, OptionResult, RankingOutput


def aggregate(analyzer: AnalyzerOutput, ranking: RankingOutput) -> list[OptionResult]:
    """Combine per-criterion scores into weighted, ranked option results (0..100)."""
    weights = {c.name: c.weight for c in analyzer.criteria}
    total_weight = sum(weights.values()) or 1.0

    results: list[OptionResult] = []
    for option in ranking.options:
        criterion_scores = {cs.criterion: cs.score for cs in option.scores}
        weighted = sum(
            (weights.get(name, 0.0) / total_weight) * criterion_scores.get(name, 0.0)
            for name in weights
        )
        results.append(
            OptionResult(
                name=option.name,
                overall_score=round(weighted * 10, 2),  # 0..10 → 0..100
                rank=0,
                pros=option.pros,
                cons=option.cons,
                criterion_scores=criterion_scores,
            )
        )

    results.sort(key=lambda r: r.overall_score, reverse=True)
    for index, result in enumerate(results):
        result.rank = index + 1
        result.is_winner = index == 0
    return results


def margin_confidence(results: list[OptionResult]) -> float:
    """Confidence from the score gap between the top two options."""
    if len(results) < 2:
        return 80.0
    margin = results[0].overall_score - results[1].overall_score
    return max(35.0, min(95.0, 55.0 + margin * 2.0))
