<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <input v-model="email" placeholder="Email" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <select v-model="role" required>
        <option value="user">User</option>
        <option value="HR">HR</option>
      </select>
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api";

const email = ref("");
const password = ref("");
const role = ref("user");
const router = useRouter();

const handleRegister = async () => {
  try {
    await api.post("/auth/register", {
      email: email.value,
      password: password.value,
      role: role.value,
    });
    alert("User registered successfully! You can now log in.");
    router.push("/");
  } catch (error) {
    console.error("Registration failed", error);
  }
};
</script>
