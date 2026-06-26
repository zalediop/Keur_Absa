<template>
  <AppNavbar />
  <main style="padding-top:80px;min-height:100vh">
    <div class="container" style="padding:2rem 1.5rem 4rem">
      <div v-if="loading" class="loading"><div class="spinner"></div>Chargement de la chambre…</div>
      <div v-else-if="error" class="empty-state">
        <p class="text-muted">{{ error }}</p>
        <router-link to="/chambres" class="btn btn--primary mt-2">Retour aux chambres</router-link>
      </div>
      <template v-else>
        <div style="display:grid;grid-template-columns:1fr 400px;gap:2rem;align-items:start">
          <!-- Détails chambre -->
          <div>
            <div class="card" style="padding:0;overflow:hidden;margin-bottom:1.5rem">
              <img
                :src="roomImageUrl"
                :alt="room?.category_detail?.name"
                style="width:100%;height:300px;object-fit:cover"
              />
              <div class="card__body">
                <h1 style="font-size:1.75rem;margin-bottom:.5rem">Chambre {{ room?.number }}</h1>
                <p class="text-muted">{{ room?.category_detail?.name }} · Étage {{ room?.floor }}</p>
                <div class="card__price mt-2">{{ formatPrice(room?.category_detail?.base_price) }} <span>/ nuit</span></div>
                <div class="amenities mt-2">
                  <span v-for="a in (room?.category_detail?.amenities || [])" :key="a" class="amenity">{{ a }}</span>
                </div>
              </div>
            </div>

            <!-- Info paiement avance -->
            <div style="background:var(--navy);color:#fff;border-radius:var(--radius-md);padding:1.5rem">
              <div style="font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:var(--gold);font-weight:700;margin-bottom:.75rem">
                Comment ça marche ?
              </div>
              <div style="display:flex;flex-direction:column;gap:.875rem">
                <div style="display:flex;gap:.875rem;align-items:flex-start">
                  <div style="min-width:32px;height:32px;background:var(--gold);border-radius:50%;display:grid;place-items:center;font-weight:700;color:var(--navy);font-size:.85rem">1</div>
                  <div>
                    <div style="font-weight:600;margin-bottom:.2rem">Réservez</div>
                    <div style="font-size:.85rem;color:rgba(255,255,255,.7)">Remplissez le formulaire avec vos dates</div>
                  </div>
                </div>
                <div style="display:flex;gap:.875rem;align-items:flex-start">
                  <div style="min-width:32px;height:32px;background:var(--gold);border-radius:50%;display:grid;place-items:center;font-weight:700;color:var(--navy);font-size:.85rem">2</div>
                  <div>
                    <div style="font-weight:600;margin-bottom:.2rem">Payez 5% d'avance</div>
                    <div style="font-size:.85rem;color:rgba(255,255,255,.7)">Wave, Orange Money, Free Money ou carte bancaire</div>
                  </div>
                </div>
                <div style="display:flex;gap:.875rem;align-items:flex-start">
                  <div style="min-width:32px;height:32px;background:var(--gold);border-radius:50%;display:grid;place-items:center;font-weight:700;color:var(--navy);font-size:.85rem">3</div>
                  <div>
                    <div style="font-weight:600;margin-bottom:.2rem">Arrivez à l'hôtel</div>
                    <div style="font-size:.85rem;color:rgba(255,255,255,.7)">Réglez le solde restant à la réception</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Formulaire réservation -->
          <div>
            <!-- Si déjà réservé, afficher infos paiement -->
            <template v-if="newReservation">
              <div class="card">
                <div class="card__body">
                  <div style="text-align:center;padding:1rem 0 1.5rem">
                    <div style="width:64px;height:64px;background:var(--success-light);border-radius:50%;display:grid;place-items:center;margin:0 auto .875rem">
                      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <h2 style="font-size:1.25rem;margin-bottom:.5rem">Réservation créée !</h2>
                    <p class="text-muted text-sm">Référence #{{ newReservation.id }}</p>
                  </div>

                  <!-- Récap -->
                  <div style="background:var(--gray-50);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.25rem">
                    <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
                      <span class="text-muted">Chambre</span>
                      <strong>N° {{ room?.number }}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
                      <span class="text-muted">Arrivée</span>
                      <strong>{{ formatDate(newReservation.check_in_date) }}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
                      <span class="text-muted">Départ</span>
                      <strong>{{ formatDate(newReservation.check_out_date) }}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
                      <span class="text-muted">{{ newReservation.nights }} nuit(s)</span>
                      <strong style="color:var(--gold-dark)">{{ formatPrice(newReservation.total_price) }}</strong>
                    </div>
                    <hr style="border:none;border-top:1px solid var(--gray-200);margin:.75rem 0">
                    <div style="display:flex;justify-content:space-between;font-size:.95rem">
                      <span class="text-muted">Avance requise (5%)</span>
                      <strong style="color:var(--navy);font-size:1.1rem">{{ formatPrice(advanceAmount) }}</strong>
                    </div>
                  </div>

                  <button class="btn btn--primary btn--full btn--lg" @click="showPaymentModal = true">
                    Payer l'avance — {{ formatPrice(advanceAmount) }}
                  </button>
                  <p class="text-center text-muted text-sm mt-2">Solde de {{ formatPrice(balanceAmount) }} à régler à l'hôtel</p>
                </div>
              </div>
            </template>

            <!-- Formulaire initial -->
            <template v-else>
              <div class="card">
                <div class="card__body">
                  <h2 style="margin-bottom:1.5rem">Réserver cette chambre</h2>
                  <form @submit.prevent="handleReservation">
                    <div class="form-group">
                      <label class="form-label">Date d'arrivée *</label>
                      <input v-model="resaForm.check_in_date" type="date" class="form-control" :min="today" required />
                    </div>
                    <div class="form-group">
                      <label class="form-label">Date de départ *</label>
                      <input v-model="resaForm.check_out_date" type="date" class="form-control" :min="minCheckOut" required />
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
                      <div class="form-group">
                        <label class="form-label">Adultes *</label>
                        <input v-model.number="resaForm.adults" type="number" class="form-control" min="1" max="10" required />
                      </div>
                      <div class="form-group">
                        <label class="form-label">Enfants</label>
                        <input v-model.number="resaForm.children" type="number" class="form-control" min="0" max="10" />
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Demandes spéciales</label>
                      <textarea v-model="resaForm.special_requests" class="form-control" rows="2" placeholder="Lit bébé, chambre calme…"></textarea>
                    </div>

                    <!-- Récap prix -->
                    <div v-if="nights > 0" style="background:rgba(212,160,23,.08);border:1px solid rgba(212,160,23,.20);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.25rem">
                      <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
                        <span class="text-muted">{{ nights }} nuit(s) × {{ formatPrice(room?.category_detail?.base_price) }}</span>
                        <strong>{{ formatPrice(room?.category_detail?.base_price * nights) }}</strong>
                      </div>
                      <div style="display:flex;justify-content:space-between;font-size:.9rem">
                        <span class="text-muted">Avance de 5%</span>
                        <strong style="color:var(--gold-dark)">{{ formatPrice(Math.ceil(room?.category_detail?.base_price * nights * 0.05)) }}</strong>
                      </div>
                    </div>

                    <button type="submit" class="btn btn--primary btn--full btn--lg" :disabled="submitting">
                      {{ submitting ? 'Création…' : 'Créer la réservation' }}
                    </button>
                  </form>
                </div>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
  </main>

  <!-- Modal paiement -->
  <PaymentModal
    v-model="showPaymentModal"
    :reservation="newReservation"
    @paid="onPaid"
  />

  <AppFooter />
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import PaymentModal from '@/components/ui/PaymentModal.vue';
import { roomsAPI, reservationsAPI } from '@/services/api';
import { formatPrice, formatDate } from '@/utils/formatters';
import { useNotificationStore } from '@/stores/notification';

const route    = useRoute();
const router   = useRouter();
const notif    = useNotificationStore();

const room            = ref(null);
const loading         = ref(true);
const error           = ref('');
const submitting      = ref(false);
const newReservation  = ref(null);   // réservation créée → attente paiement
const showPaymentModal = ref(false);

const today    = new Date().toISOString().split('T')[0];
const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

const resaForm = ref({
  check_in_date: tomorrow, check_out_date: '', adults: 1, children: 0, special_requests: '',
});

const minCheckOut = computed(() => {
  if (!resaForm.value.check_in_date) return today;
  const d = new Date(resaForm.value.check_in_date);
  d.setDate(d.getDate() + 1);
  return d.toISOString().split('T')[0];
});

const nights = computed(() => {
  if (!resaForm.value.check_in_date || !resaForm.value.check_out_date) return 0;
  const diff = new Date(resaForm.value.check_out_date) - new Date(resaForm.value.check_in_date);
  return Math.max(0, Math.ceil(diff / 86400000));
});

// Montants avance
// On calcule localement si total_price est 0 ou absent (protection contre bug API)
const computedTotal = computed(() => {
  const apiTotal = parseFloat(newReservation.value?.total_price || 0);
  if (apiTotal > 0) return apiTotal;
  // Fallback : calcul local avec le prix de base × nuits
  const basePrice = parseFloat(room.value?.category_detail?.base_price || 0);
  const n = newReservation.value?.nights || nights.value;
  return basePrice * n;
});

const advanceAmount = computed(() => {
  return Math.ceil(computedTotal.value * 0.05);
});
const balanceAmount = computed(() => {
  return computedTotal.value - advanceAmount.value;
});

watch(() => resaForm.value.check_in_date, (val) => {
  const d = new Date(val); d.setDate(d.getDate() + 1);
  resaForm.value.check_out_date = d.toISOString().split('T')[0];
});

// Image de la chambre : priorité image_url chambre > image_url catégorie > fallback
const fallbackImg = '/placeholder-room.jpg';
const roomImageUrl = computed(() => {
  if (room.value?.image_url) return room.value.image_url;
  if (room.value?.category_detail?.image_url) return room.value.category_detail.image_url;
  return fallbackImg;
});

onMounted(async () => {
  try {
    room.value = await roomsAPI.getRoom(route.params.id);
  } catch (e) {
    error.value = e.message || 'Chambre introuvable.';
  } finally {
    loading.value = false;
  }
});

async function handleReservation() {
  submitting.value = true;
  try {
    const res = await reservationsAPI.create({
      room:             room.value.id,
      check_in_date:    resaForm.value.check_in_date,
      check_out_date:   resaForm.value.check_out_date,
      adults:           resaForm.value.adults,
      children:         resaForm.value.children,
      special_requests: resaForm.value.special_requests,
    });
    newReservation.value = res;
    notif.showToast('Réservation créée ! Procédez au paiement de l\'avance.', 'success');
  } catch (err) {
    notif.showToast(err.message, 'error');
  } finally {
    submitting.value = false;
  }
}

function onPaid() {
  notif.showToast('Réservation confirmée ! Bienvenue à KEUR ABSA.', 'success');
  setTimeout(() => router.push('/dashboard/client'), 1500);
}
</script>

<style scoped>
.mt-2 { margin-top: .75rem; }
</style>
