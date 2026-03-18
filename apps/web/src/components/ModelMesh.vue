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
          <div class="provider-badges">
            <span v-if="provider.priority" class="capsule priority-pill">{{ provider.priority }}</span>
            <span class="capsule">{{ provider.deployment }}</span>
          </div>
        </div>
        <strong class="provider-fit">{{ provider.fit }}</strong>
        <div class="tag-row">
          <span v-for="strength in provider.strengths" :key="strength" class="chip">{{ strength }}</span>
        </div>
        <div class="augmentation-list">
          <span v-for="item in provider.augmentation" :key="item" class="augmentation-chip">{{ item }}</span>
        </div>
      </article>
    </div>

    <section class="enablement-panel">
      <div class="section-heading compact">
        <div>
          <p class="eyebrow">{{ t('modelMesh.enablementTitle') }}</p>
        </div>
      </div>

      <div class="enablement-grid">
        <article v-for="item in enablement" :key="item.id" class="enablement-card">
          <div class="enablement-top">
            <strong>{{ item.name }}</strong>
            <span class="capsule">{{ item.kind }}</span>
          </div>
          <p>{{ item.summary }}</p>
          <small>{{ t('modelMesh.enablementImpact') }}: {{ item.impact }}</small>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '../i18n';
import type { EnablementLayer, ModelProvider } from '../types';

defineProps<{
  strategy: string;
  providers: ModelProvider[];
  enablement: EnablementLayer[];
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

.section-heading.compact {
  margin-top: 28px;
}

.section-heading h2 {
  margin: 8px 0 0;
}

.strategy-copy {
  max-width: 76ch;
  color: var(--text-dim);
}

.provider-grid,
.enablement-grid {
  display: grid;
  gap: 16px;
}

.provider-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 24px;
}

.enablement-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.provider-card,
.enablement-card {
  padding: 18px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top right, rgba(255, 122, 26, 0.12), transparent 32%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.enablement-card {
  background:
    radial-gradient(circle at top right, rgba(0, 212, 170, 0.14), transparent 34%),
    rgba(255, 255, 255, 0.03);
}

.provider-top,
.enablement-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.provider-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.provider-top h3 {
  margin: 0;
}

.provider-top p,
.enablement-card p,
.enablement-card small {
  color: var(--text-dim);
}

.provider-fit {
  display: block;
  margin-top: 18px;
  color: var(--text-soft);
  line-height: 1.5;
}

.tag-row,
.augmentation-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.chip,
.augmentation-chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  color: var(--text-soft);
  font-size: 0.82rem;
}

.chip {
  background: rgba(0, 212, 170, 0.08);
  border: 1px solid rgba(0, 212, 170, 0.18);
}

.augmentation-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.priority-pill {
  background: rgba(255, 122, 26, 0.16);
  border-color: rgba(255, 122, 26, 0.2);
}

.enablement-panel {
  margin-top: 8px;
}

@media (max-width: 1100px) {
  .provider-grid,
  .enablement-grid {
    grid-template-columns: 1fr;
  }
}
</style>
