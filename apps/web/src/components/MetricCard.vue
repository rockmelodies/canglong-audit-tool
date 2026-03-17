<template>
  <article class="metric-card panel" :class="item.tone">
    <p class="eyebrow">{{ item.label }}</p>
    <div class="metric-value">{{ item.value }}</div>
    <p class="metric-delta">{{ item.delta }}</p>
  </article>
</template>

<script setup lang="ts">
import type { MetricCardItem } from '../types';

defineProps<{
  item: MetricCardItem;
}>();
</script>

<style scoped>
.metric-card {
  min-height: 152px;
}

.metric-value {
  margin-top: 22px;
  font-size: clamp(1.8rem, 3vw, 2.8rem);
  font-weight: 800;
}

.metric-delta {
  margin-top: 12px;
  color: var(--text-dim);
}

.accent {
  background:
    radial-gradient(circle at top right, rgba(0, 212, 170, 0.22), transparent 38%),
    rgba(14, 20, 25, 0.82);
}

.warning {
  background:
    radial-gradient(circle at top right, rgba(255, 122, 26, 0.24), transparent 38%),
    rgba(14, 20, 25, 0.82);
}
</style>

