export interface User {
  email: string;
  full_name: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface BrokerConfig {
  broker_name: string;
  api_key: string;
  api_secret: string;
  user_id: string;
}

export interface BrokerStatus {
  broker_name: string;
  status: string;
  message?: string;
}

export type StrategyType = 'momentum' | 'mean_reversion' | 'breakout' | 'scalping';
export type StrategyStatus = 'active' | 'paused' | 'stopped';

export interface Strategy {
  id: string;
  name: string;
  strategy_type: StrategyType;
  symbol: string;
  parameters: Record<string, any>;
  status: StrategyStatus;
  user_id: string;
}

export interface CreateStrategy {
  name: string;
  strategy_type: StrategyType;
  symbol: string;
  parameters: Record<string, any>;
  user_id: string;
}
