<template>
  <AppNavbar />
  <main style="padding-top:80px;min-height:100vh">
    <div class="container" style="padding-top:2rem;padding-bottom:4rem">
      <div class="section__header" style="text-align:left;margin-bottom:2rem">
        <p class="section__eyebrow">Nos hébergements</p>
        <h1 class="section__title">Nos chambres disponibles</h1>
      </div>

      <!-- Filtres -->
      <div class="search-bar mb-4">
        <div class="search-bar__grid">
          <div class="form-group" style="margin:0">
            <label class="form-label">Arrivée</label>
            <input type="date" v-model="filters.check_in" :min="today" class="form-control" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Départ</label>
            <input type="date" v-model="filters.check_out" :min="minCheckOut" class="form-control" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Catégorie</label>
            <select v-model="filters.category" class="form-control">
              <option value="">Toutes</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <button class="btn btn--primary" @click="loadRooms">Filtrer</button>
        </div>
      </div>

      <!-- Grille chambres -->
      <div v-if="loading" class="loading"><div class="spinner"></div>Chargement…</div>
      <div v-else-if="rooms.length === 0" class="empty-state">
        <div class="empty-state__icon">🏨</div>
        <div class="empty-state__title">Aucune chambre disponible</div>
        <p class="text-muted">Essayez d'autres dates ou catégories.</p>
      </div>
      <div v-else class="grid-3">
        <div v-for="room in rooms" :key="room.id" class="card fade-in-up">
          <div class="card__image" style="padding:0;overflow:hidden;height:200px">
            <img
              :src="getRoomImage(room)"
              :alt="room.category_detail?.name"
              style="width:100%;height:100%;object-fit:cover"
            />
          </div>
          <div class="card__body">
            <div class="d-flex" style="justify-content:space-between;align-items:center;margin-bottom:.5rem">
              <h3 class="card__title" style="margin:0">Chambre {{ room.number }}</h3>
              <span :class="['badge', room.status === 'available' ? 'badge--green' : 'badge--red']">
                {{ room.status === 'available' ? 'Disponible' : room.status }}
              </span>
            </div>
            <p style="font-size:.85rem;color:var(--navy-400);margin-bottom:.75rem">
              {{ room.category_detail?.name }} · Étage {{ room.floor }}
            </p>
            <div class="card__price">{{ formatPrice(room.category_detail?.base_price) }} <span>/ nuit</span></div>
            <div class="card__meta">
              <span class="card__meta-item">👥 {{ room.category_detail?.max_occupancy }} pers. max</span>
            </div>
            <div class="amenities">
              <span v-for="a in (room.category_detail?.amenities || []).slice(0,3)" :key="a" class="amenity">✓ {{ a }}</span>
            </div>
            <router-link
              v-if="room.status === 'available'"
              :to="`/reservation/${room.id}`"
              class="btn btn--primary btn--full mt-2"
            >
              Réserver cette chambre
            </router-link>
            <button v-else class="btn btn--full mt-2" disabled>Non disponible</button>
          </div>
        </div>
      </div>
    </div>
  </main>
  <AppFooter />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import { roomsAPI } from '@/services/api';
import { formatPrice } from '@/utils/formatters';

const route = useRoute();

const today = new Date().toISOString().split('T')[0];

const filters = ref({
  check_in:  route.query.check_in  || '',
  check_out: route.query.check_out || '',
  category:  route.query.category  || '',
});

const minCheckOut = computed(() => {
  if (!filters.value.check_in) return today;
  const d = new Date(filters.value.check_in);
  d.setDate(d.getDate() + 1);
  return d.toISOString().split('T')[0];
});

watch(() => filters.value.check_in, (val) => {
  const d = new Date(val);
  d.setDate(d.getDate() + 1);
  filters.value.check_out = d.toISOString().split('T')[0];
});

const rooms      = ref([]);
const categories = ref([]);
const loading    = ref(true);

const fallbackImg = '/placeholder-room.jpg';
function getRoomImage(room) {
  if (room.image_url) return room.image_url;
  if (room.category_detail?.image_url) return room.category_detail.image_url;
  return fallbackImg;
}

async function loadRooms() {
  loading.value = true;
  try {
    const params = {};
    if (filters.value.check_in)  params.check_in  = filters.value.check_in;
    if (filters.value.check_out) params.check_out = filters.value.check_out;
    if (filters.value.category)  params.category  = filters.value.category;
    const data = await roomsAPI.getRooms(params);
    rooms.value = data.results || data;
  } catch { rooms.value = []; }
  finally { loading.value = false; }
}

onMounted(async () => {
  const [catsData] = await Promise.all([roomsAPI.getCategories(), loadRooms()]);
  categories.value = (catsData.results || catsData);
});
</script>

<style scoped>
.mt-2  { margin-top: .75rem; }
.mb-4  { margin-bottom: 1.5rem; }
.d-flex { display: flex; }
</style>
