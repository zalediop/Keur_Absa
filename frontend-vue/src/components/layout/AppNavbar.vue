<template>
  <nav class="navbar">
    <div class="navbar__inner">
      <router-link to="/" class="navbar__brand">
        <div class="navbar__logo-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M3 21h18M3 7v14M21 7v14M16 3H8v4H3M12 11v2M12 17v2M8 11v2M8 17v2M16 11v2M16 17v2"/>
          </svg>
        </div>
        KEUR <span>ABSA</span>
      </router-link>

      <ul class="navbar__nav">
        <li><router-link to="/" active-class="active" exact-active-class="active">Accueil</router-link></li>
        <li><router-link to="/chambres" active-class="active">Chambres</router-link></li>
      </ul>

      <div class="navbar__actions">
        <template v-if="authStore.isAuthenticated">
          <span class="text-muted text-sm" style="color:rgba(255,255,255,.7)">
            Bonjour, <strong style="color:#fff">{{ authStore.user?.first_name || authStore.user?.username }}</strong>
          </span>
          <router-link :to="authStore.dashboardRoute" class="btn btn--outline-white btn--sm">Mon espace</router-link>
          <button class="btn btn--primary btn--sm" @click="handleLogout">Déconnexion</button>
        </template>
        <template v-else>
          <router-link to="/login"    class="btn btn--outline-white btn--sm">Connexion</router-link>
          <router-link to="/register" class="btn btn--primary btn--sm">S'inscrire</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';

const authStore  = useAuthStore();
const notif      = useNotificationStore();
const router     = useRouter();

async function handleLogout() {
  await authStore.logout();
  notif.showToast('Déconnexion réussie.', 'success');
  router.push('/');
}
</script>
