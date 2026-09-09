import { apiFetch } from './client';
import {
  FactRelationship,
  RelationshipType,
  ReconciliationRunResponse,
  ReconciliationSession,
} from '../types/comparison';
import { PaginatedResponse } from '../types/api';

export interface ReconciliationFilterParams {
  relationship?: RelationshipType;
  document_id?: string;
  entity?: string;
  attribute?: string;
  min_confidence?: number;
  skip?: number;
  limit?: number;
}

export const reconciliationApi = {
  getReconciliations: async (
    params: ReconciliationFilterParams = {},
    skip = 0,
    limit = 50
  ): Promise<FactRelationship[]> => {
    const query = new URLSearchParams();
    if (params.relationship) query.append('relationship', params.relationship);
    if (params.document_id) query.append('document_id', params.document_id);
    if (params.entity) query.append('entity', params.entity);
    if (params.attribute) query.append('attribute', params.attribute);
    if (params.min_confidence !== undefined) query.append('min_confidence', params.min_confidence.toString());
    query.append('skip', (params.skip !== undefined ? params.skip : skip).toString());
    query.append('limit', (params.limit !== undefined ? params.limit : limit).toString());

    return apiFetch<FactRelationship[]>(`/reconciliation?${query.toString()}`);
  },

  listReconciliations: async (
    params: ReconciliationFilterParams = {}
  ): Promise<PaginatedResponse<FactRelationship>> => {
    const items = await reconciliationApi.getReconciliations(params);
    return {
      items,
      total: items.length,
      page: 1,
      limit: params.limit || 50,
      total_pages: 1,
    };
  },

  getReconciliation: async (id: string): Promise<FactRelationship> => {
    return apiFetch<FactRelationship>(`/reconciliation/${id}`);
  },

  runReconciliation: async (options: {
    min_candidate_score?: number;
    document_ids?: string[];
    use_llm_for_ambiguous?: boolean;
    reconcile_all?: boolean;
    similarity_threshold?: number;
  } = {}): Promise<ReconciliationRunResponse> => {
    return apiFetch<ReconciliationRunResponse>('/reconciliation/run', {
      method: 'POST',
      body: JSON.stringify({
        min_candidate_score: options.similarity_threshold || options.min_candidate_score || 0.30,
        document_ids: options.document_ids,
        use_llm_for_ambiguous: options.use_llm_for_ambiguous || false,
      }),
    });
  },

  reconcileFactPair: async (
    factAId: string,
    factBId: string,
    useLlm = false
  ): Promise<FactRelationship> => {
    return apiFetch<FactRelationship>('/reconciliation/pair', {
      method: 'POST',
      body: JSON.stringify({
        fact_a_id: factAId,
        fact_b_id: factBId,
        use_llm_for_ambiguous: useLlm,
      }),
    });
  },

  getSessions: async (): Promise<ReconciliationSession[]> => {
    return apiFetch<ReconciliationSession[]>('/reconciliation/sessions');
  },

  getSession: async (sessionId: string): Promise<ReconciliationSession> => {
    return apiFetch<ReconciliationSession>(`/reconciliation/sessions/${sessionId}`);
  },
};
