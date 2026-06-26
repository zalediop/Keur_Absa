<template>
  <AppNavbar />
  <main class="auth-page">
    <div class="auth-card fade-in-up">
      <div class="auth-card__logo">
        <div style="width:56px;height:56px;background:var(--navy);border-radius:12px;display:grid;place-items:center;margin:0 auto 1rem">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2"><path d="M3 21h18M3 7v14M21 7v14M16 3H8v4H3M12 11v2M12 17v2M8 11v2M8 17v2M16 11v2M16 17v2"/></svg>
        </div>
      </div>
      <h1 class="auth-card__title">KEUR ABSA</h1>
      <p class="auth-card__subtitle">Hôtel &amp; Résidence — Saly, Sénégal</p>

      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label class="form-label" for="username">Nom d'utilisateur ou email</label>
          <input v-model="form.username" type="text" id="username" class="form-control" placeholder="votre_identifiant" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="password">
            Mot de passe
            <a href="#" style="float:right;font-size:.8rem">Oublié ?</a>
          </label>
          <input v-model="form.password" type="password" id="password" class="form-control" placeholder="••••••••" autocomplete="current-password" required />
        </div>
        <button type="submit" class="btn btn--primary btn--full btn--lg mt-2" :disabled="authStore.loading">
          {{ authStore.loading ? 'Connexion…' : 'Se connecter' }}
        </button>
      </form>

      <div class="auth-divider mt-3 mb-3">ou</div>

      <!-- Comptes de démo -->
      <div style="background:rgba(11,31,58,.04);border:1px solid rgba(11,31,58,.10);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.25rem">
        <p style="font-size:.8rem;color:var(--gray-500);margin-bottom:.75rem;text-align:center">Comptes de démonstration</p>
        <div style="display:flex;flex-direction:column;gap:.5rem">
          <button @click="loginAs('client1','Client1234!')" class="btn btn--outline btn--sm">Client &mdash; client1</button>
          <button @click="loginAs('receptionniste','Recept1234!')" class="btn btn--outline btn--sm">Réceptionniste &mdash; receptionniste</button>
          <button @click="loginAs('admin','Admin1234!')" class="btn btn--navy btn--sm">Administrateur &mdash; admin</button>
        </div>
      </div>

      <p class="text-center text-muted text-sm">
        Pas encore de compte ?
        <router-link to="/register" style="color:var(--gold-dark)">S'inscrire gratuitement</router-link>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { getDashboardRoute } from '@/utils/formatters';

const router    = useRouter();
const route     = useRoute();
const authStore = useAuthStore();
const notif     = useNotificationStore();

const form = ref({ username: '', password: '' });

// Si session expirée
if (route.query.session === 'expired') {
  notif.showToast('Votre session a expiré. Reconnectez-vous.', 'warning');
}

async function handleLogin() {
  try {
    const res = await authStore.login({ username: form.value.username, password: form.value.password });
    notif.showToast(res.message || 'Connexion réussie !', 'success');
    const redirect = route.query.redirect || getDashboardRoute(res.user.role);
    setTimeout(() => router.push(redirect), 600);
  } catch (err) {
    notif.showToast(err.message, 'error');
  }
}

async function loginAs(username, password) {
  form.value = { username, password };
  await handleLogin();
}
</script>

<style scoped>
.mt-2 { margin-top: .75rem; }
.mt-3 { margin-top: 1rem; }
.mb-3 { margin-bottom: 1rem; }
.text-gold { color: var(--gold-400); }
</style>
