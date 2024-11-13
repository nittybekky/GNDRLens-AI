<template>
  <v-container>
    <!-- Input Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">
            SDG 5 Gender Analysis Assessment
          </v-card-title>
          <v-select
            v-model="selectedIndustry"
            :items="industries"
            label="Select Industry"
            placeholder="Choose an industry"
            outlined
            dense
          ></v-select>
          <v-card-text>
            <v-textarea
              v-model="textInput"
              label="Enter text to analyze..."
              :disabled="isLoading"
              rows="4"
              hide-details
              class="mb-4"
            />
            <v-btn
              @click="analyzeContent"
              :loading="isLoading"
              color="primary"
              class="mt-4"
            >
              Analyze Text
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-if="result && !error">
    <!-- Overall Assessment Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Overall Assessment</v-card-title>
      <v-card-text>
        <p>
          <strong>Equity Score:</strong>
          {{ overallMetrics.equityScore }} (Scale: 0 to 1)
        </p>
        <!-- Display charts if results are available -->
        <v-row v-if="result">
          <v-col cols="12">
            <!-- Overall Equity Score -->
            <div class="chart-container">
              <Bar :data="equityChartData" :options="chartOptions" />
            </div>
          </v-col>
        </v-row>
        <v-divider class="my-2"></v-divider>
        <p><strong>Priority Actions:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(action, index) in overallMetrics.priorityActions"
            :key="index"
          >
            <v-list-item-content>
              <v-list-item-title>{{ action.issue }}</v-list-item-title>
              <v-list-item-subtitle>{{
                action.recommendation
              }}</v-list-item-subtitle>
              <p>
                <strong>Impact:</strong>
                {{ action.impact }}
              </p>
              <p>
                <strong>Priority:</strong>
                {{ action.priority }}
              </p>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- Bias Detection Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Bias Detection</v-card-title>
      <v-card-text>
        <p>
          <strong>Bias Score:</strong> {{ biasMetrics.biasScore }} (Scale: 0 to
          1)
        </p>
        <v-divider class="my-2"></v-divider>
        <p>
          Explicit Biases: This checks for obvious, deliberate biases or
          discriminatory actions based on someone's identity, such as race,
          gender, or other characteristics. Implicit Biases: This focuses on
          unconscious biases that could affect decisions or interactions, like
          favoring one group over another without realizing it. Stereotypes:
          Looks for generalized assumptions about a group, like thinking all
          people from a certain background act or think the same way. Bias
          Score: A score that summarizes how much bias exists in the
          environment. A higher score means more bias.
        </p>
        <p>
          <strong>Explicit Biases:</strong>
          {{
            biasMetrics.explicitBiases.length
              ? biasMetrics.explicitBiases.join(", ")
              : "No explicit biases detected."
          }}
        </p>
        <p>
          <strong>Implicit Biases:</strong>
          {{
            biasMetrics.implicitBiases.length
              ? biasMetrics.implicitBiases.join(", ")
              : "No implicit biases detected."
          }}
        </p>
        <p>
          <strong>Stereotypes:</strong>
          {{
            biasMetrics.stereotypes.length
              ? biasMetrics.stereotypes.join(", ")
              : "No stereotypes detected."
          }}
        </p>
        <div class="chart-container">
          <Bar :data="biasChartData" :options="chartOptions" />
        </div>
      </v-card-text>
    </v-card>

    <!-- Representation Analysis Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Representation Analysis</v-card-title>
      <div class="chart-container">
        <Pie :data="representationChartData" :options="chartOptions" />
      </div>
      <v-divider class="my-2"></v-divider>
      <p>
        Visibility Score: Measures how much a group (e.g., women, minorities) is
        represented or visible in key positions in the organization. A higher
        score means more visibility. Agency Score: This looks at how much
        influence a group has in decision-making processes. A low score means
        they have less say in important decisions. Power Dynamics: This
        identifies any imbalances in power, such as a lack of representation in
        leadership roles for certain groups, which can affect their influence
        and voice in the organization.
      </p>
      <v-card-text>
        <p>
          <strong>Visibility Score:</strong>
          {{ representationMetrics.visibilityScore }} (Scale: 0 to 1)
        </p>
        <p>
          <strong>Agency Score:</strong>
          {{ representationMetrics.agencyScore }} (Scale: 0 to 1)
        </p>
        <v-divider class="my-2"></v-divider>
        <p><strong>Power Dynamics Observations:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(item, index) in representationMetrics.powerDynamics"
            :key="index"
          >
            {{ item.observation }}
          </v-list-item>
        </v-list>
        <p><strong>Improvement Areas:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(area, index) in representationMetrics.improvementAreas"
            :key="index"
          >
            {{ area.suggestion }}
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- Workplace Equity Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Workplace Equity</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar :data="workplaceEquityChartData" :options="chartOptions" />
        </div>
        <p>
          <strong>Workplace Equity Score:</strong>
          {{ workplaceEquityScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Workplace Equity score is an assessment of leadership inclusivity,
          advancement barriers, and work-life balance assumptions within the
          organization. A higher score indicates more equitable workplace
          practices.
        </p>
        <v-divider class="my-2"></v-divider>
        <p><strong>Advancement Barriers:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(barrier, index) in workplaceMetrics.advancementBarriers"
            :key="index"
          >
            {{ barrier.barrier || "No advancement barriers detected." }}
          </v-list-item>
        </v-list>
        <p><strong>Work-Life Balance Assumptions:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(assumption, index) in workplaceMetrics.workLifeAssumptions"
            :key="index"
          >
            {{
              assumption.assumption || "No work-life assumptions identified."
            }}
          </v-list-item>
        </v-list>
      </v-card-content>
    </v-card>

    <!-- Safety Assessment Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Safety Assessment</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar :data="safetyAssessmentChartData" :options="chartOptions" />
        </div>
        <p>
          <strong>Safety Assessment Score:</strong>
          {{ safetyAssessmentScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Safety Assessment score evaluates the organization's psychological
          safety, presence of harassment indicators, and use of undermining
          language. A higher score indicates a safer and more supportive work
          environment.
        </p>
        <v-divider class="my-2"></v-divider>
        <p>
          <strong>Harassment Indicators:</strong>
          {{
            safetyMetrics.harassmentIndicators.length
              ? safetyMetrics.harassmentIndicators.join(", ")
              : "No harassment indicators found."
          }}
        </p>
        <p>
          <strong>Undermining Language:</strong>
          {{
            safetyMetrics.underminingLanguage.length
              ? safetyMetrics.underminingLanguage.join(", ")
              : "No undermining language detected."
          }}
        </p>
      </v-card-content>
    </v-card>

    <!-- Empowerment Opportunities Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Empowerment Opportunities</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar
            :data="empowermentOpportunitiesChartData"
            :options="chartOptions"
          />
        </div>
        <p>
          <strong>Empowerment Opportunities Score:</strong>
          {{ empowermentOpportunitiesScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Empowerment Opportunities score reflects the presence of
          growth-oriented language, mentorship opportunities, and inclusive
          language alternatives within the organization. A higher score
          indicates more opportunities for employee development and advancement.
        </p>
        <v-card-text>
          <p>
            <strong>Growth Language:</strong>
            {{
              empowermentMetrics.growthLanguage.length
                ? empowermentMetrics.growthLanguage.join(", ")
                : "No growth-oriented language found."
            }}
          </p>
          <p><strong>Mentorship Opportunities:</strong></p>
          <v-list dense>
            <v-list-item
              v-for="(
                opportunity, index
              ) in empowermentMetrics.mentorshipOpportunities"
              :key="index"
            >
              {{ opportunity || "No mentorship opportunities provided." }}
            </v-list-item>
          </v-list>
          <p>
            <strong>Inclusive Alternatives:</strong>
            {{
              empowermentMetrics.inclusiveAlternatives.length
                ? empowermentMetrics.inclusiveAlternatives.join(", ")
                : "No inclusive language alternatives suggested."
            }}
          </p>
        </v-card-text>
      </v-card-content>
    </v-card>

    <!-- Violence Prevention Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Violence Prevention</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar :data="violencePreventionChartData" :options="chartOptions" />
        </div>
        <p>
          <strong>Violence Prevention Score:</strong>
          {{ violencePreventionScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Violence Prevention score assesses the organization's overall
          safety, presence of risk indicators, and implementation of safety
          measures. A higher score indicates a safer environment with effective
          prevention measures.
        </p>
        <v-divider class="my-2"></v-divider>
        <p>
          <strong>Risk Indicators:</strong>
          {{
            violencePreventionMetrics.riskIndicators.length
              ? violencePreventionMetrics.riskIndicators.join(", ")
              : "No risk indicators detected."
          }}
        </p>
        <p>
          <strong>Safety Measures Gaps:</strong>
          {{
            violencePreventionMetrics.safetyMeasures.gaps.length
              ? violencePreventionMetrics.safetyMeasures.gaps.join(", ")
              : "No safety measure gaps identified."
          }}
        </p>
      </v-card-content>
    </v-card>

    <!-- Care Work Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Care Work</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar :data="careWorkChartData" :options="chartOptions" />
        </div>
        <p>
          <strong>Care Work Score:</strong>
          {{ careWorkScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Care Work score evaluates the recognition and consideration of
          unpaid care responsibilities within the organization. A higher score
          indicates a more supportive environment for employees with care
          obligations.
        </p>
        <v-divider class="my-2"></v-divider>
        <p><strong>Care Responsibilities:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(
              responsibility, index
            ) in careWorkMetrics.careResponsibilities"
            :key="index"
          >
            {{
              responsibility || "No care responsibilities assumptions detected."
            }}
          </v-list-item>
        </v-list>
      </v-card-content>
    </v-card>

    <!-- Policy Implementation Metrics Section -->
    <v-card outlined class="mb-4">
      <v-card-title>Policy Implementation</v-card-title>
      <v-card-content>
        <div class="chart-container">
          <Bar :data="policyImplementationChartData" :options="chartOptions" />
        </div>
        <p>
          <strong>Policy Implementation Score:</strong>
          {{ policyImplementationScore.toFixed(2) }} (Scale: 0 to 100)
        </p>
        <p>
          The Policy Implementation score reflects the organization's current
          policy implementation and the recommendations for additional policies
          to address gender equity. A higher score indicates more effective
          policy implementation.
        </p>
        <p><strong>Recommended Policies:</strong></p>
        <v-list dense>
          <v-list-item
            v-for="(policy, index) in policyMetrics.recommendedPolicies"
            :key="index"
          >
            <v-list-item-content>
              <v-list-item-title
                >{{ policy.focus_area || "No specific focus area." }}:
                {{
                  policy.recommendation || "No recommendations provided."
                }}</v-list-item-title
              >
              <v-list-item-subtitle>{{
                policy.rationale || "No rationale provided."
              }}</v-list-item-subtitle>
              <p>
                <strong>Priority:</strong>
                {{ policy.priority || "No priority specified." }}
              </p>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-content>
    </v-card>

    <!-- Error Display -->
    <v-alert v-if="error" type="error" class="mt-4">
      {{ error }}
    </v-alert>
  </v-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { analyzeText } from "@/services/api";
import { Line, Pie, Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  PointElement,
  LineElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from "chart.js";

// Registering Chart.js elements
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement
);

// Base state management
const textInput = ref("");
const result = ref(null);
const isLoading = ref(false);
const error = ref(null);
const selectedIndustry = ref("");
const industries = [
  "Agriculture",
  "Automotive",
  "Construction",
  "Education",
  "Energy",
  "Finance",
  "Healthcare",
  "Hospitality",
  "Information Technology",
  "Manufacturing",
  "Marketing",
  "Media & Entertainment",
  "Pharmaceuticals",
  "Real Estate",
  "Retail",
  "Telecommunications",
  "Transportation",
  "Travel & Tourism",
];

// Context information
const analysisContext = ref({
  language: navigator.language || "en",
  location: "nigeria",
  industry: selectedIndustry.value,
});

// Analysis method
const analyzeContent = async () => {
  if (!textInput.value.trim()) {
    error.value = "Please enter text to analyze";
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    const response = await analyzeText({
      content: textInput.value,
      context: analysisContext.value,
    });

    result.value = response.data;
    console.log("Analysis result:", result.value);
  } catch (err) {
    console.error("Analysis failed:", err);
    error.value = err.message || "Analysis failed";
  } finally {
    isLoading.value = false;
  }
};

// Computed properties for each metric section
const overallMetrics = computed(() => ({
  equityScore: result.value?.overall_assessment?.equity_score || 0,
  priorityActions: result.value?.overall_assessment?.priority_actions || [
    { issue: "No significant issues found." },
  ],
}));

// Computed properties for each metric section
const biasMetrics = computed(() => ({
  biasScore: result.value?.bias_detection?.bias_score || 0,
  explicitBiases: result.value?.bias_detection?.explicit_biases || [],
  implicitBiases: result.value?.bias_detection?.implicit_biases || [],
  stereotypes: result.value?.bias_detection?.stereotypes || [],
}));

const representationMetrics = computed(() => ({
  visibilityScore: result.value?.representation_analysis?.visibility_score || 0,
  agencyScore: result.value?.representation_analysis?.agency_score || 0,
  powerDynamics: result.value?.representation_analysis?.power_dynamics || [],
  improvementAreas:
    result.value?.representation_analysis?.improvement_areas || [],
}));

const workplaceMetrics = computed(() => ({
  advancementBarriers:
    result.value?.workplace_equity?.advancement_barriers || [],
  leadershipScore:
    result.value?.workplace_equity?.leadership_language?.inclusive_score || 0,
  workLifeAssumptions:
    result.value?.workplace_equity?.work_life_assumptions || [],
}));

const safetyMetrics = computed(() => ({
  psychologicalSafetyScore:
    result.value?.safety_assessment?.psychological_safety?.score || 0,
  harassmentIndicators:
    result.value?.safety_assessment?.harassment_indicators || [],
  underminingLanguage:
    result.value?.safety_assessment?.undermining_language || [],
}));

const empowermentMetrics = computed(() => ({
  growthLanguage:
    result.value?.empowerment_opportunities?.growth_language || [],
  mentorshipOpportunities:
    result.value?.empowerment_opportunities?.mentorship_opportunities || [],
  inclusiveAlternatives:
    result.value?.empowerment_opportunities?.inclusive_alternatives || [],
}));

const violencePreventionMetrics = computed(() => ({
  overallSafetyScore:
    result.value?.violence_prevention?.overall_safety_score || 0,
  riskIndicators: result.value?.violence_prevention?.risk_indicators || [],
  safetyMeasures: {
    gaps: result.value?.violence_prevention?.safety_measures?.gaps || [],
  },
}));

const careWorkMetrics = computed(() => ({
  careRecognitionScore:
    result.value?.unpaid_care_analysis?.care_recognition_score || 0,
  careResponsibilities:
    result.value?.unpaid_care_analysis?.care_responsibilities || [],
  workLifeMeasures: {
    flexibilityScore:
      result.value?.unpaid_care_analysis?.work_life_measures
        ?.flexibility_score || 0,
    supportScore:
      result.value?.unpaid_care_analysis?.work_life_measures?.support_score ||
      0,
    gaps: result.value?.unpaid_care_analysis?.work_life_measures?.gaps || [],
    recommendations:
      result.value?.unpaid_care_analysis?.work_life_measures?.recommendations ||
      [],
  },
  economicImpact: {
    careerProgression:
      result.value?.unpaid_care_analysis?.economic_impact?.career_progression ||
      "",
    compensationEffects:
      result.value?.unpaid_care_analysis?.economic_impact
        ?.compensation_effects || [],
    mitigationStrategies:
      result.value?.unpaid_care_analysis?.economic_impact
        ?.mitigation_strategies || [],
  },
}));

const policyMetrics = computed(() => ({
  currentPolicies: {
    strengths:
      result.value?.policy_recommendations?.current_policies?.strengths || [],
    weaknesses:
      result.value?.policy_recommendations?.current_policies?.weaknesses || [],
    implementationScore:
      result.value?.policy_recommendations?.current_policies
        ?.implementation_score || 0,
  },
  recommendedPolicies:
    result.value?.policy_recommendations?.recommended_policies || [],
  resourceImplications: {
    requiredResources:
      result.value?.policy_recommendations?.resource_implications
        ?.required_resources || [],
    potentialChallenges:
      result.value?.policy_recommendations?.resource_implications
        ?.potential_challenges || [],
    mitigationStrategies:
      result.value?.policy_recommendations?.resource_implications
        ?.mitigation_strategies || [],
  },
  monitoringFramework: {
    metrics:
      result.value?.policy_recommendations?.monitoring_framework?.metrics || [],
    dataNeeds:
      result.value?.policy_recommendations?.monitoring_framework?.data_needs ||
      [],
    reviewFrequency:
      result.value?.policy_recommendations?.monitoring_framework
        ?.review_frequency || "",
  },
}));

// Workplace Equity Metrics
const workplaceEquityScore = computed(() => {
  const { leadershipScore, advancementBarriers, workLifeAssumptions } =
    workplaceMetrics.value;
  return (
    (leadershipScore +
      (100 - advancementBarriers.length) +
      (100 - workLifeAssumptions.length)) /
    3
  );
});

// Safety Assessment Metrics
const safetyAssessmentScore = computed(() => {
  const {
    psychologicalSafetyScore,
    harassmentIndicators,
    underminingLanguage,
  } = safetyMetrics.value;
  return (
    (psychologicalSafetyScore +
      (100 - harassmentIndicators.length) +
      (100 - underminingLanguage.length)) /
    3
  );
});

// Empowerment Opportunities Metrics
const empowermentOpportunitiesScore = computed(() => {
  const { growthLanguage, mentorshipOpportunities, inclusiveAlternatives } =
    empowermentMetrics.value;
  return (
    (growthLanguage.length +
      mentorshipOpportunities.length +
      inclusiveAlternatives.length) /
    3
  );
});

// Violence Prevention Metrics
const violencePreventionScore = computed(() => {
  const { overallSafetyScore, riskIndicators, safetyMeasures } =
    violencePreventionMetrics.value;
  return (
    (overallSafetyScore +
      (100 - riskIndicators.length) +
      (100 - safetyMeasures.gaps.length)) /
    3
  );
});

// Care Work Metrics
const careWorkScore = computed(() => {
  const {
    careRecognitionScore,
    careResponsibilities,
    workLifeMeasures,
    economicImpact,
  } = careWorkMetrics.value;
  return (
    (careRecognitionScore +
      (100 - careResponsibilities.length) +
      workLifeMeasures.flexibilityScore +
      workLifeMeasures.supportScore) /
    4
  );
});

// Policy Implementation Metrics
const policyImplementationScore = computed(() => {
  const { currentPolicies, recommendedPolicies } = policyMetrics.value;
  return (
    (currentPolicies.implementationScore + (100 - recommendedPolicies.length)) /
    2
  );
});

// Chart Data for each Metric Section
const biasChartData = computed(() => ({
  labels: ["Bias Score", "Explicit Biases", "Implicit Biases", "Stereotypes"],
  datasets: [
    {
      label: "Bias Detection",
      data: [
        biasMetrics.value.biasScore,
        biasMetrics.value.explicitBiases.length,
        biasMetrics.value.implicitBiases.length,
        biasMetrics.value.stereotypes.length,
      ],
      backgroundColor: ["#FF7043", "#FFB74D", "#FFEB3B", "#8BC34A"],
      borderColor: ["#D32F2F", "#F57C00", "#FBC02D", "#388E3C"],
      borderWidth: 1,
    },
  ],
}));

const representationChartData = computed(() => ({
  labels: [
    "Visibility Score",
    "Agency Score",
    "Power Dynamics",
    "Improvement Areas",
  ],
  datasets: [
    {
      label: "Representation Analysis",
      data: [
        representationMetrics.value.visibilityScore,
        representationMetrics.value.agencyScore,
        representationMetrics.value.powerDynamics.length,
        representationMetrics.value.improvementAreas.length,
      ],
      backgroundColor: ["#42A5F5", "#66BB6A", "#FFEB3B", "#FF7043"],
      borderColor: ["#1E88E5", "#43A047", "#FBC02D", "#D32F2F"],
      borderWidth: 1,
    },
  ],
}));

const workplaceEquityChartData = computed(() => ({
  labels: ["Workplace Equity"],
  datasets: [
    {
      label: "Workplace Equity",
      data: [workplaceEquityScore.value],
      backgroundColor: ["#42A5F5"],
      borderColor: ["#1E88E5"],
      borderWidth: 1,
    },
  ],
}));

const safetyAssessmentChartData = computed(() => ({
  labels: ["Safety Assessment"],
  datasets: [
    {
      label: "Safety Assessment",
      data: [safetyAssessmentScore.value],
      backgroundColor: ["#66BB6A"],
      borderColor: ["#388E3C"],
      borderWidth: 1,
    },
  ],
}));

const empowermentOpportunitiesChartData = computed(() => ({
  labels: ["Empowerment Opportunities"],
  datasets: [
    {
      label: "Empowerment Opportunities",
      data: [empowermentOpportunitiesScore.value],
      backgroundColor: ["#FFEB3B"],
      borderColor: ["#FBC02D"],
      borderWidth: 1,
    },
  ],
}));

const violencePreventionChartData = computed(() => ({
  labels: ["Violence Prevention"],
  datasets: [
    {
      label: "Violence Prevention",
      data: [violencePreventionScore.value],
      backgroundColor: ["#FF7043"],
      borderColor: ["#D32F2F"],
      borderWidth: 1,
    },
  ],
}));

const careWorkChartData = computed(() => ({
  labels: ["Care Work"],
  datasets: [
    {
      label: "Care Work",
      data: [careWorkScore.value],
      backgroundColor: ["#9575CD"],
      borderColor: ["#673AB7"],
      borderWidth: 1,
    },
  ],
}));

const policyImplementationChartData = computed(() => ({
  labels: ["Policy Implementation"],
  datasets: [
    {
      label: "Policy Implementation",
      data: [policyImplementationScore.value],
      backgroundColor: ["#2196F3"],
      borderColor: ["#1976D2"],
      borderWidth: 1,
    },
  ],
}));

// Chart Data for Equity Metrics
const equityChartData = computed(() => ({
  labels: ["Equity Score"],
  datasets: [
    {
      label: "Equity Assessment",
      data: [overallMetrics.value.equityScore],
      backgroundColor: ["#66BB6A"],
      borderColor: ["#388E3C"],
      borderWidth: 1,
    },
  ],
}));

// Chart options for interactivity and appearance
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    tooltip: {
      backgroundColor: "#fff",
      titleColor: "#333",
      bodyColor: "#333",
      borderColor: "#ccc",
      borderWidth: 1,
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || "";
          if (label) {
            label += ": ";
          }
          label += context.raw;
          return label;
        },
      },
    },
    legend: {
      labels: {
        color: "#333",
      },
    },
  },
  scales: {
    y: {
      ticks: {
        beginAtZero: true,
      },
    },
  },
};
</script>

<style>
* {
  -webkit-line-clamp: unset !important;
  white-space: normal;
}
</style>
