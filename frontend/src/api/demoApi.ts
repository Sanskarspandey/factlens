import { apiFetch } from './client';
import { DemoCase } from '../types/api';

export const demoApi = {
  getDemoCases: async (): Promise<DemoCase[]> => {
    return apiFetch<DemoCase[]>('/demo/cases');
  },

  getCases: async (): Promise<{ cases: DemoCase[] }> => {
    const cases = await demoApi.getDemoCases();
    return { cases };
  },

  seedDemoData: async (): Promise<{
    seeded_documents: number;
    seeded_facts: number;
    reconciled_cases: number;
    documents_created?: number;
    facts_created?: number;
    reconciliations_created?: number;
  }> => {
    const res = await apiFetch<any>('/demo/seed', {
      method: 'POST',
    });
    return {
      ...res,
      documents_created: res.seeded_documents,
      facts_created: res.seeded_facts,
      reconciliations_created: res.reconciled_cases,
    };
  },

  seedDemo: async (): Promise<{
    documents_created: number;
    facts_created: number;
    reconciliations_created: number;
  }> => {
    const res = await demoApi.seedDemoData();
    return {
      documents_created: res.seeded_documents,
      facts_created: res.seeded_facts,
      reconciliations_created: res.reconciled_cases,
    };
  },
};
