<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in notifStore.toasts"
          :key="toast.id"
          :class="['toast', `toast--${toast.type}`]"
        >
          <span class="toast__icon">{{ icons[toast.type] || 'ℹ️' }}</span>
          <span class="toast__message">{{ toast.message }}</span>
          <button class="toast__close" @click="notifStore.removeToast(toast.id)">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notification';
const notifStore = useNotificationStore();
const icons = { success: '✅', error: '❌', warning: '⚠️' };
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: .75rem;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .875rem 1.25rem;
  border-radius: 10px;
  font-size: .9rem;
  font-weight: 500;
  min-width: 280px;
  max-width: 400px;
  box-shadow: 0 8px 25px rgba(0,0,0,.25);
  pointer-events: auto;
  backdrop-filter: blur(10px);
}

.toast--success { background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.3); color: #6ee7b7; }
.toast--error   { background: rgba(239,68,68,.15);  border: 1px solid rgba(239,68,68,.3);  color: #fca5a5; }
.toast--warning { background: rgba(245,158,11,.15); border: 1px solid rgba(245,158,11,.3); color: #fcd34d; }

.toast__message { flex: 1; }
.toast__close {
  background: none; border: none; cursor: pointer;
  color: inherit; font-size: 1.1rem; opacity: .6; padding: 0;
}
.toast__close:hover { opacity: 1; }

/* Transitions */
.toast-enter-active, .toast-leave-active { transition: all .3s ease; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to   { opacity: 0; transform: translateX(100%); }
</style>
