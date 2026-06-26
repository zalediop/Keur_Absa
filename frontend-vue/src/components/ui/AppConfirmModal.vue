<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay active" @click.self="cancel">
        <div class="modal confirm-modal">
          <div class="confirm-modal__icon" :class="`confirm-modal__icon--${type}`">
            <svg v-if="type === 'danger'" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6M10 11v6M14 11v6M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
            </svg>
            <svg v-else-if="type === 'warning'" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="confirm-modal__content">
            <h3 class="confirm-modal__title">{{ title }}</h3>
            <p v-if="message" class="confirm-modal__message">{{ message }}</p>
          </div>
          <div class="confirm-modal__actions">
            <button class="btn btn--outline btn--sm" @click="cancel">{{ cancelLabel }}</button>
            <button
              :class="['btn', 'btn--sm', type === 'danger' ? 'btn--danger' : type === 'warning' ? 'btn--warning' : 'btn--primary']"
              @click="confirm"
            >{{ confirmLabel }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue:   { type: Boolean, default: false },
  title:        { type: String,  default: "Confirmer l'action" },
  message:      { type: String,  default: '' },
  confirmLabel: { type: String,  default: 'Confirmer' },
  cancelLabel:  { type: String,  default: 'Annuler' },
  type:         { type: String,  default: 'danger' },
});

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

function confirm() {
  emit('confirm');
  emit('update:modelValue', false);
}

function cancel() {
  emit('cancel');
  emit('update:modelValue', false);
}
</script>

<style scoped>
.confirm-modal {
  max-width: 420px;
  text-align: center;
  padding: 2rem;
}
.confirm-modal__icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  margin: 0 auto 1.25rem;
}
.confirm-modal__icon--danger  { background: rgba(220,38,38,.1);  color: var(--error,  #dc2626); }
.confirm-modal__icon--warning { background: rgba(245,127,23,.1); color: var(--warning,#f57f17); }
.confirm-modal__icon--info    { background: rgba(11,31,58,.08);  color: var(--navy,   #0b1f3a); }
.confirm-modal__title   { font-size:1.15rem; font-weight:700; color:var(--navy,#0b1f3a); margin-bottom:.5rem; }
.confirm-modal__message { color:var(--gray-500,#6b7280); font-size:.9rem; line-height:1.5; margin-bottom:1.5rem; }
.confirm-modal__actions { display:flex; gap:.75rem; justify-content:center; margin-top:1.5rem; }
.modal-enter-active, .modal-leave-active { transition: opacity .25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
