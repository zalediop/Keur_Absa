import { defineStore } from 'pinia';
import { ref } from 'vue';

let toastId = 0;

export const useNotificationStore = defineStore('notification', () => {
  const toasts = ref([]);

  function showToast(message, type = 'success', duration = 4000) {
    const id = ++toastId;
    toasts.value.push({ id, message, type });
    setTimeout(() => removeToast(id), duration);
  }

  function removeToast(id) {
    const idx = toasts.value.findIndex(t => t.id === id);
    if (idx !== -1) toasts.value.splice(idx, 1);
  }

  return { toasts, showToast, removeToast };
});
