export type FactStatus = 'EXTRACTED' | 'VERIFIED' | 'UNCERTAIN' | 'FAILED' | 'FLAGGED';
export type ValueStatus = 'ACTUAL' | 'ESTIMATE' | 'FORECAST' | 'GUIDANCE' | 'TARGET' | 'UNKNOWN';

export interface Fact {
  id: string;
  document_id: string;
  page_id?: string;
  page_number: number;
  document_filename?: string;
  
  // Semantic contents
  statement: string;
  entity?: string;
  attribute?: string;
  
  // Grounding
  evidence_quote: string;
  bounding_box?: number[]; // [x0, y0, x1, y1]
  
  // Normalization
  raw_value?: string;
  normalized_value?: number;
  normalized_value_str?: string;
  unit?: string;
  currency?: string;
  time_period?: string;
  fiscal_year?: string;
  quarter?: string;
  
  // Context Dimensions
  geography?: string;
  scope?: string;
  definition?: string;
  source_section?: string;
  value_status?: ValueStatus;

  // Quality & Uncertainty
  confidence: number;
  status: FactStatus;
  uncertainty_notes?: string;
  indexing_status?: string;
  source_type?: 'PDF' | 'SYNTHETIC_DEMO';
  
  created_at: string;
  updated_at: string;
}

export interface FactFilterParams {
  document_id?: string;
  entity?: string;
  attribute?: string;
  time_period?: string;
  fiscal_year?: string;
  quarter?: string;
  status?: FactStatus;
  search_query?: string;
  search?: string;
  min_confidence?: number;
  skip?: number;
  limit?: number;
}

