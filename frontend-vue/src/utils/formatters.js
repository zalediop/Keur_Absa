/** Formate une date YYYY-MM-DD en français */
export function formatDate(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

/** Formate un montant en FCFA */
export function formatPrice(amount) {
  if (amount === null || amount === undefined) return '—';
  return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
}

/** Retourne le statut badge selon le status de réservation */
export function getStatusInfo(status) {
  const map = {
    pending:     { label: 'En attente',  css: 'badge--gold'  },
    confirmed:   { label: 'Confirmée',   css: 'badge--green' },
    checked_in:  { label: 'Arrivé',      css: 'badge--blue'  },
    checked_out: { label: 'Parti',       css: 'badge--gray'  },
    cancelled:   { label: 'Annulée',     css: 'badge--red'   },
  };
  return map[status] || { label: status, css: '' };
}

/** URL du dashboard selon le rôle */
export function getDashboardRoute(role) {
  const routes = {
    client:       '/dashboard/client',
    receptionist: '/dashboard/reception',
    admin:        '/dashboard/admin',
  };
  return routes[role] || '/';
}
