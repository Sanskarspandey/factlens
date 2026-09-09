export interface EvaluationCategoryStats {
  name: string;
  passed: number;
  failed: number;
  total: number;
}

export interface EvaluationScenarioResult {
  id: string;
  category: string;
  title: string;
  expected_relationship: string;
  actual_relationship: string;
  status: 'PASS' | 'FAIL';
  source_type: 'PDF' | 'SYNTHETIC_DEMO';
  fact_a_id?: string;
  fact_b_id?: string;
  fact_a_preview?: string;
  fact_b_preview?: string;
  explanation: string;
}

export interface EvaluationSummary {
  total_scenarios: number;
  passed_scenarios: number;
  failed_scenarios: number;
  execution_time_ms: number;
}

export interface EvaluationSuiteResult {
  summary: EvaluationSummary;
  categories: EvaluationCategoryStats[];
  scenarios: EvaluationScenarioResult[];
}
