import { defineStore } from "pinia";
import { ref } from "vue";
import { analyzeText as apiAnalyzeText } from "@/services/api";

export const useAnalysisStore = defineStore("analysis", () => {
  const analysisResult = ref({
    risk_assessment: {
      score: null,
      level: null,
      immediate_concerns: [],
    },
    content_analysis: {
      sentiment: null,
      tone: null,
      complexity: null,
      credibility_flags: [],
    },
    bias_assessment: {
      detected_biases: [],
      implicit_biases: [],
      severity: null,
    },
    cultural_sensitivity: {
      flags: [],
      affected_groups: [],
      context: null,
    },
    recommendations: [],
  });

  const isLoading = ref(false);
  const error = ref(null);

  const analyzeText = async (text) => {
    isLoading.value = true;
    error.value = null;

    try {
      const result = await apiAnalyzeText(text);

      // Update each part of analysisResult individually
      analysisResult.value.risk_assessment = result.risk_assessment || {
        score: null,
        level: null,
        immediate_concerns: [],
      };
      analysisResult.value.content_analysis = result.content_analysis || {
        sentiment: null,
        tone: null,
        complexity: null,
        credibility_flags: [],
      };
      analysisResult.value.bias_assessment = result.bias_assessment || {
        detected_biases: [],
        implicit_biases: [],
        severity: null,
      };
      analysisResult.value.cultural_sensitivity =
        result.cultural_sensitivity || {
          flags: [],
          affected_groups: [],
          context: null,
        };
      analysisResult.value.recommendations = result.recommendations || [];

      return result;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    analysisResult,
    isLoading,
    error,
    analyzeText,
  };
});
