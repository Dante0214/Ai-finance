import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
// const API_BASE_URL = "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const stockApi = {
  search: (query) =>
    apiClient.get("/api/stock-search", { params: { q: query } }),
  analyze: (ticker) => apiClient.get(`/api/analysis/${ticker}`),
  rankings: () => apiClient.get("/api/us/rankings"),
};
