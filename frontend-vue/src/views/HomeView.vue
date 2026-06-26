<template>
  <AppNavbar />

  <!-- ===== HERO ===== -->
  <section class="hero">
    <div class="container">
      <div class="hero__content">
        <div class="hero__eyebrow">Réservation en ligne · Saly, Sénégal</div>
        <h1 class="hero__title">
          Vivez une expérience
          <em>hôtelière inoubliable</em>
        </h1>
        <p class="hero__subtitle">
          Consultez nos chambres disponibles, réservez en quelques clics et payez en toute sécurité. Disponible 24h/24.
        </p>
        <div class="hero__cta">
          <router-link to="/chambres" class="btn btn--primary btn--lg">Voir les chambres →</router-link>
          <router-link to="/register" class="btn btn--outline btn--lg">Créer un compte</router-link>
        </div>
        <div class="hero__stats">
          <div>
            <div class="hero__stat-value">9+</div>
            <div class="hero__stat-label">Chambres</div>
          </div>
          <div>
            <div class="hero__stat-value">3</div>
            <div class="hero__stat-label">Catégories</div>
          </div>
          <div>
            <div class="hero__stat-value">24/7</div>
            <div class="hero__stat-label">Service</div>
          </div>
        </div>
      </div>
    </div>
    <div class="hero__decoration" aria-hidden="true">
      <svg viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%">
        <circle cx="250" cy="250" r="200" stroke="rgba(212,160,23,0.15)" stroke-width="1"/>
        <circle cx="250" cy="250" r="150" stroke="rgba(212,160,23,0.10)" stroke-width="1"/>
        <circle cx="250" cy="250" r="100" stroke="rgba(212,160,23,0.08)" stroke-width="1"/>
        <circle cx="250" cy="250" r="50"  fill="rgba(212,160,23,0.05)"/>
      </svg>
    </div>
  </section>

  <!-- ===== SEARCH BAR ===== -->
  <section style="padding:0 0 4rem;background:var(--gray-50)">
    <div class="container">
      <div class="search-bar">
        <h3 style="margin-bottom:1rem;font-size:1.1rem;">Rechercher une chambre disponible</h3>
        <div class="search-bar__grid">
          <div class="form-group" style="margin:0">
            <label class="form-label">Arrivée</label>
            <input type="date" v-model="search.checkIn" :min="today" class="form-control" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Départ</label>
            <input type="date" v-model="search.checkOut" :min="minCheckOut" class="form-control" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Personnes</label>
            <select v-model="search.capacity" class="form-control">
              <option value="1">1 personne</option>
              <option value="2">2 personnes</option>
              <option value="3">3 personnes</option>
              <option value="4">4+ personnes</option>
            </select>
          </div>
          <button class="btn btn--primary btn--lg" @click="goToChambres">Rechercher</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== CATEGORIES ===== -->
  <section class="section section--dark">
    <div class="container">
      <div class="section__header">
        <p class="section__eyebrow">Nos hébergements</p>
        <h2 class="section__title">Choisissez votre catégorie</h2>
        <p class="section__subtitle">Du confort Standard au luxe de la Suite Présidentielle</p>
      </div>
      <div class="grid-3">
        <template v-if="loadingCats">
          <div class="loading"><div class="spinner"></div>Chargement…</div>
        </template>
        <template v-else-if="categories.length === 0">
          <p class="text-muted">Impossible de charger les catégories.</p>
        </template>
        <div v-for="cat in categories" :key="cat.id" class="card fade-in-up">
          <div class="card__image" style="padding:0;overflow:hidden;height:200px">
            <img
              :src="cat.image_url || categoryImages[cat.name] || fallbackImg"
              :alt="cat.name"
              style="width:100%;height:100%;object-fit:cover"
            />
          </div>
          <div class="card__body">
            <h3 class="card__title">{{ cat.name }}</h3>
            <div class="card__price">{{ formatPrice(cat.base_price) }} <span>/ nuit</span></div>
            <div class="card__meta">
              <span class="card__meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
                {{ cat.max_occupancy }} pers. max
              </span>
              <span class="card__meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M3 7v14M21 7v14M16 3H8v4H3"/></svg>
                {{ cat.rooms_count }} chambre(s)
              </span>
            </div>
            <div class="amenities">
              <span v-for="a in (cat.amenities || []).slice(0,3)" :key="a" class="amenity">{{ a }}</span>
            </div>
            <router-link :to="`/chambres?category=${cat.id}`" class="btn btn--outline btn--full mt-2">
              Voir les chambres
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== WHY US ===== -->
  <section class="section">
    <div class="container">
      <div class="section__header">
        <p class="section__eyebrow">Pourquoi nous choisir</p>
        <h2 class="section__title">Une expérience premium</h2>
      </div>
      <div class="grid-3">
        <div class="card fade-in-up fade-in-up--delay-1" style="padding:0">
          <div class="card__body" style="padding:2rem;text-align:center">
            <div style="width:56px;height:56px;background:rgba(11,31,58,.06);border-radius:50%;display:grid;place-items:center;margin:0 auto 1rem">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--navy)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </div>
            <h3 class="card__title">Paiement sécurisé</h3>
            <p>Vos transactions sont protégées. Paiement par carte, virement ou mobile money.</p>
          </div>
        </div>
        <div class="card fade-in-up fade-in-up--delay-2" style="padding:0">
          <div class="card__body" style="padding:2rem;text-align:center">
            <div style="width:56px;height:56px;background:rgba(212,160,23,.10);border-radius:50%;display:grid;place-items:center;margin:0 auto 1rem">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--gold-dark)" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14M22 4L12 14.01l-3-3"/></svg>
            </div>
            <h3 class="card__title">Confirmation instantanée</h3>
            <p>Votre réservation est confirmée immédiatement. Zéro attente.</p>
          </div>
        </div>
        <div class="card fade-in-up fade-in-up--delay-3" style="padding:0">
          <div class="card__body" style="padding:2rem;text-align:center">
            <div style="width:56px;height:56px;background:rgba(11,31,58,.06);border-radius:50%;display:grid;place-items:center;margin:0 auto 1rem">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--navy)" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
            </div>
            <h3 class="card__title">Meilleur prix garanti</h3>
            <p>Tarifs saisonniers transparents. Voyagez en haute ou basse saison au meilleur prix.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== CTA ===== -->
  <section class="section section--dark" style="text-align:center">
    <div class="container">
      <h2 style="margin-bottom:1rem;color:#fff">Prêt à réserver votre séjour ?</h2>
      <p class="section__subtitle mb-4" style="color:rgba(255,255,255,.7)">Créez votre compte gratuitement et réservez en moins de 2 minutes.</p>
      <div class="hero__cta" style="justify-content:center">
        <router-link to="/register" class="btn btn--primary btn--lg">Créer un compte gratuit</router-link>
        <router-link to="/chambres" class="btn btn--outline-white btn--lg">Voir les chambres</router-link>
      </div>
    </div>
  </section>

  <AppFooter />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import { roomsAPI } from '@/services/api';
import { formatPrice } from '@/utils/formatters';

const router = useRouter();

// Dates
const today = new Date().toISOString().split('T')[0];
const tomorrowDate = new Date(Date.now() + 86400000).toISOString().split('T')[0];

const search = ref({ checkIn: tomorrowDate, checkOut: '', capacity: '2' });

const minCheckOut = computed(() => {
  if (!search.value.checkIn) return today;
  const d = new Date(search.value.checkIn);
  d.setDate(d.getDate() + 1);
  return d.toISOString().split('T')[0];
});

watch(() => search.value.checkIn, (val) => {
  const d = new Date(val);
  d.setDate(d.getDate() + 1);
  search.value.checkOut = d.toISOString().split('T')[0];
});

function goToChambres() {
  const q = {};
  if (search.value.checkIn)  q.check_in  = search.value.checkIn;
  if (search.value.checkOut) q.check_out = search.value.checkOut;
  if (search.value.capacity) q.capacity  = search.value.capacity;
  router.push({ path: '/chambres', query: q });
}

// Catégories
const categories  = ref([]);
const loadingCats = ref(true);

const fallbackImg = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80';
const categoryImages = {
  'Chambre Double Standard':    'https://images.unsplash.com/photo-1611891487122-2075b962442f?auto=format&fit=crop&w=600&q=80',
  'Double Standard Vue Mer':    'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80',
  'Chambre Familiale Baobab':   'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80',
  'Suite Swim-Up Vue Mer':      'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=600&q=80',
};

onMounted(async () => {
  try {
    const data = await roomsAPI.getCategories();
    categories.value = data.results || data;
  } catch { /* silencieux */ } finally {
    loadingCats.value = false;
  }
});
</script>

<style scoped>
.mt-2 { margin-top: .75rem; }
.mb-4 { margin-bottom: 1.5rem; }
</style>
