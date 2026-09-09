export type DocumentStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'PROCESSED'
  | 'COMPLETED'
  | 'UPLOADED'
  | 'FAILED';

export interface DocumentPage {
  id: string;
  page_number: number;
  raw_text: string;
  layout_blocks?: any[];
}

export interface Document {
  id: string;
  filename: string;
  file_path: string;
  file_hash: string;
  file_size: number;
  num_pages: number;
  page_count?: number;
  status: DocumentStatus;
  error_message?: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
  fact_count?: number;
  pages?: DocumentPage[];
}
