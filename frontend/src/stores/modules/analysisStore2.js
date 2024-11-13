// src/store/modules/analysisStore.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api";

export const useAnalysisStore = defineStore("analysis", () => {
  // State
  const metrics = ref({
    inclusionScore: 0,
    trendData: [],
    patterns: [],
    culturalInsights: [],
    biasIndicators: [],
    recentAnalyses: [],
  });

  const isLoading = ref(false);
  const error = ref(null);

  // Actions
  const fetchMetrics = async (timeframe = "30days") => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get(
        `/analysis/metrics?timeframe=${timeframe}`
      );
      metrics.value = response.data;
    } catch (err) {
      error.value = err.message;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchUserHistory = async () => {
    try {
      const response = await api.get("/analysis/history");
      metrics.value.recentAnalyses = response.data;
    } catch (err) {
      error.value = err.message;
    }
  };

  // Computed
  const scorePercentage = computed(() =>
    (metrics.value.inclusionScore * 100).toFixed(1)
  );

  const trendLabels = computed(() =>
    metrics.value.trendData.map((d) => d.date)
  );

  const trendScores = computed(() =>
    metrics.value.trendData.map((d) => d.score)
  );

  const analyzeText = async (text, userId) => {
    isLoading.value = true;
    error.value = null;
    const requestData = {
      content: text,
      // user_id: userId, // Add user_id if needed by backend
    };
    console.log("Sending request with data:", requestData); // Log request payload
    try {
      const response = await api.post("api/v1/analysis/analyze", requestData);
      await fetchUserHistory();
      return response.data;
    } catch (err) {
      console.error(
        "Analysis request error:",
        err.response?.data || err.message
      );
      error.value = err.response?.data?.detail || err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    metrics,
    isLoading,
    error,
    fetchMetrics,
    fetchUserHistory,
    scorePercentage,
    trendLabels,
    trendScores,
    analyzeText,
  };
});
