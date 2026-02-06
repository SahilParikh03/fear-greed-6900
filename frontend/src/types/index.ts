export interface ComponentScore {
  score: number;
  signal: string;
  reasoning: string;
}

export interface IndexData {
  master_score: number;
  sentiment: string;
  breakdown: {
    volatility: number;
    dominance: number;
    social: number;
  };
  component_details: {
    volatility: ComponentScore;
    dominance: ComponentScore;
    social: ComponentScore;
  };
  weights: {
    volatility: number;
    dominance: number;
    social: number;
  };
  timestamp: string;
}

export interface HistoryItem {
  timestamp: string;
  total_market_cap: number;
  btc_dominance: number;
  total_volume_24h?: number;
  market_cap_change_24h?: number;
}

export interface HistoryData {
  count: number;
  data: HistoryItem[];
}
