<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="email" placeholder="Email" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/modules/authStore";

const email = ref("");
const password = ref("");
const authStore = useAuthStore();

const handleLogin = async () => {
  await authStore.login(email.value, password.value);
};
</script>
