import api from './api';
import { Strategy, CreateStrategy } from '../types';

export const strategyService = {
  async list(userId?: string): Promise<Strategy[]> {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get<Strategy[]>('/api/v1/strategies/', { params });
    return response.data;
  },

  async get(strategyId: string): Promise<Strategy> {
    const response = await api.get<Strategy>(`/api/v1/strategies/${strategyId}`);
    return response.data;
  },

  async create(data: CreateStrategy): Promise<Strategy> {
    const response = await api.post<Strategy>('/api/v1/strategies/', data);
    return response.data;
  },

  async update(strategyId: string, data: Partial<Strategy>): Promise<Strategy> {
    const response = await api.patch<Strategy>(`/api/v1/strategies/${strategyId}`, data);
    return response.data;
  },

  async delete(strategyId: string): Promise<void> {
    await api.delete(`/api/v1/strategies/${strategyId}`);
  },

  async start(strategyId: string): Promise<Strategy> {
    const response = await api.post<Strategy>(`/api/v1/strategies/${strategyId}/start`);
    return response.data;
  },

  async stop(strategyId: string): Promise<Strategy> {
    const response = await api.post<Strategy>(`/api/v1/strategies/${strategyId}/stop`);
    return response.data;
  },
};
