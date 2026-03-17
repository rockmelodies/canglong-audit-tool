<template>
  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Capability Matrix</p>
        <h2>Audit stack lanes</h2>
      </div>
      <span class="capsule">Extensible adapters</span>
    </div>

    <div class="capability-grid">
      <article v-for="item in items" :key="item.name" class="capability-card">
        <div class="capability-top">
          <h3>{{ item.name }}</h3>
          <span class="capsule">{{ item.status }}</span>
        </div>
        <p>{{ item.summary }}</p>
        <small>{{ item.depth }}</small>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { CapabilityItem } from '../types';

defineProps<{
  items: CapabilityItem[];
}>();
</script>

<style scoped>
.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-heading h2 {
  margin: 8px 0 0;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.capability-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.capability-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.capability-card h3 {
  margin: 0;
}

.capability-card p {
  color: var(--text-dim);
  line-height: 1.6;
}

.capability-card small {
  color: var(--text-soft);
}

@media (max-width: 720px) {
  .capability-grid {
    grid-template-columns: 1fr;
  }
}
</style>

