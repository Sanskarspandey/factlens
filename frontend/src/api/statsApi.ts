import { apiFetch } from './client';
import { SystemStats } from '../types/api';

export const statsApi = {
  getStats: async (): Promise<SystemStats> => {
    return apiFetch<SystemStats>('/stats');
  },
};
