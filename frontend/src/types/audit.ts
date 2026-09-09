export interface ExtractionFailureItem {
  id: string;
  document_id: string;
  document_filename?: string;
  page_number?: number;
  stage: string;
  raw_content?: string;
  error_type: string;
  error_message: string;
  context_data?: Record<string, any>;
  created_at?: string;
}

export interface UncertainFactItem {
  id: string;
  type: 'FACT_UNCERTAINTY';
  document_id: string;
  statement: string;
  entity?: string;
  attribute?: string;
  evidence_quote: string;
  uncertainty_notes?: string;
  confidence: number;
  created_at?: string;
}

export interface UncertainReconciliationItem {
  id: string;
  type: 'RECONCILIATION_UNCERTAINTY';
  source_fact_id: string;
  candidate_fact_id: string;
  relationship: string;
  rationale: string;
  uncertainty_notes?: string;
  confidence: number;
  created_at?: string;
}

export interface UncertaintiesResponse {
  uncertain_facts: UncertainFactItem[];
  uncertain_reconciliations: UncertainReconciliationItem[];
}
