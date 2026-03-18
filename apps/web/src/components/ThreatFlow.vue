<template>
  <section class="panel flow-card">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('threatFlow.eyebrow') }}</p>
        <h2>{{ t('threatFlow.title') }}</h2>
      </div>
      <span class="capsule">{{ t('threatFlow.tag') }}</span>
    </div>

    <div class="flow-grid">
      <article v-for="stage in stages" :key="stage.name" class="flow-stage">
        <p>{{ stage.name }}</p>
        <strong>{{ stage.count }}</strong>
        <span>{{ stage.emphasis }}</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '../i18n';
import type { FlowStage } from '../types';

defineProps<{
  stages: FlowStage[];
}>();

const { t } = useI18n();
</script>

<style scoped>
.flow-card {
  overflow: hidden;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-heading h2 {
  margin: 8px 0 0;
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.flow-stage {
  position: relative;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.flow-stage strong {
  display: block;
  margin: 18px 0 10px;
  font-size: 1.9rem;
}

.flow-stage span {
  color: var(--text-dim);
}

@media (max-width: 900px) {
  .flow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .flow-grid {
    grid-template-columns: 1fr;
  }
}
</style>
