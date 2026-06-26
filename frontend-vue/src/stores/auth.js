import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI, TokenManager } from '@/services/api';
import { getDashboardRoute } from '@/utils/formatters';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(TokenManager.getUser());
  const loading = ref(false);

  const isAuthenticated = computed(() => !!user.value);
  const isAdmin        = computed(() => user.value?.role === 'admin');
  const isReceptionist = computed(() => ['admin', 'receptionist'].includes(user.value?.role));
  const dashboardRoute = computed(() => getDashboardRoute(user.value?.role));

  async function login(credentials) {
    loading.value = true;
    try {
      const res = await authAPI.login(credentials);
      TokenManager.setTokens(res.tokens.access, res.tokens.refresh);
      TokenManager.setUser(res.user);
      user.value = res.user;
      return res;
    } finally {
      loading.value = false;
    }
  }

  async function register(data) {
    loading.value = true;
    try {
      const res = await authAPI.register(data);
      TokenManager.setTokens(res.tokens.access, res.tokens.refresh);
      TokenManager.setUser(res.user);
      user.value = res.user;
      return res;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      const refresh = TokenManager.getRefresh();
      if (refresh) await authAPI.logout(refresh);
    } catch { /* silencieux */ } finally {
      TokenManager.clearTokens();
      user.value = null;
    }
  }

  function refresh() {
    user.value = TokenManager.getUser();
  }

  return { user, loading, isAuthenticated, isAdmin, isReceptionist, dashboardRoute, login, register, logout, refresh };
});
