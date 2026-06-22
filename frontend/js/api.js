/**
 * HotelBookCI — API Wrapper avec gestion JWT
 *
 * Ce module centralise toutes les communications avec le backend Django.
 * Il injecte automatiquement le token Bearer dans chaque requête.
 * En cas de 401, il tente de rafraîchir le token avant de réessayer.
 */

const API_BASE = 'http://127.0.0.1:8000/api';

// ============================================================
// Gestion du stockage des tokens JWT
// ============================================================

const TokenManager = {
  /** Récupère le token access depuis localStorage */
  getAccess() {
    return localStorage.getItem('access_token');
  },

  /** Récupère le token refresh depuis localStorage */
  getRefresh() {
    return localStorage.getItem('refresh_token');
  },

  /** Stocke les deux tokens après login/inscription */
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },

  /** Supprime tous les tokens (logout) */
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  },

  /** Vérifie si l'utilisateur est connecté */
  isAuthenticated() {
    return !!this.getAccess();
  },

  /** Stocke les données utilisateur */
  setUser(user) {
    localStorage.setItem('user_data', JSON.stringify(user));
  },

  /** Récupère les données utilisateur */
  getUser() {
    const data = localStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
  },
};

// ============================================================
// Wrapper fetch avec injection du token JWT
// ============================================================

let isRefreshing = false; // Évite les appels refresh simultanés

/**
 * Effectue un appel API avec gestion automatique du token JWT.
 * Si le serveur retourne 401, tente de rafraîchir le token et réessaie.
 *
 * @param {string} endpoint - URL relative ex: '/auth/login/'
 * @param {object} options  - Options fetch (method, body, etc.)
 * @returns {Promise<any>}  - La réponse JSON parsée
 */
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  // Construction des headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Injection du token Bearer si disponible
  const token = TokenManager.getAccess();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  // Si body est un objet, le sérialiser en JSON
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  let response = await fetch(url, config);

  // ---- Gestion du 401 : token expiré ----
  if (response.status === 401 && !isRefreshing) {
    const refreshToken = TokenManager.getRefresh();

    if (refreshToken) {
      isRefreshing = true;
      try {
        const refreshResponse = await fetch(`${API_BASE}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken }),
        });

        if (refreshResponse.ok) {
          const { access } = await refreshResponse.json();
          // Stocker le nouveau token
          localStorage.setItem('access_token', access);
          // Réessayer la requête originale avec le nouveau token
          headers['Authorization'] = `Bearer ${access}`;
          response = await fetch(url, { ...config, headers });
        } else {
          // Refresh token aussi expiré → déconnecter
          TokenManager.clearTokens();
          window.location.href = '/frontend/login.html?session=expired';
          return;
        }
      } catch (err) {
        TokenManager.clearTokens();
        window.location.href = '/frontend/login.html?session=expired';
        return;
      } finally {
        isRefreshing = false;
      }
    } else {
      // Pas de refresh token → redirect login
      window.location.href = '/frontend/login.html';
      return;
    }
  }

  // ---- Parse la réponse ----
  const contentType = response.headers.get('content-type');
  let data;

  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    // Construire un message d'erreur lisible
    const error = new Error(extractErrorMessage(data) || `Erreur ${response.status}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

/**
 * Extrait le message d'erreur lisible depuis la réponse DRF.
 * DRF peut retourner: string, { detail: ... }, { field: [errors] }
 */
function extractErrorMessage(data) {
  if (typeof data === 'string') return data;
  if (data?.detail) return data.detail;
  if (data?.error) return data.error;
  if (data?.non_field_errors) return data.non_field_errors[0];

  // Erreurs de champs
  const fieldErrors = Object.entries(data || {})
    .filter(([, val]) => Array.isArray(val))
    .map(([key, val]) => `${key}: ${val[0]}`)
    .join(' | ');

  return fieldErrors || 'Une erreur est survenue.';
}

// ============================================================
// API Auth
// ============================================================
const authAPI = {
  register: (data) => apiCall('/auth/register/', { method: 'POST', body: data }),
  login: (data) => apiCall('/auth/login/', { method: 'POST', body: data }),
  logout: (refresh) => apiCall('/auth/logout/', { method: 'POST', body: { refresh } }),
  getProfile: () => apiCall('/auth/profile/'),
  updateProfile: (data) => apiCall('/auth/profile/', { method: 'PATCH', body: data }),
  changePassword: (data) => apiCall('/auth/change-password/', { method: 'POST', body: data }),
  refreshToken: (refresh) => apiCall('/auth/token/refresh/', { method: 'POST', body: { refresh } }),

  // Admin
  getUsers: (params = {}) => apiCall(`/auth/users/?${new URLSearchParams(params)}`),
  updateUser: (id, data) => apiCall(`/auth/users/${id}/`, { method: 'PATCH', body: data }),
  deleteUser: (id) => apiCall(`/auth/users/${id}/`, { method: 'DELETE' }),
};

// ============================================================
// API Chambres
// ============================================================
const roomsAPI = {
  getCategories: () => apiCall('/rooms/categories/'),
  getCategory: (id) => apiCall(`/rooms/categories/${id}/`),
  createCategory: (data) => apiCall('/rooms/categories/', { method: 'POST', body: data }),
  updateCategory: (id, data) => apiCall(`/rooms/categories/${id}/`, { method: 'PATCH', body: data }),

  getRooms: (params = {}) => apiCall(`/rooms/?${new URLSearchParams(params)}`),
  getRoom: (id) => apiCall(`/rooms/${id}/`),
  createRoom: (data) => apiCall('/rooms/', { method: 'POST', body: data }),
  updateRoom: (id, data) => apiCall(`/rooms/${id}/`, { method: 'PATCH', body: data }),
  deleteRoom: (id) => apiCall(`/rooms/${id}/`, { method: 'DELETE' }),

  getRates: () => apiCall('/rooms/rates/'),
  createRate: (data) => apiCall('/rooms/rates/', { method: 'POST', body: data }),
  updateRate: (id, data) => apiCall(`/rooms/rates/${id}/`, { method: 'PATCH', body: data }),
  deleteRate: (id) => apiCall(`/rooms/rates/${id}/`, { method: 'DELETE' }),
};

// ============================================================
// API Réservations
// ============================================================
const reservationsAPI = {
  create: (data) => apiCall('/reservations/', { method: 'POST', body: data }),
  getAll: (params = {}) => apiCall(`/reservations/?${new URLSearchParams(params)}`),
  getOne: (id) => apiCall(`/reservations/${id}/`),
  cancel: (id) => apiCall(`/reservations/${id}/cancel/`, { method: 'PATCH' }),
  confirm: (id) => apiCall(`/reservations/${id}/confirm/`, { method: 'PATCH' }),
  checkIn: (id, notes = '') => apiCall(`/reservations/${id}/checkin/`, { method: 'POST', body: { notes } }),
  checkOut: (id, notes = '') => apiCall(`/reservations/${id}/checkout/`, { method: 'POST', body: { notes } }),
};

// ============================================================
// API Paiements
// ============================================================
const paymentsAPI = {
  create: (data) => apiCall('/payments/', { method: 'POST', body: data }),
  getAll: () => apiCall('/payments/'),
  getOne: (id) => apiCall(`/payments/${id}/`),
};

// ============================================================
// Utilitaires UI
// ============================================================

/** Affiche une notification toast */
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span class="toast__icon">${icons[type] || 'ℹ️'}</span>
    <span class="toast__message">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut .3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/** Formate une date YYYY-MM-DD en français */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

/** Formate un montant en FCFA */
function formatPrice(amount) {
  return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
}

/** Retourne le badge HTML pour un statut de réservation */
function getStatusBadge(status) {
  const badges = {
    pending:     '<span class="badge badge--gold">En attente</span>',
    confirmed:   '<span class="badge badge--green">Confirmée</span>',
    checked_in:  '<span class="badge badge--blue">Arrivé</span>',
    checked_out: '<span class="badge badge--gray">Parti</span>',
    cancelled:   '<span class="badge badge--red">Annulée</span>',
  };
  return badges[status] || `<span class="badge">${status}</span>`;
}

/** Redirige vers login si non authentifié */
function requireAuth() {
  if (!TokenManager.isAuthenticated()) {
    window.location.href = '/frontend/login.html';
    return false;
  }
  return true;
}

/** Redirige si le rôle n'est pas autorisé */
function requireRole(...allowedRoles) {
  const user = TokenManager.getUser();
  if (!user || !allowedRoles.includes(user.role)) {
    showToast("Accès non autorisé.", 'error');
    setTimeout(() => window.location.href = '/frontend/index.html', 1500);
    return false;
  }
  return true;
}

// Export global
window.API = { auth: authAPI, rooms: roomsAPI, reservations: reservationsAPI, payments: paymentsAPI };
window.TokenManager = TokenManager;
window.showToast = showToast;
window.formatDate = formatDate;
window.formatPrice = formatPrice;
window.getStatusBadge = getStatusBadge;
window.requireAuth = requireAuth;
window.requireRole = requireRole;
