<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay active" @click.self="$emit('update:modelValue', false)">
        <div class="modal">
          <div class="modal__header">
            <h2>{{ title }}</h2>
            <button class="modal__close" @click="$emit('update:modelValue', false)">×</button>
          </div>
          <div class="modal__body">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({ modelValue: Boolean, title: String });
defineEmits(['update:modelValue']);
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal__body { padding: 1.5rem; }
</style>
