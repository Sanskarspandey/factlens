import { apiFetch } from './client';
import { FactRelationship } from '../types/comparison';

export const comparisonApi = {
  comparePair: async (factAId: string, factBId: string, useLlm = false): Promise<FactRelationship> => {
    return apiFetch<FactRelationship>('/comparison/compare-pair', {
      method: 'POST',
      body: JSON.stringify({
        fact_a_id: factAId,
        fact_b_id: factBId,
        use_llm_for_ambiguous: useLlm,
      }),
    });
  },
};
