<template>
  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('modelMesh.eyebrow') }}</p>
        <h2>{{ t('modelMesh.title') }}</h2>
      </div>
      <span class="capsule">{{ t('modelMesh.tag') }}</span>
    </div>

    <p class="strategy-copy">{{ strategy }}</p>

    <div class="provider-grid">
      <article v-for="provider in providers" :key="provider.id" class="provider-card">
        <div class="provider-top">
          <div>
            <h3>{{ provider.name }}</h3>
            <p>{{ provider.category }}</p>
          </div>
          <span class="capsule">{{ provider.deployment }}</span>
        </div>
        <strong class="provider-fit">{{ provider.fit }}</strong>
        <div class="tag-row">
          <span v-for="strength in provider.strengths" :key="strength" class="chip">{{ strength }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '../i18n';
import type { ModelProvider } from '../types';

defineProps<{
  strategy: string;
  providers: ModelProvider[];
}>();

const { t } = useI18n();
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

.strategy-copy {
  max-width: 72ch;
  color: var(--text-dim);
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.provider-card {
  padding: 18px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, rgba(255, 122, 26, 0.12), transparent 32%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.provider-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.provider-top h3 {
  margin: 0;
}

.provider-top p {
  margin: 6px 0 0;
  color: var(--text-dim);
}

.provider-fit {
  display: block;
  margin-top: 18px;
  color: var(--text-soft);
  line-height: 1.5;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(0, 212, 170, 0.08);
  border: 1px solid rgba(0, 212, 170, 0.18);
  color: var(--text-soft);
  font-size: 0.82rem;
}

@media (max-width: 900px) {
  .provider-grid {
    grid-template-columns: 1fr;
  }
}
</style>
