/**
 * dashboard.js — Logique des tableaux de bord par rôle
 */

document.addEventListener('DOMContentLoaded', () => {
  if (!requireAuth()) return;
  const path = window.location.pathname;

  if (path.includes('dashboard-client')) initClientDashboard();
  if (path.includes('dashboard-receptionniste')) initReceptionistDashboard();
  if (path.includes('dashboard-admin')) initAdminDashboard();

  // Afficher le nom dans la sidebar
  const user = TokenManager.getUser();
  if (user) {
    const nameEl = document.getElementById('sidebarUserName');
    const roleEl = document.getElementById('sidebarUserRole');
    if (nameEl) nameEl.textContent = user.first_name ? `${user.first_name} ${user.last_name}` : user.username;
    if (roleEl) {
      const roleLabels = { client: 'Client', receptionist: 'Réceptionniste', admin: 'Administrateur' };
      roleEl.textContent = roleLabels[user.role] || user.role;
    }
  }
});

// ============================================================
// DASHBOARD CLIENT
// ============================================================
async function initClientDashboard() {
  loadClientStats();
  loadClientReservations('all');

  document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadClientReservations(btn.dataset.filter);
    });
  });
}

async function loadClientStats() {
  try {
    const data = await API.reservations.getAll();
    const reservations = data.results || data;
    const confirmed = reservations.filter(r => ['confirmed', 'checked_in'].includes(r.status)).length;
    const pending = reservations.filter(r => r.status === 'pending').length;
    const completed = reservations.filter(r => r.status === 'checked_out').length;

    setStatValue('statTotal', reservations.length);
    setStatValue('statConfirmed', confirmed);
    setStatValue('statPending', pending);
    setStatValue('statCompleted', completed);
  } catch (e) { /* silencieux */ }
}

async function loadClientReservations(filter) {
  const container = document.getElementById('reservationsContainer');
  if (!container) return;
  container.innerHTML = '<div class="loading"><div class="spinner"></div>Chargement…</div>';

  try {
    const params = filter !== 'all' ? { status: filter } : {};
    const data = await API.reservations.getAll(params);
    const reservations = data.results || data;

    if (!reservations.length) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">📋</div>
          <div class="empty-state__title">Aucune réservation</div>
          <a href="/frontend/chambres.html" class="btn btn--primary mt-2">Réserver une chambre</a>
        </div>`;
      return;
    }

    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Chambre</th>
              <th>Arrivée</th>
              <th>Départ</th>
              <th>Nuits</th>
              <th>Montant</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${reservations.map(r => `
              <tr>
                <td><strong>#${r.id}</strong></td>
                <td>${r.room_detail?.number ? `Chambre ${r.room_detail.number}` : '—'}</td>
                <td>${formatDate(r.check_in_date)}</td>
                <td>${formatDate(r.check_out_date)}</td>
                <td>${r.nights}</td>
                <td>${formatPrice(r.total_price)}</td>
                <td>${getStatusBadge(r.status)}</td>
                <td>
                  ${r.is_cancellable
                    ? `<button onclick="cancelReservation(${r.id})" class="btn btn--danger btn--sm">Annuler</button>`
                    : ''}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">${err.message}</p>`;
  }
}

async function cancelReservation(id) {
  if (!confirm('Confirmer l\'annulation de cette réservation ?')) return;
  try {
    await API.reservations.cancel(id);
    showToast('Réservation annulée.', 'success');
    loadClientReservations('all');
    loadClientStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ============================================================
// DASHBOARD RÉCEPTIONNISTE
// ============================================================
async function initReceptionistDashboard() {
  if (!requireRole('receptionist', 'admin')) return;
  loadReceptionistStats();
  loadPendingReservations();
  loadTodayArrivals();
}

async function loadReceptionistStats() {
  try {
    const data = await API.reservations.getAll();
    const all = data.results || data;
    setStatValue('statPending', all.filter(r => r.status === 'pending').length);
    setStatValue('statConfirmed', all.filter(r => r.status === 'confirmed').length);
    setStatValue('statCheckedIn', all.filter(r => r.status === 'checked_in').length);
    setStatValue('statTotal', all.length);
  } catch (e) { /* silencieux */ }
}

async function loadPendingReservations() {
  const container = document.getElementById('pendingContainer');
  if (!container) return;
  container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  try {
    const data = await API.reservations.getAll({ status: 'pending' });
    const reservations = data.results || data;

    if (!reservations.length) {
      container.innerHTML = `<div class="empty-state"><div class="empty-state__icon">✅</div><p>Aucune réservation en attente.</p></div>`;
      return;
    }

    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Arrivée</th><th>Départ</th><th>Montant</th><th>Actions</th></tr></thead>
          <tbody>
            ${reservations.map(r => `
              <tr>
                <td><strong>#${r.id}</strong></td>
                <td>${r.client_detail?.full_name || '—'}</td>
                <td>${r.room_detail?.number ? `N° ${r.room_detail.number}` : '—'}</td>
                <td>${formatDate(r.check_in_date)}</td>
                <td>${formatDate(r.check_out_date)}</td>
                <td>${formatPrice(r.total_price)}</td>
                <td class="d-flex gap-1">
                  <button onclick="confirmReservation(${r.id})" class="btn btn--success btn--sm">Confirmer</button>
                  <button onclick="cancelReservationAdmin(${r.id})" class="btn btn--danger btn--sm">Annuler</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">${err.message}</p>`;
  }
}

async function loadTodayArrivals() {
  const container = document.getElementById('arrivalsContainer');
  if (!container) return;
  const today = new Date().toISOString().split('T')[0];
  container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  try {
    const data = await API.reservations.getAll({ status: 'confirmed', date_from: today, date_to: today });
    const reservations = data.results || data;

    if (!reservations.length) {
      container.innerHTML = `<div class="empty-state"><p>Aucune arrivée prévue aujourd'hui.</p></div>`;
      return;
    }

    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>#</th><th>Client</th><th>Chambre</th><th>Catégorie</th><th>Personnes</th><th>Actions</th></tr></thead>
          <tbody>
            ${reservations.map(r => `
              <tr>
                <td><strong>#${r.id}</strong></td>
                <td>${r.client_detail?.full_name || '—'}</td>
                <td>${r.room_detail?.number ? `N° ${r.room_detail.number}` : '—'}</td>
                <td>${r.room_detail?.category_detail?.name || '—'}</td>
                <td>${r.adults + r.children} pers.</td>
                <td>
                  <button onclick="performCheckIn(${r.id})" class="btn btn--primary btn--sm">Check-in ✓</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">${err.message}</p>`;
  }
}

async function confirmReservation(id) {
  try {
    await API.reservations.confirm(id);
    showToast('Réservation confirmée.', 'success');
    loadPendingReservations();
    loadReceptionistStats();
  } catch (err) { showToast(err.message, 'error'); }
}

async function cancelReservationAdmin(id) {
  if (!confirm('Annuler cette réservation ?')) return;
  try {
    await API.reservations.cancel(id);
    showToast('Réservation annulée.', 'success');
    loadPendingReservations();
    loadReceptionistStats();
  } catch (err) { showToast(err.message, 'error'); }
}

async function performCheckIn(id) {
  try {
    await API.reservations.checkIn(id);
    showToast('Check-in enregistré ! 🛎️', 'success');
    loadTodayArrivals();
    loadReceptionistStats();
  } catch (err) { showToast(err.message, 'error'); }
}

async function performCheckOut(id) {
  try {
    await API.reservations.checkOut(id);
    showToast('Check-out enregistré. Chambre en nettoyage.', 'success');
    loadReceptionistStats();
  } catch (err) { showToast(err.message, 'error'); }
}

// ============================================================
// DASHBOARD ADMIN
// ============================================================
async function initAdminDashboard() {
  if (!requireRole('admin')) return;
  loadAdminStats();
  loadAdminRooms();
  loadAdminUsers();
  loadAdminRates();
  initAdminForms();
}

async function loadAdminStats() {
  try {
    const [reservData, roomsData] = await Promise.all([
      API.reservations.getAll(),
      API.rooms.getRooms(),
    ]);
    const reservations = reservData.results || reservData;
    const rooms = roomsData.results || roomsData;

    setStatValue('statTotalRooms', rooms.length);
    setStatValue('statTotalReservations', reservations.length);
    setStatValue('statRevenue', formatPrice(
      reservations.filter(r => r.status !== 'cancelled')
        .reduce((sum, r) => sum + parseFloat(r.total_price || 0), 0)
    ));
    setStatValue('statOccupied', rooms.filter(r => r.status === 'occupied').length);
  } catch (e) { /* silencieux */ }
}

async function loadAdminRooms() {
  const container = document.getElementById('roomsContainer');
  if (!container) return;
  container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  try {
    const data = await API.rooms.getRooms();
    const rooms = data.results || data;

    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>N°</th><th>Étage</th><th>Catégorie</th><th>Statut</th><th>Actions</th></tr></thead>
          <tbody>
            ${rooms.map(r => `
              <tr>
                <td><strong>${r.number}</strong></td>
                <td>${r.floor}</td>
                <td>${r.category_detail?.name || '—'}</td>
                <td>
                  <span class="badge ${r.status === 'available' ? 'badge--green' : r.status === 'maintenance' ? 'badge--red' : 'badge--blue'}">
                    ${r.status}
                  </span>
                </td>
                <td>
                  <button onclick="deleteRoom(${r.id})" class="btn btn--danger btn--sm">Supprimer</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">${err.message}</p>`;
  }
}

async function loadAdminUsers() {
  const container = document.getElementById('usersContainer');
  if (!container) return;
  try {
    const data = await API.auth.getUsers();
    const users = data.results || data;
    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Nom</th><th>Email</th><th>Rôle</th><th>Réservations</th><th>Actions</th></tr></thead>
          <tbody>
            ${users.map(u => `
              <tr>
                <td>#${u.id}</td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td>
                  <select onchange="changeUserRole(${u.id}, this.value)" class="form-control" style="width:auto;padding:.3rem .6rem;font-size:.8rem">
                    <option value="client" ${u.role === 'client' ? 'selected' : ''}>Client</option>
                    <option value="receptionist" ${u.role === 'receptionist' ? 'selected' : ''}>Réceptionniste</option>
                    <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                  </select>
                </td>
                <td>${u.reservations_count}</td>
                <td>
                  <button onclick="deleteUser(${u.id})" class="btn btn--danger btn--sm">Supprimer</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<p class="text-muted">${err.message}</p>`;
  }
}

async function loadAdminRates() {
  const container = document.getElementById('ratesContainer');
  if (!container) return;
  try {
    const data = await API.rooms.getRates();
    const rates = data.results || data;
    if (!rates.length) {
      container.innerHTML = '<p class="text-muted">Aucun tarif saisonnier défini.</p>';
      return;
    }
    container.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>Saison</th><th>Catégorie</th><th>Du</th><th>Au</th><th>Prix/nuit</th><th>Actions</th></tr></thead>
          <tbody>
            ${rates.map(r => `
              <tr>
                <td><strong>${r.name}</strong></td>
                <td>${r.category_name}</td>
                <td>${formatDate(r.start_date)}</td>
                <td>${formatDate(r.end_date)}</td>
                <td class="text-gold">${formatPrice(r.price_per_night)}</td>
                <td><button onclick="deleteRate(${r.id})" class="btn btn--danger btn--sm">Supprimer</button></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) { /* silencieux */ }
}

function initAdminForms() {
  // Charger les catégories pour les formulaires
  loadCategoriesForForms();

  // Formulaire ajout chambre
  const roomForm = document.getElementById('addRoomForm');
  if (roomForm) {
    roomForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await API.rooms.createRoom({
          number: roomForm.number.value,
          floor: parseInt(roomForm.floor.value),
          category: parseInt(roomForm.category.value),
        });
        showToast('Chambre ajoutée !', 'success');
        roomForm.reset();
        loadAdminRooms();
        loadAdminStats();
      } catch (err) { showToast(err.message, 'error'); }
    });
  }

  // Formulaire tarif saisonnier
  const rateForm = document.getElementById('addRateForm');
  if (rateForm) {
    rateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await API.rooms.createRate({
          category: parseInt(rateForm.category.value),
          name: rateForm.name.value,
          start_date: rateForm.start_date.value,
          end_date: rateForm.end_date.value,
          price_per_night: parseFloat(rateForm.price_per_night.value),
        });
        showToast('Tarif saisonnier créé !', 'success');
        rateForm.reset();
        loadAdminRates();
      } catch (err) { showToast(err.message, 'error'); }
    });
  }
}

async function loadCategoriesForForms() {
  const selects = document.querySelectorAll('.category-select');
  try {
    const data = await API.rooms.getCategories();
    const cats = data.results || data;
    selects.forEach(select => {
      select.innerHTML = '<option value="">Sélectionner…</option>' +
        cats.map(c => `<option value="${c.id}">${c.name} (${formatPrice(c.base_price)}/nuit)</option>`).join('');
    });
  } catch (e) { /* silencieux */ }
}

async function changeUserRole(userId, newRole) {
  try {
    await API.auth.updateUser(userId, { role: newRole });
    showToast('Rôle mis à jour.', 'success');
  } catch (err) { showToast(err.message, 'error'); }
}

async function deleteRoom(id) {
  if (!confirm('Supprimer cette chambre ?')) return;
  try {
    await API.rooms.deleteRoom(id);
    showToast('Chambre supprimée.', 'success');
    loadAdminRooms();
  } catch (err) { showToast(err.message, 'error'); }
}

async function deleteUser(id) {
  if (!confirm('Supprimer cet utilisateur ?')) return;
  try {
    await API.auth.deleteUser(id);
    showToast('Utilisateur supprimé.', 'success');
    loadAdminUsers();
  } catch (err) { showToast(err.message, 'error'); }
}

async function deleteRate(id) {
  if (!confirm('Supprimer ce tarif ?')) return;
  try {
    await API.rooms.deleteRate(id);
    showToast('Tarif supprimé.', 'success');
    loadAdminRates();
  } catch (err) { showToast(err.message, 'error'); }
}

// ---- Utilitaires ----
function setStatValue(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

window.cancelReservation = cancelReservation;
window.confirmReservation = confirmReservation;
window.cancelReservationAdmin = cancelReservationAdmin;
window.performCheckIn = performCheckIn;
window.performCheckOut = performCheckOut;
window.changeUserRole = changeUserRole;
window.deleteRoom = deleteRoom;
window.deleteUser = deleteUser;
window.deleteRate = deleteRate;
