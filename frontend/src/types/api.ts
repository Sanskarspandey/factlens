export interface APIResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page?: number;
  size?: number;
  limit?: number;
  total_pages?: number;
}

export interface SystemStats {
  documents: number;
  pages: number;
  facts: number;
  reconciliations: number;
  corroborated: number;
  contradicted: number;
  contextually_different: number;
  uncertain: number;
}

export interface DemoCase {
  id: string;
  title: string;
  description: string;
  expected_relationship: 'CORROBORATED' | 'CONTRADICTED' | 'CONTEXTUALLY_DIFFERENT' | 'UNCERTAIN';
  fact_a_preview?: string;
  fact_b_preview?: string;
  metric?: string;
  source_a_doc?: string;
  source_a_val?: string;
  source_b_doc?: string;
  source_b_val?: string;
  fact_a_id?: string;
  fact_b_id?: string;
}
