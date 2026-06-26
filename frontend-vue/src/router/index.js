import { createRouter, createWebHistory } from 'vue-router';
import { TokenManager } from '@/services/api';

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/chambres', name: 'chambres', component: () => import('@/views/ChambresView.vue') },
  { path: '/reservation/:id', name: 'reservation', component: () => import('@/views/ReservationView.vue'), meta: { requiresAuth: true } },
  {
    path: '/login', name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register', name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/dashboard/client', name: 'dashboard-client',
    component: () => import('@/views/dashboard/ClientView.vue'),
    meta: { requiresAuth: true, role: 'client' },
  },
  {
    path: '/dashboard/reception', name: 'dashboard-reception',
    component: () => import('@/views/dashboard/ReceptionView.vue'),
    meta: { requiresAuth: true, roles: ['receptionist', 'admin'] },
  },
  {
    path: '/dashboard/admin', name: 'dashboard-admin',
    component: () => import('@/views/dashboard/AdminView.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  // Catch-all
  { path: '/:pathMatch(.*)*', redirect: '/' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

// Navigation Guards
router.beforeEach((to) => {
  const isAuth = TokenManager.isAuthenticated();
  const user   = TokenManager.getUser();

  // Pages réservées aux non-connectés (login/register)
  if (to.meta.guestOnly && isAuth) {
    const role = user?.role;
    if (role === 'admin') return { name: 'dashboard-admin' };
    if (role === 'receptionist') return { name: 'dashboard-reception' };
    return { name: 'dashboard-client' };
  }

  // Pages nécessitant une connexion
  if (to.meta.requiresAuth && !isAuth) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }

  // Vérification du rôle unique
  if (to.meta.role && user && user.role !== to.meta.role && user.role !== 'admin') {
    return { name: 'home' };
  }

  // Vérification de plusieurs rôles
  if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
    return { name: 'home' };
  }
});

export default router;
