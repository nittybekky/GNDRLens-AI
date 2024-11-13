import { defineStore } from "pinia";
import api from "@/services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null,
  }),
  actions: {
    async login(email, password) {
      try {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await api.post("/auth/login", formData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        this.token = response.data.access_token;
        api.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
      } catch (error) {
        console.error("Login failed", error);
      }
    },
    logout() {
      this.token = null;
      delete api.defaults.headers.common["Authorization"];
    },
  },
});
