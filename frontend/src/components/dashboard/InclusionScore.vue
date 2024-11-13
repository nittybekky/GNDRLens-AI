<!-- src/components/dashboard/InclusionScore.vue -->
<template>
  <v-container>
    <v-row>
      <!-- Overall Score Card -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Inclusion Score</v-card-title>
          <v-card-text>
            <div class="text-h3 text-center">
              {{ analysisStore.scorePercentage }}%
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Trend Chart -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Score Trends</v-card-title>
          <v-card-text>
            <Line :data="chartData" :options="chartOptions" />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Patterns & Insights -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Detected Patterns</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(pattern, index) in analysisStore.metrics.patterns"
                :key="index"
                :title="pattern"
              >
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-pattern</v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Cultural Insights -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Cultural Insights</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(insight, index) in analysisStore.metrics
                  .culturalInsights"
                :key="index"
                :title="insight"
              >
                <template v-slot:prepend>
                  <v-icon color="info">mdi-lightbulb</v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAnalysisStore } from "@/store/modules/analysisStore";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const analysisStore = useAnalysisStore();
const timeframe = ref("30days");

const chartData = computed(() => ({
  labels: analysisStore.trendLabels,
  datasets: [
    {
      label: "Inclusion Score",
      data: analysisStore.trendScores,
      borderColor: "#1976D2",
      tension: 0.1,
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
    },
  },
};

onMounted(async () => {
  await analysisStore.fetchMetrics(timeframe.value);
});
</script>
