// Mirrors app/schemas/decision.py::DecisionResult on the AI service.

export type Criterion = {
  name: string;
  weight: number;
  direction: "higher_better" | "lower_better";
};

export type OptionResult = {
  name: string;
  overall_score: number;
  rank: number;
  is_winner: boolean;
  pros: string[];
  cons: string[];
  criterion_scores: Record<string, number>;
};

export type DecisionResult = {
  title: string;
  decision_type: string;
  criteria: Criterion[];
  options: OptionResult[];
  winner: string;
  confidence: number;
  recommendation: string;
  reasoning: string;
};

export type AgentStatus = { node: string; label: string };
