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

      <div></div>

      <div class="navbar__actions">
        <slot name="actions">
          <!-- Actions par defaut : afficher le nom utilisateur -->
          <span v-if="showGreeting" class="text-muted text-sm">
            Bonjour, <strong style="color:#fff">{{ authStore.user?.first_name || authStore.user?.username }}</strong>
          </span>
        </slot>
        <button @click="handleLogout" class="btn btn--outline-white btn--sm">Deconnexion</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';

defineProps({
  showGreeting: { type: Boolean, default: true },
});

const authStore = useAuthStore();
const notif     = useNotificationStore();
const router    = useRouter();

async function handleLogout() {
  await authStore.logout();
  notif.showToast('Deconnexion reussie.', 'success');
  router.push('/');
}
</script>
