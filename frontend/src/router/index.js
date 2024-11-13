import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/modules/authStore";
import HomeView from "../views/HomeView.vue";
import Analysis from "@/views/Analysis.vue";
import RegisterForm from "@/components/RegisterForm.vue";
import LoginForm from "@/components/LoginForm.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    { path: "/register", component: RegisterForm },
    { path: "/login", component: LoginForm },

    {
      path: "/about",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/AboutView.vue"),
    },
    {
      path: "/analyze",
      name: "analyze",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/Analysis.vue"),
      // beforeEnter: (to, from, next) => {
      //   const authStore = useAuthStore();
      //   if (!authStore.token) {
      //     next("/");
      //   } else {
      //     next();
      //   }
      // },
    },
  ],
});

export default router;
