import axios from "axios";
import type { IndexData, HistoryData } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiClient = {
  getIndex: async (): Promise<IndexData> => {
    const response = await api.get<IndexData>("/api/v1/index");
    return response.data;
  },

  getHistory: async (days: number = 7): Promise<HistoryData> => {
    const response = await api.get<HistoryData>("/api/v1/history", {
      params: { days },
    });
    return response.data;
  },

  refreshData: async (): Promise<{ status: string; message: string; timestamp: string }> => {
    const response = await api.post("/api/v1/refresh");
    return response.data;
  },

  healthCheck: async (): Promise<any> => {
    const response = await api.get("/api/v1/health");
    return response.data;
  },
};
