/**
 * rooms.js — Affichage et filtrage des chambres disponibles
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  const path = window.location.pathname;
  if (path.includes('chambres')) loadRoomsPage();
  if (path.includes('reservation')) loadReservationPage();
});

// ============================================================
// Page Chambres — Browse & Filtres
// ============================================================
async function loadRoomsPage() {
  const grid = document.getElementById('roomsGrid');
  const filterForm = document.getElementById('filterForm');
  if (!grid) return;

  // Charger les catégories pour le filtre
  loadCategoryOptions();

  // Charger les chambres au démarrage
  await fetchAndDisplayRooms({});

  // Filtrage
  if (filterForm) {
    filterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const params = {};
      const checkIn = filterForm.check_in?.value;
      const checkOut = filterForm.check_out?.value;
      const category = filterForm.category?.value;
      const capacity = filterForm.capacity?.value;

      if (checkIn) params.check_in = checkIn;
      if (checkOut) params.check_out = checkOut;
      if (category) params.category = category;
      if (capacity) params.capacity = capacity;

      await fetchAndDisplayRooms(params);
    });
  }
}

async function loadCategoryOptions() {
  const select = document.getElementById('categoryFilter');
  if (!select) return;
  try {
    const data = await API.rooms.getCategories();
    const categories = data.results || data;
    categories.forEach(cat => {
      const opt = document.createElement('option');
      opt.value = cat.id;
      opt.textContent = cat.name;
      select.appendChild(opt);
    });
  } catch (e) { /* silencieux */ }
}

async function fetchAndDisplayRooms(params) {
  const grid = document.getElementById('roomsGrid');
  grid.innerHTML = '<div class="loading"><div class="spinner"></div>Chargement des chambres…</div>';

  try {
    const data = await API.rooms.getRooms(params);
    const rooms = data.results || data;

    if (!rooms.length) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1">
          <div class="empty-state__icon">🏨</div>
          <div class="empty-state__title">Aucune chambre disponible</div>
          <p class="text-muted">Essayez d'autres dates ou critères.</p>
        </div>`;
      return;
    }

    grid.innerHTML = rooms.map(room => renderRoomCard(room, params)).join('');
  } catch (err) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><p class="text-muted">${err.message}</p></div>`;
  }
}

function renderRoomCard(room, params = {}) {
  const cat = room.category_detail || {};
  const amenities = (cat.amenities || []).slice(0, 3).map(a =>
    `<span class="amenity">✓ ${a}</span>`
  ).join('');

  const price = room.price_for_period
    ? `${formatPrice(room.price_for_period)} <span>/ séjour (${room.nights} nuits)</span>`
    : `${formatPrice(room.current_price || cat.base_price || 0)} <span>/ nuit</span>`;

  const reserveParams = new URLSearchParams({
    room_id: room.id,
    room_name: `Chambre ${room.number} — ${cat.name || ''}`,
    ...(params.check_in ? { check_in: params.check_in } : {}),
    ...(params.check_out ? { check_out: params.check_out } : {}),
  }).toString();

  return `
    <div class="card fade-in-up">
      <div class="card__image" style="background: linear-gradient(135deg, #1e293b, #334155); display:flex; align-items:center; justify-content:center; font-size:3rem;">
        🛏️
      </div>
      <div class="card__body">
        <div class="d-flex justify-between align-center mb-1">
          <span class="badge badge--gold">${cat.name || 'Standard'}</span>
          <span class="badge badge--gray">Étage ${room.floor}</span>
        </div>
        <h3 class="card__title">Chambre ${room.number}</h3>
        <div class="card__price">${price}</div>
        <div class="card__meta">
          <span class="card__meta-item">👥 ${cat.max_occupancy || 2} pers. max</span>
          <span class="card__meta-item">🏨 N° ${room.number}</span>
        </div>
        <div class="amenities">${amenities}</div>
        <a href="/frontend/reservation.html?${reserveParams}" class="btn btn--primary btn--full mt-2">
          Réserver cette chambre →
        </a>
      </div>
    </div>`;
}

// ============================================================
// Page Réservation
// ============================================================
async function loadReservationPage() {
  if (!requireAuth()) return;

  const params = new URLSearchParams(window.location.search);
  const roomId = params.get('room_id');
  const roomName = params.get('room_name');
  const checkIn = params.get('check_in');
  const checkOut = params.get('check_out');

  // Pré-remplir les champs
  if (document.getElementById('roomName')) document.getElementById('roomName').textContent = roomName || 'Chambre sélectionnée';
  if (document.getElementById('roomId')) document.getElementById('roomId').value = roomId;
  if (document.getElementById('checkIn')) document.getElementById('checkIn').value = checkIn || '';
  if (document.getElementById('checkOut')) document.getElementById('checkOut').value = checkOut || '';

  // Calculer le prix à la volée
  const checkInInput = document.getElementById('checkIn');
  const checkOutInput = document.getElementById('checkOut');
  if (checkInInput && checkOutInput) {
    [checkInInput, checkOutInput].forEach(input => {
      input.addEventListener('change', updatePriceEstimate);
    });
    if (checkIn && checkOut) updatePriceEstimate();
  }

  // Soumettre la réservation
  const form = document.getElementById('reservationForm');
  if (form) {
    form.addEventListener('submit', submitReservation);
  }
}

async function updatePriceEstimate() {
  const roomId = document.getElementById('roomId')?.value;
  const checkIn = document.getElementById('checkIn')?.value;
  const checkOut = document.getElementById('checkOut')?.value;
  const priceEl = document.getElementById('priceEstimate');
  if (!roomId || !checkIn || !checkOut || !priceEl) return;

  try {
    const data = await API.rooms.getRooms({ check_in: checkIn, check_out: checkOut });
    const rooms = data.results || data;
    const room = rooms.find(r => r.id == roomId);
    if (room && room.price_for_period) {
      priceEl.textContent = formatPrice(room.price_for_period);
      priceEl.dataset.price = room.price_for_period;
    }
  } catch (e) { /* silencieux */ }
}

async function submitReservation(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('[type="submit"]');

  try {
    btn.disabled = true;
    btn.textContent = 'Réservation en cours…';

    const payload = {
      room: parseInt(form.room_id?.value || document.getElementById('roomId').value),
      check_in_date: document.getElementById('checkIn').value,
      check_out_date: document.getElementById('checkOut').value,
      adults: parseInt(form.adults?.value || 1),
      children: parseInt(form.children?.value || 0),
      special_requests: form.special_requests?.value || '',
    };

    const reservation = await API.reservations.create(payload);

    // Paiement immédiat
    const method = form.payment_method?.value || 'card';
    await API.payments.create({
      reservation: reservation.id,
      amount: reservation.total_price,
      method,
    });

    showToast('Réservation et paiement confirmés ! 🎉', 'success');
    setTimeout(() => window.location.href = '/frontend/dashboard-client.html', 1500);

  } catch (err) {
    showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Confirmer et payer';
  }
}

window.loadRoomsPage = loadRoomsPage;
