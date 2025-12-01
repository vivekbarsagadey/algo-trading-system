import api from './api';
import { BrokerConfig, BrokerStatus } from '../types';

export const brokerService = {
  async connect(config: BrokerConfig): Promise<BrokerStatus> {
    const response = await api.post<BrokerStatus>('/api/v1/broker/connect', config);
    return response.data;
  },

  async disconnect(userId: string): Promise<BrokerStatus> {
    const response = await api.delete<BrokerStatus>(`/api/v1/broker/disconnect/${userId}`);
    return response.data;
  },

  async getStatus(userId: string): Promise<BrokerStatus> {
    const response = await api.get<BrokerStatus>(`/api/v1/broker/status/${userId}`);
    return response.data;
  },

  async getSupportedBrokers(): Promise<string[]> {
    const response = await api.get<string[]>('/api/v1/broker/supported');
    return response.data;
  },
};
