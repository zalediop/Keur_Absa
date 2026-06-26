<template>
  <AppDashboardNavbar>
    <template #actions>
      <a href="http://127.0.0.1:8000/api/schema/swagger-ui/" target="_blank" class="btn btn--outline-white btn--sm">API Docs</a>
    </template>
  </AppDashboardNavbar>

  <div class="dashboard">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar__section">
        <div class="sidebar-user">
          <div class="sidebar-user__label">Connecté en tant que</div>
          <div class="sidebar-user__name">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</div>
          <div class="sidebar-user__role">Administrateur</div>
        </div>
        <span class="sidebar__label">Gestion hôtelière</span>
        <a href="#" v-for="tab in tabs" :key="tab.key"
          :class="['sidebar__link', activeTab === tab.key ? 'active' : '']"
          @click.prevent="activeTab = tab.key"
        >
          <span class="sidebar__link-icon" v-html="tab.icon"></span> {{ tab.label }}
        </a>
      </div>
    </aside>

    <main class="dashboard__main">
      <!-- Stats globales -->
      <div class="stats-grid mb-4">
        <div class="stat-card"><div class="stat-card__value">{{ stats.totalRooms }}</div><div class="stat-card__label">Total chambres</div></div>
        <div class="stat-card"><div class="stat-card__value">{{ stats.occupied }}</div><div class="stat-card__label">Occupées</div></div>
        <div class="stat-card"><div class="stat-card__value">{{ stats.totalReservations }}</div><div class="stat-card__label">Réservations</div></div>
        <div class="stat-card"><div class="stat-card__value" style="font-size:1.25rem">{{ stats.revenue }}</div><div class="stat-card__label">Revenu total</div></div>
      </div>

      <!-- ===== CHAMBRES ===== -->
      <section v-show="activeTab === 'rooms'">
        <div class="dashboard__header"><h2>Gestion des Chambres</h2></div>
        <div class="card mb-4">
          <div class="card__body">
            <h3 style="margin-bottom:1.25rem">Ajouter une chambre</h3>
            <form @submit.prevent="addRoom">
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:1rem;align-items:end;margin-bottom:1rem">
                <div class="form-group" style="margin:0">
                  <label class="form-label">Numéro *</label>
                  <input v-model="roomForm.number" type="text" class="form-control" placeholder="Ex: 104" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Étage *</label>
                  <input v-model.number="roomForm.floor" type="number" class="form-control" placeholder="1" min="0" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Catégorie *</label>
                  <select v-model.number="roomForm.category" class="form-control" required>
                    <option value="">Sélectionner…</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
                <button type="submit" class="btn btn--primary">Ajouter</button>
              </div>
              <div class="form-group" style="margin:0">
                <label class="form-label">Photo de la chambre</label>
                <input
                  type="file" accept="image/*" class="form-control"
                  @change="roomForm.imageFile = $event.target.files[0]"
                  style="cursor:pointer"
                />
                <div v-if="roomForm.imageFile" style="font-size:.8rem;color:var(--gray-500);margin-top:.3rem">
                  🖼️ {{ roomForm.imageFile.name }}
                </div>
              </div>
            </form>
          </div>
        </div>
        <div v-if="loadingRooms" class="loading"><div class="spinner"></div></div>
        <div v-else class="table-wrapper">
          <!-- Recherche chambres -->
          <div style="margin-bottom:1rem">
            <input v-model="roomSearch" type="text" class="form-control" placeholder="🔍 Rechercher par numéro, étage ou catégorie…" style="max-width:380px" />
          </div>
          <table>
            <thead><tr><th>N°</th><th>Photo</th><th>Étage</th><th>Catégorie</th><th>Statut</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in filteredRooms" :key="r.id">
                <td><strong>{{ r.number }}</strong></td>
                <td>
                  <div v-if="r.image_url" style="width:48px;height:36px;border-radius:4px;overflow:hidden">
                    <img :src="r.image_url" style="width:100%;height:100%;object-fit:cover" />
                  </div>
                  <label v-else style="cursor:pointer">
                    <span class="btn btn--outline btn--sm" style="font-size:.72rem">🖼️ Photo</span>
                    <input type="file" accept="image/*" style="display:none" @change="uploadRoomPhoto(r.id, $event)" />
                  </label>
                </td>
                <td>{{ r.floor }}</td>
                <td>{{ r.category_detail?.name || '—' }}</td>
                <td>
                  <span :class="['badge', r.status === 'available' ? 'badge--green' : r.status === 'maintenance' ? 'badge--red' : 'badge--blue']">
                    {{ r.status }}
                  </span>
                </td>
                <td style="display:flex;gap:.5rem;flex-wrap:wrap">
                  <button @click="openEditRoom(r)" class="btn btn--primary btn--sm">Modifier</button>
                  <label style="cursor:pointer">
                    <span class="btn btn--outline btn--sm">🖼️ Photo</span>
                    <input type="file" accept="image/*" style="display:none" @change="uploadRoomPhoto(r.id, $event)" />
                  </label>
                  <button @click="askDeleteRoom(r.id)" class="btn btn--danger btn--sm">Supprimer</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== TARIFS ===== -->
      <section v-show="activeTab === 'rates'">
        <div class="dashboard__header"><h2>Tarifs Saisonniers</h2></div>
        <div class="card mb-4">
          <div class="card__body">
            <h3 style="margin-bottom:1.25rem">Définir un tarif saisonnier</h3>
            <form @submit.prevent="addRate">
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr auto;gap:1rem;align-items:end">
                <div class="form-group" style="margin:0">
                  <label class="form-label">Catégorie *</label>
                  <select v-model.number="rateForm.category" class="form-control" required>
                    <option value="">Sélectionner…</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Nom de la saison *</label>
                  <input v-model="rateForm.name" type="text" class="form-control" placeholder="Haute saison" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Début *</label>
                  <input v-model="rateForm.start_date" type="date" class="form-control" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Fin *</label>
                  <input v-model="rateForm.end_date" type="date" class="form-control" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Prix/nuit (FCFA) *</label>
                  <input v-model.number="rateForm.price_per_night" type="number" class="form-control" placeholder="50000" required />
                </div>
                <button type="submit" class="btn btn--primary">Créer</button>
              </div>
            </form>
          </div>
        </div>
        <div v-if="loadingRates" class="loading"><div class="spinner"></div></div>
        <p v-else-if="rates.length === 0" class="text-muted">Aucun tarif saisonnier défini.</p>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>Saison</th><th>Catégorie</th><th>Du</th><th>Au</th><th>Prix/nuit</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in rates" :key="r.id">
                <td><strong>{{ r.name }}</strong></td>
                <td>{{ r.category_name }}</td>
                <td>{{ formatDate(r.start_date) }}</td>
                <td>{{ formatDate(r.end_date) }}</td>
                <td class="text-gold">{{ formatPrice(r.price_per_night) }}</td>
                <td><button @click="askDeleteRate(r.id)" class="btn btn--danger btn--sm">Supprimer</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== RÉSERVATIONS ===== -->
      <section v-show="activeTab === 'reservations'">
        <div class="dashboard__header"><h2>Toutes les réservations</h2></div>
        <!-- Recherche réservations -->
        <div style="margin-bottom:1rem">
          <input v-model="resSearch" type="text" class="form-control" placeholder="🔍 Rechercher par client, chambre ou statut…" style="max-width:380px" />
        </div>
        <div v-if="loadingAllRes" class="loading"><div class="spinner"></div></div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Arrivée</th><th>Départ</th><th>Statut</th><th>Montant</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="r in filteredReservations" :key="r.id">
                <td>#{{ r.id }}</td>
                <td>{{ r.client_detail?.full_name || '—' }}</td>
                <td>{{ r.room_detail?.number || '—' }}</td>
                <td>{{ formatDate(r.check_in_date) }}</td>
                <td>{{ formatDate(r.check_out_date) }}</td>
                <td><AppBadge :status="r.status" /></td>
                <td>{{ formatPrice(r.total_price) }}</td>
                <td style="display:flex;gap:.5rem">
                  <button v-if="r.status === 'pending'" @click="confirmRes(r.id)" class="btn btn--success btn--sm">Confirmer</button>
                  <button v-if="r.is_cancellable" @click="askCancelRes(r.id)" class="btn btn--danger btn--sm">Annuler</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== CATÉGORIES ===== -->
      <section v-show="activeTab === 'categories'">
        <div class="dashboard__header"><h2>Gestion des Catégories</h2></div>
        <div class="card mb-4">
          <div class="card__body">
            <h3 style="margin-bottom:1.25rem">Ajouter une catégorie</h3>
            <form @submit.prevent="addCategory">
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:1rem;align-items:end">
                <div class="form-group" style="margin:0">
                  <label class="form-label">Nom *</label>
                  <input v-model="catForm.name" type="text" class="form-control" placeholder="Ex: Chambre Double Standard" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Prix de base (FCFA) *</label>
                  <input v-model.number="catForm.base_price" type="number" class="form-control" placeholder="55000" required />
                </div>
                <div class="form-group" style="margin:0">
                  <label class="form-label">Capacité max *</label>
                  <input v-model.number="catForm.max_occupancy" type="number" class="form-control" placeholder="2" min="1" required />
                </div>
                <button type="submit" class="btn btn--primary">Ajouter</button>
              </div>
              <div class="form-group mt-2">
                <label class="form-label">Description *</label>
                <textarea v-model="catForm.description" class="form-control" rows="2" placeholder="Description de la catégorie..." required></textarea>
              </div>
              <div class="form-group mt-2">
                <label class="form-label">Photo de la catégorie</label>
                <input
                  type="file" accept="image/*" class="form-control"
                  @change="catForm.imageFile = $event.target.files[0]"
                  style="cursor:pointer"
                />
                <div v-if="catForm.imageFile" style="font-size:.8rem;color:var(--gray-500);margin-top:.3rem">
                  🖼️ {{ catForm.imageFile.name }}
                </div>
              </div>
            </form>
          </div>
        </div>
        <div v-if="loadingCats" class="loading"><div class="spinner"></div></div>
        <div v-else class="table-wrapper">
          <table>
            <thead><tr><th>ID</th><th>Photo</th><th>Nom</th><th>Prix de base</th><th>Capacité Max</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="c in categories" :key="c.id">
                <td>#{{ c.id }}</td>
                <td>
                  <div v-if="c.image_url" style="width:48px;height:36px;border-radius:4px;overflow:hidden">
                    <img :src="c.image_url" style="width:100%;height:100%;object-fit:cover" />
                  </div>
                  <span v-else style="color:var(--gray-400);font-size:.8rem">Aucune</span>
                </td>
                <td><strong>{{ c.name }}</strong></td>
                <td>{{ formatPrice(c.base_price) }}</td>
                <td>👥 {{ c.max_occupancy }} pers.</td>
                <td style="display:flex;gap:.5rem;flex-wrap:wrap">
                  <button @click="openEditCategory(c)" class="btn btn--primary btn--sm">Modifier</button>
                  <button @click="askDeleteCategory(c.id)" class="btn btn--danger btn--sm">Supprimer</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===== UTILISATEURS ===== -->
      <section v-show="activeTab === 'users'">
        <div class="dashboard__header">
          <h2>Gestion des Utilisateurs</h2>
          <p class="text-muted text-sm">Modifiez les rôles directement dans le tableau</p>
        </div>
        <div v-if="loadingUsers" class="loading"><div class="spinner"></div></div>
        <div v-else class="table-wrapper">
          <!-- Recherche utilisateurs -->
          <div style="margin-bottom:1rem">
            <input v-model="userSearch" type="text" class="form-control" placeholder="🔍 Rechercher par nom, email…" style="max-width:380px" />
          </div>
          <table>
            <thead><tr><th>ID</th><th>Nom</th><th>Email</th><th>Rôle</th><th>Réservations</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-for="u in filteredUsers" :key="u.id">
                <td>#{{ u.id }}</td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <select @change="changeRole(u.id, $event.target.value)" class="form-control" style="width:auto;padding:.3rem .6rem;font-size:.8rem">
                    <option value="client"       :selected="u.role === 'client'">Client</option>
                    <option value="receptionist" :selected="u.role === 'receptionist'">Réceptionniste</option>
                    <option value="admin"        :selected="u.role === 'admin'">Admin</option>
                  </select>
                </td>
                <td>{{ u.reservations_count }}</td>
                <td>
                  <button
                    @click="askDeleteUser(u.id)"
                    class="btn btn--danger btn--sm"
                    :disabled="u.id === authStore.user?.id"
                    :title="u.id === authStore.user?.id ? 'Impossible de supprimer votre propre compte' : ''"
                  >Supprimer</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>

  <!-- Modals de confirmation -->
  <AppConfirmModal
    v-model="confirmModal.show"
    :title="confirmModal.title"
    :message="confirmModal.message"
    :type="confirmModal.type"
    :confirmLabel="confirmModal.confirmLabel"
    @confirm="confirmModal.action"
  />

  <!-- Modal édition chambre -->
  <AppModal v-model="showRoomModal" :title="`Modifier la Chambre ${editRoom?.number}`">
    <form @submit.prevent="updateRoom">
      <div class="form-group">
        <label class="form-label">Numéro</label>
        <input v-model="editRoom.number" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label class="form-label">Étage</label>
        <input v-model.number="editRoom.floor" type="number" class="form-control" required />
      </div>
      <div class="form-group">
        <label class="form-label">Catégorie</label>
        <select v-model.number="editRoom.category" class="form-control" required>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Statut</label>
        <select v-model="editRoom.status" class="form-control" required>
          <option value="available">Disponible</option>
          <option value="occupied">Occupée</option>
          <option value="maintenance">En maintenance</option>
          <option value="cleaning">En nettoyage</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Photo de la chambre</label>
        <div v-if="editRoom.image_url" style="margin-bottom:.5rem">
          <img :src="editRoom.image_url" style="width:100%;height:120px;object-fit:cover;border-radius:var(--radius-sm)" />
        </div>
        <input
          type="file" accept="image/*" class="form-control"
          @change="editRoom.imageFile = $event.target.files[0]"
          style="cursor:pointer"
        />
        <div v-if="editRoom.imageFile" style="font-size:.8rem;color:var(--gray-500);margin-top:.3rem">
          🖼️ {{ editRoom.imageFile.name }}
        </div>
      </div>
      <button type="submit" class="btn btn--primary btn--full mt-2">Enregistrer</button>
    </form>
  </AppModal>

  <!-- Modal édition catégorie -->
  <AppModal v-model="showCatModal" :title="`Modifier la Catégorie #${editCat?.id}`">
    <form @submit.prevent="updateCategory">
      <div class="form-group">
        <label class="form-label">Nom</label>
        <input v-model="editCat.name" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label class="form-label">Prix de base (FCFA)</label>
        <input v-model.number="editCat.base_price" type="number" class="form-control" required />
      </div>
      <div class="form-group">
        <label class="form-label">Capacité max</label>
        <input v-model.number="editCat.max_occupancy" type="number" class="form-control" required />
      </div>
      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea v-model="editCat.description" class="form-control" rows="3" required></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Photo de la catégorie</label>
        <div v-if="editCat.image_url" style="margin-bottom:.5rem">
          <img :src="editCat.image_url" style="width:100%;height:120px;object-fit:cover;border-radius:var(--radius-sm)" />
        </div>
        <input
          type="file" accept="image/*" class="form-control"
          @change="editCat.imageFile = $event.target.files[0]"
          style="cursor:pointer"
        />
        <div v-if="editCat.imageFile" style="font-size:.8rem;color:var(--gray-500);margin-top:.3rem">
          🖼️ {{ editCat.imageFile.name }}
        </div>
      </div>
      <button type="submit" class="btn btn--primary btn--full mt-2">Enregistrer</button>
    </form>
  </AppModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppBadge from '@/components/ui/AppBadge.vue';
import AppModal from '@/components/ui/AppModal.vue';
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue';
import AppDashboardNavbar from '@/components/layout/AppDashboardNavbar.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { roomsAPI, reservationsAPI, authAPI, statsAPI } from '@/services/api';
import { formatDate, formatPrice } from '@/utils/formatters';

const router    = useRouter();
const authStore = useAuthStore();
const notif     = useNotificationStore();

const tabs = [
  { key: 'rooms',        icon: '&#127968;', label: 'Chambres' },
  { key: 'categories',   icon: '&#9783;',   label: 'Catégories' },
  { key: 'rates',        icon: 'FCFA',      label: 'Tarifs saisonniers' },
  { key: 'reservations', icon: '&#9776;',   label: 'Réservations' },
  { key: 'users',        icon: '&#9786;',   label: 'Utilisateurs' },
];
const activeTab = ref('rooms');

// Stats
const stats = ref({ totalRooms: '—', occupied: '—', totalReservations: '—', revenue: '—' });

// Données
const rooms           = ref([]);
const categories      = ref([]);
const rates           = ref([]);
const allReservations = ref([]);
const users           = ref([]);

// Loaders
const loadingRooms  = ref(false);
const loadingRates  = ref(false);
const loadingAllRes = ref(false);
const loadingCats   = ref(false);
const loadingUsers  = ref(false);

// Recherches
const roomSearch = ref('');
const resSearch  = ref('');
const userSearch = ref('');

// Computed — filtres de recherche
const filteredRooms = computed(() => {
  const q = roomSearch.value.toLowerCase().trim();
  if (!q) return rooms.value;
  return rooms.value.filter(r =>
    r.number?.toLowerCase().includes(q) ||
    String(r.floor).includes(q) ||
    r.category_detail?.name?.toLowerCase().includes(q) ||
    r.status?.toLowerCase().includes(q)
  );
});

const filteredReservations = computed(() => {
  const q = resSearch.value.toLowerCase().trim();
  if (!q) return allReservations.value;
  return allReservations.value.filter(r =>
    String(r.id).includes(q) ||
    r.client_detail?.full_name?.toLowerCase().includes(q) ||
    r.room_detail?.number?.toLowerCase().includes(q) ||
    r.status?.toLowerCase().includes(q)
  );
});

const filteredUsers = computed(() => {
  const q = userSearch.value.toLowerCase().trim();
  if (!q) return users.value;
  return users.value.filter(u =>
    u.full_name?.toLowerCase().includes(q) ||
    u.email?.toLowerCase().includes(q) ||
    u.role?.toLowerCase().includes(q) ||
    u.username?.toLowerCase().includes(q)
  );
});

// Formulaires ajout
const roomForm = ref({ number: '', floor: 0, category: '', imageFile: null });
const rateForm = ref({ category: '', name: '', start_date: '', end_date: '', price_per_night: '' });
const catForm  = ref({ name: '', base_price: '', max_occupancy: '', description: '', imageFile: null });

// Modals édition
const showRoomModal = ref(false);
const editRoom      = ref({});
const showCatModal  = ref(false);
const editCat       = ref({});

// Modal de confirmation générique
const confirmModal = ref({
  show: false, title: '', message: '', type: 'danger', confirmLabel: 'Confirmer', action: () => {},
});
function openConfirm({ title, message, type = 'danger', confirmLabel = 'Confirmer', action }) {
  confirmModal.value = { show: true, title, message, type, confirmLabel, action };
}

// ---- Stats (endpoint dédié) ----
async function loadStats() {
  try {
    const data = await statsAPI.getDashboard();
    stats.value = {
      totalRooms:        data.rooms?.total        ?? '—',
      occupied:          data.rooms?.occupied      ?? '—',
      totalReservations: data.reservations?.total  ?? '—',
      revenue:           formatPrice(parseFloat(data.revenue || 0)),
    };
  } catch (e) { console.warn('loadStats error:', e.message); }
}

// ---- Chambres ----
async function loadRooms() {
  loadingRooms.value = true;
  try { const d = await roomsAPI.getRooms(); rooms.value = d.results || d; }
  catch (e) { console.error(e); rooms.value = []; }
  finally { loadingRooms.value = false; }
}

async function addRoom() {
  try {
    const created = await roomsAPI.createRoom({ number: roomForm.value.number, floor: roomForm.value.floor, category: roomForm.value.category });
    if (roomForm.value.imageFile) {
      try { await roomsAPI.uploadRoomImage(created.id, roomForm.value.imageFile); }
      catch { notif.showToast('Chambre créée mais l\'image n\'a pas pu être uploadée.', 'warning'); }
    }
    notif.showToast('Chambre ajoutée !', 'success');
    roomForm.value = { number: '', floor: 0, category: '', imageFile: null };
    loadRooms(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function openEditRoom(room) {
  editRoom.value = { id: room.id, number: room.number, floor: room.floor, category: room.category_detail?.id, status: room.status, image_url: room.image_url, imageFile: null };
  showRoomModal.value = true;
}

async function updateRoom() {
  try {
    await roomsAPI.updateRoom(editRoom.value.id, { number: editRoom.value.number, floor: editRoom.value.floor, category: editRoom.value.category, status: editRoom.value.status });
    if (editRoom.value.imageFile) {
      try { await roomsAPI.uploadRoomImage(editRoom.value.id, editRoom.value.imageFile); }
      catch { notif.showToast('Données mises à jour mais l\'image n\'a pas pu être uploadée.', 'warning'); }
    }
    notif.showToast('Chambre mise à jour !', 'success');
    showRoomModal.value = false;
    loadRooms(); loadStats();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

async function uploadRoomPhoto(id, event) {
  const file = event.target.files[0];
  if (!file) return;
  try {
    await roomsAPI.uploadRoomImage(id, file);
    notif.showToast('Photo mise à jour !', 'success');
    loadRooms();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function askDeleteRoom(id) {
  openConfirm({
    title: 'Supprimer la chambre',
    message: 'Cette action est irréversible. Toutes les réservations associées seront supprimées.',
    confirmLabel: 'Supprimer',
    action: () => deleteRoom(id),
  });
}
async function deleteRoom(id) {
  try { await roomsAPI.deleteRoom(id); notif.showToast('Chambre supprimée.', 'success'); loadRooms(); loadStats(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Tarifs ----
async function loadRates() {
  loadingRates.value = true;
  try { const d = await roomsAPI.getRates(); rates.value = d.results || d; }
  catch (e) { console.error(e); rates.value = []; }
  finally { loadingRates.value = false; }
}

async function addRate() {
  try {
    await roomsAPI.createRate({ ...rateForm.value });
    notif.showToast('Tarif créé !', 'success');
    rateForm.value = { category: '', name: '', start_date: '', end_date: '', price_per_night: '' };
    loadRates();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function askDeleteRate(id) {
  openConfirm({
    title: 'Supprimer ce tarif',
    message: 'Les nouvelles réservations utiliseront le tarif de base de la catégorie.',
    confirmLabel: 'Supprimer',
    action: () => deleteRate(id),
  });
}
async function deleteRate(id) {
  try { await roomsAPI.deleteRate(id); notif.showToast('Tarif supprimé.', 'success'); loadRates(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Réservations ----
async function loadAllReservations() {
  loadingAllRes.value = true;
  try { const d = await reservationsAPI.getAll(); allReservations.value = d.results || d; }
  catch (e) { console.error(e); allReservations.value = []; }
  finally { loadingAllRes.value = false; }
}

async function confirmRes(id) {
  try { await reservationsAPI.confirm(id); notif.showToast('Réservation confirmée.', 'success'); loadAllReservations(); loadStats(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

function askCancelRes(id) {
  openConfirm({
    title: 'Annuler la réservation',
    message: 'Cette réservation sera annulée. Le client devra refaire une demande.',
    confirmLabel: 'Annuler la réservation',
    action: () => cancelRes(id),
  });
}
async function cancelRes(id) {
  try { await reservationsAPI.cancel(id); notif.showToast('Réservation annulée.', 'success'); loadAllReservations(); loadStats(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Catégories ----
async function loadCategories() {
  loadingCats.value = true;
  try { const d = await roomsAPI.getCategories(); categories.value = d.results || d; }
  catch (e) { console.error(e); categories.value = []; }
  finally { loadingCats.value = false; }
}

async function addCategory() {
  try {
    const created = await roomsAPI.createCategory({ name: catForm.value.name, base_price: catForm.value.base_price, max_occupancy: catForm.value.max_occupancy, description: catForm.value.description });
    if (catForm.value.imageFile) {
      try { await roomsAPI.uploadCategoryImage(created.id, catForm.value.imageFile); }
      catch { notif.showToast('Catégorie créée mais l\'image n\'a pas pu être uploadée.', 'warning'); }
    }
    notif.showToast('Catégorie ajoutée !', 'success');
    catForm.value = { name: '', base_price: '', max_occupancy: '', description: '', imageFile: null };
    loadCategories();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function openEditCategory(cat) {
  editCat.value = { ...cat, imageFile: null };
  showCatModal.value = true;
}

async function updateCategory() {
  try {
    await roomsAPI.updateCategory(editCat.value.id, { name: editCat.value.name, base_price: editCat.value.base_price, max_occupancy: editCat.value.max_occupancy, description: editCat.value.description });
    if (editCat.value.imageFile) {
      try { await roomsAPI.uploadCategoryImage(editCat.value.id, editCat.value.imageFile); }
      catch { notif.showToast('Données mises à jour mais l\'image n\'a pas pu être uploadée.', 'warning'); }
    }
    notif.showToast('Catégorie mise à jour !', 'success');
    showCatModal.value = false;
    loadCategories(); loadRooms();
  } catch (e) { notif.showToast(e.message, 'error'); }
}

function askDeleteCategory(id) {
  openConfirm({
    title: 'Supprimer la catégorie',
    message: 'Toutes les chambres associées à cette catégorie seront également supprimées.',
    confirmLabel: 'Supprimer',
    action: () => deleteCategory(id),
  });
}
async function deleteCategory(id) {
  try { await roomsAPI.deleteCategory(id); notif.showToast('Catégorie supprimée.', 'success'); loadCategories(); loadRooms(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Utilisateurs ----
async function loadUsers() {
  loadingUsers.value = true;
  try { const d = await authAPI.getUsers(); users.value = d.results || d; }
  catch (e) { console.error(e); users.value = []; }
  finally { loadingUsers.value = false; }
}

async function changeRole(id, role) {
  try { await authAPI.updateUser(id, { role }); notif.showToast('Rôle mis à jour.', 'success'); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

function askDeleteUser(id) {
  if (id === authStore.user?.id) {
    notif.showToast('Impossible de supprimer votre propre compte.', 'error');
    return;
  }
  openConfirm({
    title: 'Supprimer l\'utilisateur',
    message: 'Cet utilisateur et toutes ses réservations seront définitivement supprimés.',
    confirmLabel: 'Supprimer',
    action: () => deleteUser(id),
  });
}
async function deleteUser(id) {
  try { await authAPI.deleteUser(id); notif.showToast('Utilisateur supprimé.', 'success'); loadUsers(); }
  catch (e) { notif.showToast(e.message, 'error'); }
}

// ---- Tab watcher ----
watch(activeTab, (tab) => {
  if (tab === 'rooms')        loadRooms();
  if (tab === 'rates')        loadRates();
  if (tab === 'reservations') loadAllReservations();
  if (tab === 'categories')   loadCategories();
  if (tab === 'users')        loadUsers();
});

// ---- Init ----
onMounted(() => {
  loadStats();
  loadRooms();
  loadCategories();
});
</script>

<style scoped>
.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: .75rem; }
.text-gold { color: var(--gold-400); }
</style>
