<template>
  <!-- Navbar dashboard -->
  <AppDashboardNavbar />

  <div class="dashboard">
    <aside class="sidebar">
      <div class="sidebar__section">
        <div class="sidebar-user">
          <div class="sidebar-user__label">Connecté en tant que</div>
          <div class="sidebar-user__name">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</div>
          <div class="sidebar-user__role">Client</div>
        </div>
        <span class="sidebar__label">Mon espace</span>
        <a href="#" class="sidebar__link active">
          <span class="sidebar__link-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
          </span> Mes réservations
        </a>
      </div>
    </aside>

    <main class="dashboard__main">
      <!-- Stats -->
      <div class="stats-grid mb-4">
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total }}</div>
          <div class="stat-card__label">Total réservations</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.confirmed }}</div>
          <div class="stat-card__label">Confirmées</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.pending }}</div>
          <div class="stat-card__label">En attente</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.completed }}</div>
          <div class="stat-card__label">Complétées</div>
        </div>
      </div>

      <div class="dashboard__header">
        <h2>Mes réservations</h2>
        <router-link to="/chambres" class="btn btn--primary btn--sm">+ Nouvelle réservation</router-link>
      </div>

      <!-- Filtres statut -->
      <div style="display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap">
        <button
          v-for="f in statusFilters"
          :key="f.value"
          :class="['btn', 'btn--sm', activeFilter === f.value ? 'btn--primary' : 'btn--outline']"
          @click="setFilter(f.value)"
        >{{ f.label }}</button>
      </div>

      <!-- Liste réservations -->
      <div v-if="loading" class="loading"><div class="spinner"></div>Chargement…</div>
      <div v-else-if="reservations.length === 0" class="empty-state">
        <div class="empty-state__title">Aucune réservation trouvée</div>
        <router-link to="/chambres" class="btn btn--primary mt-2">Réserver une chambre</router-link>
      </div>
      <div v-else class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th><th>Chambre</th><th>Arrivée</th><th>Départ</th>
              <th>Nuits</th><th>Montant</th><th>Statut</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reservations" :key="r.id">
              <td><strong>#{{ r.id }}</strong></td>
              <td>{{ r.room_detail?.number ? `Chambre ${r.room_detail.number}` : '—' }}</td>
              <td>{{ formatDate(r.check_in_date) }}</td>
              <td>{{ formatDate(r.check_out_date) }}</td>
              <td>{{ r.nights }}</td>
              <td>{{ formatPrice(r.total_price) }}</td>
              <td><AppBadge :status="r.status" /></td>
              <td>
                <button
                  v-if="r.is_cancellable"
                  class="btn btn--danger btn--sm"
                  @click="cancelReservation(r.id)"
                >Annuler</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AppBadge from '@/components/ui/AppBadge.vue';
import AppDashboardNavbar from '@/components/layout/AppDashboardNavbar.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { reservationsAPI } from '@/services/api';
import { formatDate, formatPrice } from '@/utils/formatters';

const router    = useRouter();
const authStore = useAuthStore();
const notif     = useNotificationStore();

const reservations = ref([]);
const loading      = ref(true);
const activeFilter = ref('all');
const stats        = ref({ total: 0, confirmed: 0, pending: 0, completed: 0 });

const statusFilters = [
  { label: 'Toutes', value: 'all' },
  { label: 'En attente', value: 'pending' },
  { label: 'Confirmées', value: 'confirmed' },
  { label: 'Arrivé', value: 'checked_in' },
  { label: 'Annulées', value: 'cancelled' },
];

async function loadReservations() {
  loading.value = true;
  try {
    const params = activeFilter.value !== 'all' ? { status: activeFilter.value } : {};
    const data = await reservationsAPI.getAll(params);
    reservations.value = data.results || data;
    if (activeFilter.value === 'all') {
      const all = reservations.value;
      stats.value = {
        total:     all.length,
        confirmed: all.filter(r => ['confirmed','checked_in'].includes(r.status)).length,
        pending:   all.filter(r => r.status === 'pending').length,
        completed: all.filter(r => r.status === 'checked_out').length,
      };
    }
  } catch { /* silencieux */ }
  finally { loading.value = false; }
}

function setFilter(val) {
  activeFilter.value = val;
  loadReservations();
}

async function cancelReservation(id) {
  if (!confirm('Confirmer l\'annulation de cette réservation ?')) return;
  try {
    await reservationsAPI.cancel(id);
    notif.showToast('Réservation annulée.', 'success');
    loadReservations();
  } catch (err) { notif.showToast(err.message, 'error'); }
}

async function handleLogout() {
  await authStore.logout();
  notif.showToast('Déconnexion réussie.', 'success');
  router.push('/');
}

onMounted(loadReservations);
</script>

<style scoped>
.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: .75rem; }
</style>
