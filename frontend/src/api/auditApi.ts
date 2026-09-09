import { apiFetch } from './client';
import { ExtractionFailureItem, UncertaintiesResponse } from '../types/audit';

export const auditApi = {
  getFailures: async (
    documentId?: string,
    stage?: string,
    skip = 0,
    limit = 50
  ): Promise<ExtractionFailureItem[]> => {
    const query = new URLSearchParams();
    if (documentId) query.append('document_id', documentId);
    if (stage) query.append('stage', stage);
    query.append('skip', skip.toString());
    query.append('limit', limit.toString());
    return apiFetch<ExtractionFailureItem[]>(`/audit/failures?${query.toString()}`);
  },

  getUncertainties: async (): Promise<UncertaintiesResponse> => {
    return apiFetch<UncertaintiesResponse>('/audit/uncertainties');
  },
};
