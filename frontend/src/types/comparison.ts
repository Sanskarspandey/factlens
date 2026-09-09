import { Fact } from './fact';

export type RelationshipType = 
  | 'CORROBORATED'
  | 'CONTRADICTED'
  | 'CONTEXTUALLY_DIFFERENT'
  | 'UNCERTAIN';

export type MatchType = 
  | 'LIKELY_SAME_FACT'
  | 'RELATED_FACT'
  | 'TEMPORAL_VARIANT'
  | 'INCOMPATIBLE_CONTEXT'
  | 'LOW_CONFIDENCE';

export interface ValueComparisonResult {
  source_raw?: string;
  source_normalized?: number;
  source_formatted?: string;
  candidate_raw?: string;
  candidate_normalized?: number;
  candidate_formatted?: string;
  absolute_difference?: number;
  relative_difference?: number;
  percentage_difference?: number;
  direction?: 'EQUAL' | 'INCREASE' | 'DECREASE' | 'INCOMPARABLE';
  within_tolerance: boolean;
  match_tolerance: number;
}

export interface ContextComparisonResult {
  entity_match: boolean;
  attribute_match: boolean;
  time_match: boolean;
  fiscal_year_match: boolean;
  quarter_match: boolean;
  scope_match: boolean;
  geography_match: boolean;
  definition_match: boolean;
  value_status_match: boolean;
  currency_match: boolean;
  unit_match: boolean;
  dimension_differences: Record<string, string>;
  is_contextually_compatible: boolean;
}

export interface SupportingEvidenceItem {
  fact_id: string;
  document_id: string;
  document_filename?: string;
  page_number: number;
  evidence_quote: string;
  statement: string;
}

export interface SupportingEvidence {
  source_evidence: SupportingEvidenceItem;
  candidate_evidence: SupportingEvidenceItem;
}

export interface VerdictChecklistItem {
  label: string;
  status: 'PASS' | 'WARN' | 'INFO' | 'FAIL';
  detail?: string;
}

export interface FactRelationship {
  id: string;
  source_fact_id: string;
  candidate_fact_id: string;
  fact_a_id?: string;
  fact_b_id?: string;
  relationship: RelationshipType;
  confidence: number;
  similarity_score?: number;
  rationale: string;
  value_comparison?: ValueComparisonResult;
  context_comparison?: ContextComparisonResult;
  supporting_evidence?: SupportingEvidence;
  uncertainty_notes?: string;
  reasoning_method?: string;
  difference_analysis?: Record<string, any>;
  verdict_checklist?: VerdictChecklistItem[];
  created_at: string;
  source_fact?: Fact;
  candidate_fact?: Fact;
  fact_a?: Fact;
  fact_b?: Fact;
}

export interface CandidateMatch {
  id: string;
  source_fact_id: string;
  candidate_fact_id: string;
  semantic_similarity: number;
  entity_score: number;
  attribute_score: number;
  time_score: number;
  scope_score: number;
  geography_score: number;
  definition_score: number;
  currency_score: number;
  overall_score: number;
  match_type: MatchType;
  reason: string;
  structured_diff?: Record<string, any>;
  created_at: string;
  source_fact?: Fact;
  candidate_fact?: Fact;
}

export interface ReconciliationSummaryStats {
  total_comparisons: number;
  corroborated_count: number;
  contradicted_count: number;
  contextually_different_count: number;
  uncertain_count: number;
}

export interface ReconciliationRunResponse {
  total_evaluated: number;
  corroborated_count: number;
  contradicted_count: number;
  contextually_different_count: number;
  uncertain_count: number;
  reconciled_pairs: FactRelationship[];
}

export interface ReconciliationSession {
  id: string;
  title?: string;
  description?: string;
  document_ids: string[];
  summary_stats?: ReconciliationSummaryStats;
  created_at: string;
  relationships: FactRelationship[];
}
