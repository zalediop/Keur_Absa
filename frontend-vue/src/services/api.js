/**
 * HotelBookCI — API Service (Vue.js version)
 * Wrapper fetch avec gestion automatique du JWT
 */

const API_BASE = '/api';

// ============================================================
// TokenManager — gestion JWT dans localStorage
// ============================================================
export const TokenManager = {
  getAccess:   () => localStorage.getItem('access_token'),
  getRefresh:  () => localStorage.getItem('refresh_token'),
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  },
  isAuthenticated: () => !!localStorage.getItem('access_token'),
  setUser:  (user) => localStorage.setItem('user_data', JSON.stringify(user)),
  getUser() {
    const d = localStorage.getItem('user_data');
    return d ? JSON.parse(d) : null;
  },
};

// ============================================================
// Core apiCall
// ============================================================
let isRefreshing = false;

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };

  const token = TokenManager.getAccess();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config = { ...options, headers };
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  let response = await fetch(url, config);

  // Auto-refresh token sur 401
  if (response.status === 401 && !isRefreshing) {
    const refreshToken = TokenManager.getRefresh();
    if (refreshToken) {
      isRefreshing = true;
      try {
        const r = await fetch(`${API_BASE}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken }),
        });
        if (r.ok) {
          const { access } = await r.json();
          localStorage.setItem('access_token', access);
          headers['Authorization'] = `Bearer ${access}`;
          response = await fetch(url, { ...config, headers });
        } else {
          TokenManager.clearTokens();
          window.location.href = '/login?session=expired';
          return;
        }
      } catch {
        TokenManager.clearTokens();
        window.location.href = '/login';
        return;
      } finally {
        isRefreshing = false;
      }
    } else {
      TokenManager.clearTokens();
      window.location.href = '/login';
      return;
    }
  }

  const contentType = response.headers.get('content-type');
  const data = contentType?.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const err = new Error(extractErrorMessage(data) || `Erreur ${response.status}`);
    err.status = response.status;
    err.data = data;
    throw err;
  }

  return data;
}

// Upload multipart (pour les fichiers/images)
async function apiCallMultipart(endpoint, formData, method = 'PATCH') {
  const url = `${API_BASE}${endpoint}`;
  const headers = {};
  const token = TokenManager.getAccess();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  // Ne pas mettre Content-Type : le navigateur le fait automatiquement avec boundary
  const response = await fetch(url, { method, headers, body: formData });
  const contentType = response.headers.get('content-type');
  const data = contentType?.includes('application/json')
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    const err = new Error(extractErrorMessage(data) || `Erreur ${response.status}`);
    err.status = response.status;
    err.data = data;
    throw err;
  }
  return data;
}

function extractErrorMessage(data) {
  if (typeof data === 'string') return data;
  if (data?.detail) return data.detail;
  if (data?.error) return data.error;
  if (data?.non_field_errors) return data.non_field_errors[0];
  const fieldErrors = Object.entries(data || {})
    .filter(([, val]) => Array.isArray(val))
    .map(([key, val]) => `${key}: ${val[0]}`)
    .join(' | ');
  return fieldErrors || 'Une erreur est survenue.';
}

// ============================================================
// API modules
// ============================================================
export const authAPI = {
  register: (data)      => apiCall('/auth/register/', { method: 'POST', body: data }),
  login: (data)         => apiCall('/auth/login/', { method: 'POST', body: data }),
  logout: (refresh)     => apiCall('/auth/logout/', { method: 'POST', body: { refresh } }),
  getProfile: ()        => apiCall('/auth/profile/'),
  updateProfile: (data) => apiCall('/auth/profile/', { method: 'PATCH', body: data }),
  changePassword: (data)=> apiCall('/auth/change-password/', { method: 'POST', body: data }),
  getUsers: (params={}) => apiCall(`/auth/users/?${new URLSearchParams(params)}`),
  updateUser: (id, data)=> apiCall(`/auth/users/${id}/`, { method: 'PATCH', body: data }),
  deleteUser: (id)      => apiCall(`/auth/users/${id}/`, { method: 'DELETE' }),
};

export const roomsAPI = {
  getCategories:          ()         => apiCall('/rooms/categories/'),
  getCategory:            (id)       => apiCall(`/rooms/categories/${id}/`),
  createCategory:         (data)     => apiCall('/rooms/categories/', { method: 'POST', body: data }),
  updateCategory:         (id, data) => apiCall(`/rooms/categories/${id}/`, { method: 'PATCH', body: data }),
  deleteCategory:         (id)       => apiCall(`/rooms/categories/${id}/`, { method: 'DELETE' }),
  uploadCategoryImage:    (id, file) => {
    const fd = new FormData(); fd.append('image', file);
    return apiCallMultipart(`/rooms/categories/${id}/`, fd, 'PATCH');
  },
  getRooms:               (params={})=> apiCall(`/rooms/?${new URLSearchParams(params)}`),
  getRoom:                (id)       => apiCall(`/rooms/${id}/`),
  createRoom:             (data)     => apiCall('/rooms/', { method: 'POST', body: data }),
  updateRoom:             (id, data) => apiCall(`/rooms/${id}/`, { method: 'PATCH', body: data }),
  deleteRoom:             (id)       => apiCall(`/rooms/${id}/`, { method: 'DELETE' }),
  uploadRoomImage:        (id, file) => {
    const fd = new FormData(); fd.append('image', file);
    return apiCallMultipart(`/rooms/${id}/`, fd, 'PATCH');
  },
  getRates:               ()         => apiCall('/rooms/rates/'),
  createRate:             (data)     => apiCall('/rooms/rates/', { method: 'POST', body: data }),
  updateRate:             (id, data) => apiCall(`/rooms/rates/${id}/`, { method: 'PATCH', body: data }),
  deleteRate:             (id)       => apiCall(`/rooms/rates/${id}/`, { method: 'DELETE' }),
};

export const reservationsAPI = {
  create:   (data)         => apiCall('/reservations/', { method: 'POST', body: data }),
  getAll:   (params={})    => apiCall(`/reservations/?${new URLSearchParams(params)}`),
  getOne:   (id)           => apiCall(`/reservations/${id}/`),
  cancel:   (id)           => apiCall(`/reservations/${id}/cancel/`, { method: 'PATCH' }),
  confirm:  (id)           => apiCall(`/reservations/${id}/confirm/`, { method: 'PATCH' }),
  checkIn:  (id, notes='') => apiCall(`/reservations/${id}/checkin/`, { method: 'POST', body: { notes } }),
  checkOut: (id, notes='') => apiCall(`/reservations/${id}/checkout/`, { method: 'POST', body: { notes } }),
};

export const paymentsAPI = {
  create: (data) => apiCall('/payments/', { method: 'POST', body: data }),
  getAll: ()     => apiCall('/payments/'),
  getOne: (id)   => apiCall(`/payments/${id}/`),
};

export const statsAPI = {
  getDashboard: () => apiCall('/stats/'),
};
