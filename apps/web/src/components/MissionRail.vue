<template>
  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('missionRail.eyebrow') }}</p>
        <h2>{{ title }}</h2>
      </div>
      <span class="capsule">{{ t('missionRail.activeCount', { count: items.length }) }}</span>
    </div>

    <div class="mission-list">
      <article v-for="mission in items" :key="mission.id" class="mission-card">
        <div class="mission-top">
          <div>
            <h3>{{ mission.name }}</h3>
            <p>{{ mission.target }}</p>
          </div>
          <span class="capsule">{{ mission.stage }}</span>
        </div>
        <div class="mission-meta">
          <span>{{ mission.mode }}</span>
          <span>{{ t('missionRail.confidence', { value: mission.confidence }) }}</span>
          <span>{{ t('missionRail.findings', { count: mission.findings }) }}</span>
        </div>
        <p class="mission-action">{{ mission.nextAction }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '../i18n';
import type { Mission } from '../types';

defineProps<{
  title: string;
  items: Mission[];
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

.mission-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.mission-card {
  padding: 18px;
  border-radius: 18px;
  background:
    radial-gradient(circle at top right, rgba(0, 212, 170, 0.14), transparent 35%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.mission-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.mission-top h3 {
  margin: 0;
}

.mission-top p {
  margin: 6px 0 0;
  color: var(--text-dim);
}

.mission-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
  color: var(--text-soft);
}

.mission-action {
  margin: 18px 0 0;
  color: var(--text-main);
}
</style>
