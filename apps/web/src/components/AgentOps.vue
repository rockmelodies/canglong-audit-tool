<template>
  <section class="agent-grid">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('agentOps.blueprintsEyebrow') }}</p>
          <h2>{{ t('agentOps.blueprintsTitle') }}</h2>
        </div>
        <span class="capsule">{{ t('agentOps.blueprintCount', { count: blueprints.length }) }}</span>
      </div>

      <div class="blueprint-list">
        <article v-for="blueprint in blueprints" :key="blueprint.name" class="blueprint-card">
          <div class="blueprint-top">
            <h3>{{ blueprint.name }}</h3>
            <span class="capsule">{{ blueprint.status }}</span>
          </div>
          <p>{{ blueprint.purpose }}</p>
          <strong>{{ blueprint.modelStrategy }}</strong>
          <div class="meta-line">
            <span>{{ t('agentOps.defaultModel') }}: {{ blueprint.defaultModel ?? '-' }}</span>
          </div>
          <div class="tag-row">
            <span v-for="output in blueprint.outputs" :key="output" class="chip">{{ output }}</span>
          </div>
          <div class="enablement-row">
            <span class="label">{{ t('agentOps.enablement') }}</span>
            <div class="tag-row compact">
              <span v-for="item in blueprint.enablement" :key="item" class="stack-chip">{{ item }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('agentOps.runsEyebrow') }}</p>
          <h2>{{ t('agentOps.runsTitle') }}</h2>
        </div>
        <span class="capsule">{{ t('agentOps.activeCount', { count: runs.length }) }}</span>
      </div>

      <div class="run-list">
        <article v-for="run in runs" :key="run.id" class="run-card">
          <div class="run-top">
            <div>
              <h3>{{ run.agent }}</h3>
              <p>{{ run.objective }}</p>
            </div>
            <span class="capsule">{{ run.state }}</span>
          </div>
          <div class="run-meta">
            <span>{{ run.provider }}</span>
            <span>{{ run.id }}</span>
          </div>
          <p class="run-result">{{ run.result }}</p>
          <div v-if="run.stack" class="stack-box">
            <span class="label">{{ t('agentOps.stack') }}</span>
            <strong>{{ run.stack }}</strong>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '../i18n';
import type { AgentBlueprint, AgentRun } from '../types';

defineProps<{
  blueprints: AgentBlueprint[];
  runs: AgentRun[];
}>();

const { t } = useI18n();
</script>

<style scoped>
.agent-grid {
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
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

.blueprint-list,
.run-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.blueprint-card,
.run-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.blueprint-top,
.run-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.blueprint-top h3,
.run-top h3 {
  margin: 0;
}

.blueprint-card p,
.run-top p,
.run-result,
.meta-line,
.label {
  color: var(--text-dim);
}

.blueprint-card strong,
.stack-box strong {
  display: block;
  margin-top: 14px;
  color: var(--text-soft);
  line-height: 1.5;
}

.meta-line {
  margin-top: 14px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.tag-row.compact {
  margin-top: 10px;
}

.chip,
.stack-chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  color: var(--text-soft);
  font-size: 0.82rem;
}

.chip {
  background: rgba(255, 122, 26, 0.08);
  border: 1px solid rgba(255, 122, 26, 0.18);
}

.stack-chip {
  background: rgba(0, 212, 170, 0.08);
  border: 1px solid rgba(0, 212, 170, 0.18);
}

.enablement-row,
.stack-box {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.run-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
  color: var(--text-soft);
}

.run-result {
  margin-bottom: 0;
}

@media (max-width: 1100px) {
  .agent-grid {
    grid-template-columns: 1fr;
  }
}
</style>
