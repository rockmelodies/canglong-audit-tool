<template>
  <div class="page">
    <section class="hero panel missions-hero">
      <div>
        <p class="eyebrow">Mission Orchestration</p>
        <h1>Queue, prove, replay</h1>
        <p>
          Missions combine semantic review, dockerized verification, reverse-engineering handoff, and guided
          breakpoints into one execution model.
        </p>
      </div>
      <div class="hero-tags">
        <span class="capsule">Docker profiles</span>
        <span class="capsule">Decompiler lanes</span>
        <span class="capsule">Runtime recipes</span>
      </div>
    </section>

    <MissionRail title="Priority Missions" :items="missions" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import MissionRail from '../components/MissionRail.vue';
import { fetchMissions } from '../services/api';
import type { Mission } from '../types';

const missions = ref<Mission[]>([]);

onMounted(async () => {
  missions.value = await fetchMissions();
});
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

