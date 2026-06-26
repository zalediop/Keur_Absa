<template>
  <AppNavbar />
  <main class="auth-page">
    <div class="auth-card fade-in-up">
      <div class="auth-card__logo">
        <div style="width:56px;height:56px;background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:16px;display:grid;place-items:center;font-size:1.75rem;margin:0 auto 1rem">🏨</div>
      </div>
      <h1 class="auth-card__title">Créer un compte</h1>
      <p class="auth-card__subtitle">Rejoignez HotelBookCI et réservez en quelques clics</p>

      <form @submit.prevent="handleRegister" novalidate>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
          <div class="form-group">
            <label class="form-label">Prénom *</label>
            <input v-model="form.first_name" type="text" class="form-control" placeholder="Amadou" required />
          </div>
          <div class="form-group">
            <label class="form-label">Nom *</label>
            <input v-model="form.last_name" type="text" class="form-control" placeholder="Diop" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Nom d'utilisateur *</label>
          <input v-model="form.username" type="text" class="form-control" placeholder="amadou_diop" required />
        </div>
        <div class="form-group">
          <label class="form-label">Email *</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="amadou@example.com" required />
        </div>
        <div class="form-group">
          <label class="form-label">Téléphone</label>
          <input v-model="form.phone" type="tel" class="form-control" placeholder="+221 77 000 00 00" />
        </div>
        <div class="form-group">
          <label class="form-label">Mot de passe *</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="Minimum 8 caractères" required />
        </div>
        <div class="form-group">
          <label class="form-label">Confirmer le mot de passe *</label>
          <input v-model="form.password_confirm" type="password" class="form-control" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn btn--primary btn--full btn--lg mt-2" :disabled="authStore.loading">
          {{ authStore.loading ? 'Inscription…' : 'Créer mon compte' }}
        </button>
      </form>

      <p class="text-center text-muted text-sm mt-3">
        Déjà un compte ?
        <router-link to="/login" class="text-gold">Se connecter</router-link>
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { getDashboardRoute } from '@/utils/formatters';

const router    = useRouter();
const authStore = useAuthStore();
const notif     = useNotificationStore();

const form = ref({
  first_name: '', last_name: '', username: '', email: '',
  phone: '', password: '', password_confirm: '',
});

async function handleRegister() {
  try {
    const res = await authStore.register({ ...form.value });
    notif.showToast('Compte créé ! Bienvenue sur HotelBookCI 🏨', 'success');
    setTimeout(() => router.push(getDashboardRoute(res.user.role)), 800);
  } catch (err) {
    notif.showToast(err.message, 'error');
  }
}
</script>

<style scoped>
.mt-2 { margin-top: .75rem; }
.mt-3 { margin-top: 1rem; }
.text-gold { color: var(--gold-400); }
</style>
