<template>
  <AppDashboardNavbar>
    <template #actions>
      <router-link to="/dashboard/admin" v-if="authStore.isAdmin" class="btn btn--outline-white btn--sm">Admin</router-link>
    </template>
  </AppDashboardNavbar>

  <div class="dashboard">
    <aside class="sidebar">
      <div class="sidebar__section">
        <div class="sidebar-user">
          <div class="sidebar-user__label">Connecté en tant que</div>
          <div class="sidebar-user__name">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</div>
          <div class="sidebar-user__role">Réceptionniste</div>
        </div>
        <span class="sidebar__label">Gestion des séjours</span>
        <a href="#" :class="['sidebar__link', activeTab === 'pending' ? 'active' : '']" @click.prevent="setTab('pending')">
          <span class="sidebar__link-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </span> En attente
          <span v-if="stats.pending > 0" style="margin-left:auto;background:var(--gold);color:var(--navy);border-radius:100px;padding:.1rem .45rem;font-size:.72rem;font-weight:700">{{ stats.pending }}</span>
        </a>
        <a href="#" :class="['sidebar__link', activeTab === 'arrivals' ? 'active' : '']" @click.prevent="setTab('arrivals')">
          <span class="sidebar__link-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          </span> Arrivées du jour
          <span v-if="stats.todayArrivals > 0" style="margin-left:auto;background:var(--gold);color:var(--navy);border-radius:100px;padding:.1rem .45rem;font-size:.72rem;font-weight:700">{{ stats.todayArrivals }}</span>
        </a>
        <a href="#" :class="['sidebar__link', activeTab === 'checkins' ? 'active' : '']" @click.prevent="setTab('checkins')">
          <span class="sidebar__link-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M3 7v14M21 7v14M16 3H8v4H3"/></svg>
          </span> Clients présents
          <span v-if="stats.checkedIn > 0" style="margin-left:auto;background:var(--info);color:#fff;border-radius:100px;padding:.1rem .45rem;font-size:.72rem;font-weight:700">{{ stats.checkedIn }}</span>
        </a>
        <a href="#" :class="['sidebar__link', activeTab === 'all' ? 'active' : '']" @click.prevent="setTab('all')">
          <span class="sidebar__link-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          </span> Toutes les réservations
        </a>
      </div>
    </aside>

    <main class="dashboard__main">
      <!-- Stats -->
      <div class="stats-grid mb-4">
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.pending }}</div>
          <div class="stat-card__label">En attente</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.confirmed }}</div>
          <div class="stat-card__label">Confirmées</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.checkedIn }}</div>
          <div class="stat-card__label">Présents</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total }}</div>
          <div class="stat-card__label">Total</div>
        </div>
      </div>

      <!-- ===== RÉSERVATIONS EN ATTENTE ===== -->
      <section v-if="activeTab === 'pending'">
        <div class="dashboard__header">
          <h2>Réservations en attente de confirmation</h2>
          <button @click="setTab('pending')" class="btn btn--outline btn--sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
            Actualiser
          </button>
        </div>
        <div v-if="loadingPending" class="loading"><div class="spinner"></div></div>
        <div v-else-if="pendingRes.length === 0" class="empty-state">
          <div class="empty-state__title">Aucune réservation en attente.</div>
        </div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Arrivée</th><th>Départ</th><th>Montant</th><th>Avance payée</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in pendingRes" :key="r.id">
                <td><strong>#{{ r.id }}</strong></td>
                <td>{{ r.client_detail?.full_name || '—' }}</td>
                <td>{{ r.room_detail?.number ? `N° ${r.room_detail.number}` : '—' }}</td>
                <td>{{ formatDate(r.check_in_date) }}</td>
                <td>{{ formatDate(r.check_out_date) }}</td>
                <td>{{ formatPrice(r.total_price) }}</td>
                <td>
                  <span v-if="r.payment?.status === 'completed'" class="badge badge--green">Oui — {{ formatPrice(r.payment.amount) }}</span>
                  <span v-else class="badge badge--red">Non payée</span>
                </td>
                <td style="display:flex;gap:.5rem">
                  <button @click="confirmRes(r.id)" class="btn btn--success btn--sm">Confirmer</button>
                  <button @click="askCancelRes(r.id)" class="btn btn--danger btn--sm">Annuler</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== ARRIVÉES DU JOUR (check-in) ===== -->
      <section v-if="activeTab === 'arrivals'">
        <div class="dashboard__header">
          <h2>Arrivées du jour — {{ formatDate(today) }}</h2>
          <button @click="setTab('arrivals')" class="btn btn--outline btn--sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
            Actualiser
          </button>
        </div>
        <div style="background:rgba(11,31,58,.05);border:1px solid rgba(11,31,58,.10);border-radius:var(--radius-sm);padding:.875rem 1rem;margin-bottom:1.5rem;font-size:.85rem;color:var(--navy)">
          <strong>Check-in :</strong> Cliquez sur "Check-in" pour enregistrer l'arrivée physique du client. La réservation doit être <strong>confirmée</strong>.
        </div>
        <div v-if="loadingArrivals" class="loading"><div class="spinner"></div></div>
        <div v-else-if="arrivals.length === 0" class="empty-state">
          <div class="empty-state__title">Aucune arrivée prévue aujourd'hui.</div>
          <p class="text-muted text-sm">Les réservations confirmées avec check-in aujourd'hui apparaîtront ici.</p>
        </div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Catégorie</th><th>Personnes</th><th>Montant total</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in arrivals" :key="r.id">
                <td><strong>#{{ r.id }}</strong></td>
                <td>{{ r.client_detail?.full_name || '—' }}</td>
                <td>N° {{ r.room_detail?.number || '—' }}</td>
                <td>{{ r.room_detail?.category_detail?.name || '—' }}</td>
                <td>{{ (r.adults || 0) + (r.children || 0) }} pers.</td>
                <td>{{ formatPrice(r.total_price) }}</td>
                <td>
                  <button @click="openCheckinModal(r)" class="btn btn--primary btn--sm">
                    Check-in
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== CLIENTS PRÉSENTS (check-out) ===== -->
      <section v-if="activeTab === 'checkins'">
        <div class="dashboard__header">
          <h2>Clients présents — Check-out</h2>
          <button @click="setTab('checkins')" class="btn btn--outline btn--sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
            Actualiser
          </button>
        </div>
        <div style="background:rgba(11,31,58,.05);border:1px solid rgba(11,31,58,.10);border-radius:var(--radius-sm);padding:.875rem 1rem;margin-bottom:1.5rem;font-size:.85rem;color:var(--navy)">
          <strong>Check-out :</strong> Enregistrez le départ du client. La chambre sera automatiquement mise en nettoyage.
        </div>
        <div v-if="loadingCheckins" class="loading"><div class="spinner"></div></div>
        <div v-else-if="checkins.length === 0" class="empty-state">
          <div class="empty-state__title">Aucun client en séjour actuellement.</div>
        </div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Arrivé le</th><th>Départ prévu</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in checkins" :key="r.id">
                <td><strong>#{{ r.id }}</strong></td>
                <td>{{ r.client_detail?.full_name || '—' }}</td>
                <td>N° {{ r.room_detail?.number || '—' }}</td>
                <td>{{ r.checkin_record?.checked_in_at ? formatDatetime(r.checkin_record.checked_in_at) : formatDate(r.check_in_date) }}</td>
                <td>
                  <span :style="isLate(r.check_out_date) ? 'color:var(--error);font-weight:600' : ''">
                    {{ formatDate(r.check_out_date) }}
                    <span v-if="isLate(r.check_out_date)" style="font-size:.75rem">(Dépassé)</span>
                  </span>
                </td>
                <td>
                  <button @click="openCheckoutModal(r)" class="btn btn--primary btn--sm">
                    Check-out
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== TOUTES LES RÉSERVATIONS ===== -->
      <section v-if="activeTab === 'all'">
        <div class="dashboard__header"><h2>Toutes les réservations</h2></div>
        <div v-if="loadingAll" class="loading"><div class="spinner"></div></div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Arrivée</th><th>Départ</th><th>Statut</th><th>Montant</th></tr></thead>
            <tbody>
              <tr v-for="r in allRes" :key="r.id">
                <td><strong>#{{ r.id }}</strong></td>
                <td>{{ r.client_detail?.full_name || '—' }}</td>
                <td>{{ r.room_detail?.number ? `N° ${r.room_detail.number}` : '—' }}</td>
                <td>{{ formatDate(r.check_in_date) }}</td>
                <td>{{ formatDate(r.check_out_date) }}</td>
                <td><AppBadge :status="r.status" /></td>
                <td>{{ formatPrice(r.total_price) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>

  <!-- Modal Check-in -->
  <AppModal v-model="showCheckinModal" :title="`Check-in — Chambre ${checkinTarget?.room_detail?.number}`">
    <div v-if="checkinTarget" style="margin-bottom:1.25rem">
      <div style="background:var(--gray-50);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.25rem">
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Client</span>
          <strong>{{ checkinTarget.client_detail?.full_name }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Chambre</span>
          <strong>N° {{ checkinTarget.room_detail?.number }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Départ prévu</span>
          <strong>{{ formatDate(checkinTarget.check_out_date) }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem">
          <span class="text-muted">Solde à encaisser</span>
          <strong style="color:var(--gold-dark)">{{ formatPrice(getBalance(checkinTarget)) }}</strong>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Notes (optionnel)</label>
        <textarea v-model="checkinNotes" class="form-control" rows="2" placeholder="Observations, documents vérifiés…"></textarea>
      </div>
    </div>
    <button class="btn btn--primary btn--full" :disabled="actionLoading" @click="doCheckIn">
      {{ actionLoading ? 'En cours…' : 'Confirmer le Check-in' }}
    </button>
  </AppModal>

  <!-- Modal Check-out -->
  <AppModal v-model="showCheckoutModal" :title="`Check-out — Chambre ${checkoutTarget?.room_detail?.number}`">
    <div v-if="checkoutTarget" style="margin-bottom:1.25rem">
      <div style="background:var(--gray-50);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.25rem">
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Client</span>
          <strong>{{ checkoutTarget.client_detail?.full_name }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Chambre</span>
          <strong>N° {{ checkoutTarget.room_detail?.number }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem">
          <span class="text-muted">Départ prévu</span>
          <strong>{{ formatDate(checkoutTarget.check_out_date) }}</strong>
        </div>
      </div>
      <div style="background:var(--warning-light);border:1px solid rgba(245,127,23,.25);border-radius:var(--radius-sm);padding:.875rem;margin-bottom:1rem;font-size:.85rem">
        <strong>Rappel :</strong> Vérifiez que le client a bien réglé le solde restant avant de procéder au check-out. La chambre passera en statut "nettoyage".
      </div>
      <div class="form-group">
        <label class="form-label">Notes (optionnel)</label>
        <textarea v-model="checkoutNotes" class="form-control" rows="2" placeholder="État de la chambre, objets oubliés…"></textarea>
      </div>
    </div>
    <button class="btn btn--primary btn--full" :disabled="actionLoading" @click="doCheckOut">
      {{ actionLoading ? 'En cours…' : 'Confirmer le Check-out' }}
    </button>
  </AppModal>

  <!-- Modal de confirmation -->
  <AppConfirmModal
    v-model="confirmModal.show"
    :title="confirmModal.title"
    :message="confirmModal.message"
    :type="confirmModal.type"
    :confirmLabel="confirmModal.confirmLabel"
    @confirm="confirmModal.action"
  />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppBadge from '@/components/ui/AppBadge.vue';
import AppModal from '@/components/ui/AppModal.vue';
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue';
import AppDashboardNavbar from '@/components/layout/AppDashboardNavbar.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { reservationsAPI, statsAPI } from '@/services/api';
import { formatDate, formatPrice } from '@/utils/formatters';

const router    = useRouter();
const authStore = useAuthStore();
const notif     = useNotificationStore();

const today     = new Date().toISOString().split('T')[0];
const activeTab = ref('pending');

// Stats
const stats = ref({ pending: 0, confirmed: 0, checkedIn: 0, total: 0, todayArrivals: 0 });

// Données
const pendingRes = ref([]);
const arrivals   = ref([]);
const checkins   = ref([]);
const allRes     = ref([]);

// Loaders
const loadingPending  = ref(false);
const loadingArrivals = ref(false);
const loadingCheckins = ref(false);
const loadingAll      = ref(false);
const actionLoading   = ref(false);

// Modals check-in/out
const showCheckinModal  = ref(false);
const showCheckoutModal = ref(false);
const checkinTarget     = ref(null);
const checkoutTarget    = ref(null);
const checkinNotes      = ref('');
const checkoutNotes     = ref('');

// Modal de confirmation
const confirmModal = ref({
  show: false, title: '', message: '', type: 'danger', confirmLabel: 'Confirmer', action: () => {},
});
function openConfirm({ title, message, type = 'danger', confirmLabel = 'Confirmer', action }) {
  confirmModal.value = { show: true, title, message, type, confirmLabel, action };
}

// Formatage datetime
function formatDatetime(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
}

// Vérifier si le départ est dépassé
function isLate(dateStr) {
  return dateStr && dateStr < today;
}

// Solde restant (total - avance payée)
function getBalance(r) {
  const total = parseFloat(r.total_price || 0);
  const paid  = parseFloat(r.payment?.amount || 0);
  return Math.max(0, total - paid);
}

// ---- Stats (endpoint dédié) ----
async function loadStats() {
  try {
    const data = await statsAPI.getDashboard();
    const r = data.reservations || {};
    stats.value = {
      total:         r.total         || 0,
      pending:       r.pending       || 0,
      confirmed:     r.confirmed     || 0,
      checkedIn:     r.checked_in    || 0,
      todayArrivals: r.today_arrivals || 0,
    };
  } catch (e) { console.warn('loadStats error:', e.message); }
}

// ---- En attente ----
async function loadPending() {
  loadingPending.value = true;
  try {
    const d = await reservationsAPI.getAll({ status: 'pending' });
    pendingRes.value = d.results || d;
  } catch { pendingRes.value = []; }
  finally { loadingPending.value = false; }
}

// ---- Arrivées du jour (status=confirmed & check_in_date=today) — filtré côté API ----
async function loadArrivals() {
  loadingArrivals.value = true;
  try {
    const d = await reservationsAPI.getAll({ status: 'confirmed', check_in_date: today });
    arrivals.value = (d.results || d).filter(r => r.check_in_date === today);
  } catch (e) { console.error(e); arrivals.value = []; }
  finally { loadingArrivals.value = false; }
}

// ---- Clients présents (check-out) ----
async function loadCheckins() {
  loadingCheckins.value = true;
  try {
    const d = await reservationsAPI.getAll({ status: 'checked_in' });
    checkins.value = d.results || d;
  } catch { checkins.value = []; }
  finally { loadingCheckins.value = false; }
}

// ---- Toutes ----
async function loadAll() {
  loadingAll.value = true;
  try {
    const d = await reservationsAPI.getAll();
    allRes.value = d.results || d;
  } catch { allRes.value = []; }
  finally { loadingAll.value = false; }
}

// ---- Confirmer ----
async function confirmRes(id) {
  try {
    await reservationsAPI.confirm(id);
    notif.showToast('Réservation confirmée.', 'success');
    loadPending(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Annuler ----
async function cancelRes(id) {
  try {
    await reservationsAPI.cancel(id);
    notif.showToast('Réservation annulée.', 'success');
    loadPending(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function askCancelRes(id) {
  openConfirm({
    title: 'Annuler la réservation',
    message: 'Cette réservation sera annulée. Le client devra refaire une demande.',
    confirmLabel: 'Annuler la réservation',
    action: () => cancelRes(id),
  });
}

// ---- Modals Check-in ----
function openCheckinModal(r) {
  checkinTarget.value = r;
  checkinNotes.value  = '';
  showCheckinModal.value = true;
}

async function doCheckIn() {
  if (!checkinTarget.value) return;
  actionLoading.value = true;
  try {
    await reservationsAPI.checkIn(checkinTarget.value.id, checkinNotes.value);
    notif.showToast(`Check-in enregistré pour ${checkinTarget.value.client_detail?.full_name}.`, 'success');
    showCheckinModal.value = false;
    loadArrivals(); loadCheckins(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
  finally { actionLoading.value = false; }
}

// ---- Modals Check-out ----
function openCheckoutModal(r) {
  checkoutTarget.value = r;
  checkoutNotes.value  = '';
  showCheckoutModal.value = true;
}

async function doCheckOut() {
  if (!checkoutTarget.value) return;
  actionLoading.value = true;
  try {
    await reservationsAPI.checkOut(checkoutTarget.value.id, checkoutNotes.value);
    notif.showToast(`Check-out enregistré. Chambre en nettoyage.`, 'success');
    showCheckoutModal.value = false;
    loadCheckins(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
  finally { actionLoading.value = false; }
}

// ---- Tab switch ----
function setTab(tab) {
  activeTab.value = tab;
}

watch(activeTab, (tab) => {
  if (tab === 'pending')  loadPending();
  if (tab === 'arrivals') loadArrivals();
  if (tab === 'checkins') loadCheckins();
  if (tab === 'all')      loadAll();
});

onMounted(() => { loadStats(); loadPending(); });
</script>

<style scoped>
.mb-4 { margin-bottom: 1.5rem; }
</style>
