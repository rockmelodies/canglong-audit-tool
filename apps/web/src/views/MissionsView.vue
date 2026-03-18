<template>
  <div class="page">
    <section class="hero panel missions-hero">
      <div>
        <p class="eyebrow">{{ t('missions.heroEyebrow') }}</p>
        <h1>{{ t('missions.title') }}</h1>
        <p>{{ t('missions.description') }}</p>
      </div>
      <div class="hero-tags">
        <span class="capsule">{{ t('missions.tagDocker') }}</span>
        <span class="capsule">{{ t('missions.tagDecompiler') }}</span>
        <span class="capsule">{{ t('missions.tagRuntime') }}</span>
      </div>
    </section>

    <MissionRail :title="t('missions.priorityTitle')" :items="missions" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import MissionRail from '../components/MissionRail.vue';
import { useI18n } from '../i18n';
import type { Locale } from '../i18n/messages';
import { fetchMissions } from '../services/api';
import type { Mission } from '../types';

const missions = ref<Mission[]>([]);
const { locale, t } = useI18n();

async function loadMissions(selectedLocale: Locale) {
  missions.value = await fetchMissions(selectedLocale);
}

watch(
  locale,
  (selectedLocale) => {
    void loadMissions(selectedLocale);
  },
  { immediate: true },
);
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.missions-hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  min-height: 220px;
}

.missions-hero h1 {
  margin: 10px 0 12px;
  font-size: clamp(2rem, 5vw, 3.8rem);
  line-height: 1;
}

.missions-hero p:last-child {
  max-width: 56ch;
  color: var(--text-dim);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

@media (max-width: 760px) {
  .missions-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-tags {
    justify-content: flex-start;
  }
}
</style>
