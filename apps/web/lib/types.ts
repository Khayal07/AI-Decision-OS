// Mirrors app/schemas/decision.py::DecisionResult on the AI service.

export type Criterion = {
  name: string;
  weight: number;
  direction: "higher_better" | "lower_better";
};

export type RiskItem = {
  description: string;
  severity: number;
  likelihood: number;
  mitigation?: string | null;
};

export type EvidenceItem = {
  claim: string;
  credibility: number;
  supports?: string | null;
};

export type RiskLevel = "low" | "medium" | "high";

export type OptionResult = {
  name: string;
  overall_score: number;
  rank: number;
  is_winner: boolean;
  pros: string[];
  cons: string[];
  criterion_scores: Record<string, number>;
  risk_level?: RiskLevel | null;
  risks: RiskItem[];
  upfront_cost?: number | null;
  long_term_value?: number | null;
  regret_risk?: number | null;
  fit?: number | null;
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
  evidence: EvidenceItem[];
  verifier_issues: string[];
};

export type AgentStatus = { node: string; label: string };
