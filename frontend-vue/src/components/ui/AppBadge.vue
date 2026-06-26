<template>
  <span :class="['badge', cssClass]">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue';
import { getStatusInfo } from '@/utils/formatters';

const props = defineProps({ status: { type: String, required: true } });

const info     = computed(() => getStatusInfo(props.status));
const label    = computed(() => info.value.label);
const cssClass = computed(() => info.value.css);
</script>
