export interface Hint {
  hint_id: number;
  hint_text: string;
  colorHex?: string;
}

export type MetricKey = 'convergence' | 'relevance' | 'familiarity' | 'readability' | 'answer-leakage' | 'leakage-avoidance';

export interface Metric {
  name: string;
  value: number;
  metadata?: any;
}

export interface EvaluationPayload {
  question: string;
  num_hints: number;
  metrics: Metric[][];
  scores_convergence: Record<string, number>[];
  candidate_answers: string[];
}

export interface GenerateResponse {
  question: string;
  hints: { id: number; text: string }[];
  answer: string;
}

export type MetricsById = Record<number, Record<string, number>>;
export type ElimMode = "per-hint" | "sequence";