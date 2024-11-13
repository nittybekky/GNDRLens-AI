import axios from "axios";

// const API_BASE_URL = "http://localhost:8000";https://gndrlens-ai.onrender.com
const API_BASE_URL = "https://gndrlens-ai.onrender.com";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const analyzeText = async (payload) => {
  try {
    console.log("Sending payload:", payload);
    const response = await api.post("/api/v1/analysis/analyze", payload);
    console.log("API response:", response.data);

    if (response?.data?.status === "success") {
      return response.data;
    } else {
      throw new Error(response?.data?.error || "Analysis failed");
    }
  } catch (error) {
    console.error("API error:", error);
    console.error("Error message:", error.message);
    throw new Error(error.response?.data?.error || "Analysis failed");
  }
};

export const getMetrics = async () => {
  try {
    const response = await api.get("/api/v1/analysis/metrics");
    console.log("Metrics response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch metrics:", error);
    throw error;
  }
};

export default api;
