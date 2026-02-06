/**
 * API Configuration
 *
 * Automatically uses the correct API URL based on environment:
 * - Development: http://localhost:8000
 * - Production: Same origin (Vercel deployment)
 */

const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = isDevelopment
  ? "http://localhost:8000"
  : "";  // Use same origin in production

export const API_ENDPOINTS = {
  index: `${API_BASE_URL}/api/v1/index`,
  agentSignal: `${API_BASE_URL}/api/v1/agent/signal`,
  history: `${API_BASE_URL}/api/v1/history`,
  refresh: `${API_BASE_URL}/api/v1/refresh`,
  btcPrice: `${API_BASE_URL}/api/v1/btc-price`,
  prices: `${API_BASE_URL}/api/v1/prices`,
  stream: `${API_BASE_URL}/api/v1/stream`,
  health: `${API_BASE_URL}/api/v1/health`,
};
