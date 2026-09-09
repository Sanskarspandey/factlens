import { apiFetch } from './client';
import { Fact, FactFilterParams } from '../types/fact';
import { CandidateMatch } from '../types/comparison';
import { PaginatedResponse } from '../types/api';

export const factsApi = {
  getFacts: async (params: FactFilterParams = {}, skip = 0, limit = 100): Promise<Fact[]> => {
    const query = new URLSearchParams();
    if (params.document_id) query.append('document_id', params.document_id);
    if (params.entity) query.append('entity', params.entity);
    if (params.attribute) query.append('attribute', params.attribute);
    if (params.time_period) query.append('time_period', params.time_period);
    if (params.fiscal_year) query.append('fiscal_year', params.fiscal_year);
    if (params.quarter) query.append('quarter', params.quarter);
    if (params.status) query.append('status', params.status);
    if (params.search || params.search_query) query.append('search', params.search || params.search_query || '');
    if (params.min_confidence !== undefined) query.append('min_confidence', params.min_confidence.toString());
    query.append('skip', skip.toString());
    query.append('limit', limit.toString());

    return apiFetch<Fact[]>(`/facts?${query.toString()}`);
  },

  listFacts: async (
    params: FactFilterParams = {},
    page = 1,
    limit = 100
  ): Promise<PaginatedResponse<Fact>> => {
    const skip = (page - 1) * limit;
    const facts = await factsApi.getFacts(params, skip, limit);
    return {
      items: facts,
      total: facts.length,
      page,
      limit,
      total_pages: Math.ceil(facts.length / limit) || 1,
    };
  },

  getFact: async (factId: string): Promise<Fact> => {
    return apiFetch<Fact>(`/facts/${factId}`);
  },

  getFactMatches: async (factId: string, topK = 10, minScore = 0.30): Promise<CandidateMatch[]> => {
    return apiFetch<CandidateMatch[]>(`/facts/${factId}/matches?top_k=${topK}&min_score=${minScore}`);
  },

  getCandidateMatches: async (
    factId: string,
    topK = 10,
    minScore = 0.30
  ): Promise<{ candidates: CandidateMatch[] }> => {
    const candidates = await factsApi.getFactMatches(factId, topK, minScore);
    return { candidates };
  },
};
