<template>
  <v-app>
    <v-main>
      <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
      >
        <v-card class="text-center" max-width="400">
          <v-card-title>
            <span class="headline">Welcome to the GNDRLens AI</span>
          </v-card-title>
          <v-card-subtitle>
            An Advanced Gender-Based Discrimination Prevention & Analysis
            Service
          </v-card-subtitle>
          <v-card-actions class="justify-center">
            <v-btn color="primary" @click="goToAnalyze"> Start Analysis </v-btn>
          </v-card-actions>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

// Function to navigate to the "analyze" route
const goToAnalyze = () => {
  router.push({ name: "analyze" });
};
</script>

<style scoped>
/* Optional: Customize the styling to your preference */
* {
  -webkit-line-clamp: unset !important;
  white-space: normal;
}
.v-container {
  background-color: #f5f5f5;
}
</style>
