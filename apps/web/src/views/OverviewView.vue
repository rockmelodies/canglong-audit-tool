<template>
  <div class="page">
    <section class="hero panel">
      <div>
        <p class="eyebrow">Adaptive Audit Core</p>
        <h1>{{ dashboard.codename }} / {{ dashboard.repository }}</h1>
        <p class="hero-copy">
          Focus: {{ dashboard.focus }}
        </p>
      </div>
      <div class="hero-rail">
        <div class="hero-stat">
          <span>Confidence</span>
          <strong>{{ dashboard.confidence }}</strong>
        </div>
        <div class="hero-stat">
          <span>Mode</span>
          <strong>Audit + Hunt + Replay</strong>
        </div>
      </div>
    </section>

    <section class="metric-grid">
      <MetricCard v-for="metric in dashboard.metrics" :key="metric.id" :item="metric" />
    </section>

    <ThreatFlow :stages="dashboard.flow" />

    <section class="two-column">
      <CapabilityGrid :items="dashboard.capabilities" />
      <section class="panel hot-paths">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Hot Paths</p>
            <h2>Files demanding proof</h2>
          </div>
          <span class="capsule">Evidence-ranked</span>
        </div>

        <div class="path-list">
          <article v-for="path in dashboard.hotPaths" :key="path.path" class="path-item">
            <div class="path-top">
              <strong>{{ path.path }}</strong>
              <span class="capsule">{{ path.risk }}</span>
            </div>
            <p>{{ path.evidence }}</p>
          </article>
        </div>
      </section>
    </section>

    <ModelMesh :strategy="llmStack.strategy" :providers="llmStack.providers" />

    <AgentOps :blueprints="llmStack.blueprints" :runs="llmStack.runs" />

    <ActivityFeed :items="dashboard.feed" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import ActivityFeed from '../components/ActivityFeed.vue';
import AgentOps from '../components/AgentOps.vue';
import CapabilityGrid from '../components/CapabilityGrid.vue';
import MetricCard from '../components/MetricCard.vue';
import ModelMesh from '../components/ModelMesh.vue';
import ThreatFlow from '../components/ThreatFlow.vue';
import { fetchDashboard, fetchLlmStack } from '../services/api';
import type { DashboardData, LlmStackData } from '../types';

const dashboard = ref<DashboardData>({
  repository: '',
  codename: 'Canglong',
  confidence: '',
  focus: '',
  metrics: [],
  flow: [],
  capabilities: [],
  feed: [],
  hotPaths: [],
});

const llmStack = ref<LlmStackData>({
  strategy: '',
  providers: [],
  blueprints: [],
  runs: [],
});

onMounted(async () => {
  const [dashboardData, llmStackData] = await Promise.all([fetchDashboard(), fetchLlmStack()]);
  dashboard.value = dashboardData;
  llmStack.value = llmStackData;
});
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  min-height: 240px;
  background:
    radial-gradient(circle at top left, rgba(255, 122, 26, 0.22), transparent 34%),
    radial-gradient(circle at right, rgba(0, 212, 170, 0.18), transparent 38%),
    linear-gradient(135deg, rgba(13, 18, 25, 0.96), rgba(7, 12, 17, 0.88));
}

.hero h1 {
  max-width: 12ch;
  margin: 10px 0 0;
  font-size: clamp(2.2rem, 6vw, 4.5rem);
  line-height: 0.94;
}

.hero-copy {
  max-width: 56ch;
  margin: 20px 0 0;
  color: var(--text-dim);
  font-size: 1.05rem;
}

.hero-rail {
  display: grid;
  gap: 14px;
  min-width: 240px;
}

.hero-stat {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-stat span {
  display: block;
  color: var(--text-dim);
}

.hero-stat strong {
  display: block;
  margin-top: 6px;
  font-size: 1.5rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.two-column {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
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

.path-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.path-item {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.path-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.path-item p {
  margin-bottom: 0;
  color: var(--text-dim);
}

@media (max-width: 1100px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .two-column {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-rail {
    width: 100%;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
