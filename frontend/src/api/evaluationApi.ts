import { apiFetch } from './client';
import { EvaluationSuiteResult } from '../types/evaluation';

export const evaluationApi = {
  runEvaluation: async (): Promise<EvaluationSuiteResult> => {
    return apiFetch<EvaluationSuiteResult>('/evaluation/run', { method: 'POST' });
  },

  getLatestEvaluation: async (): Promise<EvaluationSuiteResult> => {
    return apiFetch<EvaluationSuiteResult>('/evaluation/latest');
  },
};
