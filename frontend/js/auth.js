/**
 * auth.js — Gestion de l'authentification JWT côté frontend
 *
 * Ce fichier gère:
 * 1. La connexion (login) → récupération et stockage des tokens
 * 2. L'inscription (register)
 * 3. La déconnexion (logout) → suppression des tokens
 * 4. La mise à jour de la navbar selon l'état d'auth
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initLoginForm();
  initRegisterForm();
});

// ============================================================
// Navbar dynamique selon l'état de connexion
// ============================================================
function initNavbar() {
  const user = TokenManager.getUser();
  const navActions = document.getElementById('navActions');
  if (!navActions) return;

  if (user) {
    const dashboardUrl = getDashboardUrl(user.role);
    navActions.innerHTML = `
      <span class="text-muted text-sm">Bonjour, <strong style="color:#fff">${user.first_name || user.username}</strong></span>
      <a href="${dashboardUrl}" class="btn btn--outline btn--sm">Mon espace</a>
      <button onclick="logout()" class="btn btn--primary btn--sm">Déconnexion</button>
    `;
  } else {
    navActions.innerHTML = `
      <a href="/frontend/login.html" class="btn btn--outline btn--sm">Connexion</a>
      <a href="/frontend/register.html" class="btn btn--primary btn--sm">S'inscrire</a>
    `;
  }
}

function getDashboardUrl(role) {
  const urls = {
    client: '/frontend/dashboard-client.html',
    receptionist: '/frontend/dashboard-receptionniste.html',
    admin: '/frontend/dashboard-admin.html',
  };
  return urls[role] || '/frontend/index.html';
}

// ============================================================
// Formulaire de connexion
// ============================================================
function initLoginForm() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  // Vérifier si session expirée
  const params = new URLSearchParams(window.location.search);
  if (params.get('session') === 'expired') {
    showToast('Votre session a expiré. Reconnectez-vous.', 'warning');
  }

  // Si déjà connecté, rediriger
  if (TokenManager.isAuthenticated()) {
    const user = TokenManager.getUser();
    if (user) window.location.href = getDashboardUrl(user.role);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    const originalText = btn.textContent;

    try {
      btn.disabled = true;
      btn.textContent = 'Connexion…';

      const data = {
        username: form.username.value.trim(),
        password: form.password.value,
      };

      /**
       * ---- FLUX JWT ----
       * 1. POST /api/auth/login/ avec username + password
       * 2. La réponse contient { tokens: { access, refresh }, user: {...} }
       * 3. On stocke les deux tokens dans localStorage
       * 4. On stocke les infos user pour affichage
       * 5. On redirige vers le dashboard selon le rôle
       */
      const response = await API.auth.login(data);

      // Stockage des tokens JWT
      TokenManager.setTokens(response.tokens.access, response.tokens.refresh);
      TokenManager.setUser(response.user);

      showToast(response.message, 'success');

      // Redirection selon le rôle
      setTimeout(() => {
        window.location.href = getDashboardUrl(response.user.role);
      }, 800);

    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });
}

// ============================================================
// Formulaire d'inscription
// ============================================================
function initRegisterForm() {
  const form = document.getElementById('registerForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    const originalText = btn.textContent;

    try {
      btn.disabled = true;
      btn.textContent = 'Inscription…';

      const data = {
        username: form.username.value.trim(),
        email: form.email.value.trim(),
        first_name: form.first_name.value.trim(),
        last_name: form.last_name.value.trim(),
        phone: form.phone?.value?.trim() || '',
        password: form.password.value,
        password_confirm: form.password_confirm.value,
      };

      const response = await API.auth.register(data);

      // Connexion automatique après inscription
      TokenManager.setTokens(response.tokens.access, response.tokens.refresh);
      TokenManager.setUser(response.user);

      showToast('Compte créé ! Bienvenue sur HotelBookCI 🏨', 'success');
      setTimeout(() => {
        window.location.href = getDashboardUrl(response.user.role);
      }, 1000);

    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });
}

// ============================================================
// Déconnexion
// ============================================================
async function logout() {
  try {
    const refresh = TokenManager.getRefresh();
    if (refresh) {
      await API.auth.logout(refresh);
    }
  } catch (e) {
    // Même si l'API échoue, on déconnecte localement
  } finally {
    /**
     * Suppression des tokens JWT du localStorage
     * → L'utilisateur ne peut plus effectuer de requêtes authentifiées
     */
    TokenManager.clearTokens();
    showToast('Déconnexion réussie.', 'success');
    setTimeout(() => window.location.href = '/frontend/index.html', 600);
  }
}

window.logout = logout;
window.getDashboardUrl = getDashboardUrl;
