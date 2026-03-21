<template>
  <div class="page">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('report.summaryEyebrow') }}</p>
          <h1>{{ t('report.summaryTitle') }} / {{ report?.repoName ?? job?.repoName ?? jobId }}</h1>
        </div>

        <button type="button" class="ghost-button" :disabled="loading" @click="loadReport()">
          {{ t('report.refresh') }}
        </button>
      </div>

      <p v-if="loading" class="notice">{{ t('report.loading') }}</p>
      <p v-else-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <div v-else-if="report" class="summary-meta">
        <span>{{ t('report.generatedAt') }}: {{ formatDate(report.generatedAt) }}</span>
      </div>
      <p v-else-if="notReady" class="notice">{{ t('report.notReady') }}</p>

      <div v-if="report" class="stats-grid">
        <article class="stat-card">
          <span>{{ t('report.statsFiles') }}</span>
          <strong>{{ report.summary.filesScanned }}</strong>
        </article>
        <article class="stat-card">
          <span>{{ t('report.statsEndpoints') }}</span>
          <strong>{{ report.summary.endpointsDiscovered }}</strong>
        </article>
        <article class="stat-card">
          <span>{{ t('report.statsFlows') }}</span>
          <strong>{{ report.summary.businessFlowsMapped }}</strong>
        </article>
        <article class="stat-card">
          <span>{{ t('report.statsFindings') }}</span>
          <strong>{{ report.summary.findingsTotal }}</strong>
        </article>
        <article class="stat-card warning">
          <span>{{ t('report.statsCritical') }}</span>
          <strong>{{ report.summary.criticalFindings }}</strong>
        </article>
        <article class="stat-card warning">
          <span>{{ t('report.statsHigh') }}</span>
          <strong>{{ report.summary.highFindings }}</strong>
        </article>
      </div>
    </section>

    <section v-if="notReady && job" class="panel">
      <p class="eyebrow">{{ t('report.jobEyebrow') }}</p>
      <div class="job-top">
        <div>
          <h2>{{ job.repoName }}</h2>
          <p>{{ job.currentStep }}</p>
        </div>
        <span class="capsule">{{ formatStatus(job.status) }}</span>
      </div>

      <div class="summary-meta">
        <span>{{ t('report.jobStatus') }}: {{ formatStatus(job.status) }}</span>
        <span>{{ t('report.jobUpdatedAt') }}: {{ formatDate(job.updatedAt) }}</span>
      </div>

      <div class="progress-row">
        <span>{{ t('report.jobProgress') }}</span>
        <strong>{{ job.progress }}%</strong>
      </div>
      <div class="progress-bar">
        <span :style="{ width: `${job.progress}%` }"></span>
      </div>

      <div class="stack-list">
        <article v-for="stage in job.stages" :key="stage.name" class="row-card">
          <strong>{{ stage.name }}</strong>
          <span>{{ formatStatus(stage.status) }}</span>
          <p>{{ stage.detail }}</p>
        </article>
      </div>
    </section>

    <section v-if="report" class="focus-grid">
      <article class="panel focus-card">
        <p class="eyebrow">{{ t('report.focusTitle') }}</p>
        <strong>{{ featuredChain?.name ?? t('report.noExploitChains') }}</strong>
        <p>{{ featuredChain?.rationale ?? t('report.noExploitChains') }}</p>
        <div v-if="featuredChain" class="chip-row">
          <span class="capsule emphasis">{{ featuredChain.confidence }}</span>
          <span class="capsule">{{ featuredChain.category }}</span>
          <span
            v-for="dependency in featuredChain.matchedDependencies.slice(0, 3)"
            :key="dependency"
            class="capsule"
          >
            {{ dependency }}
          </span>
        </div>
      </article>

      <article class="panel focus-card">
        <p class="eyebrow">{{ t('report.focusJava') }}</p>
        <strong>{{ javaChains.length }}</strong>
        <p>
          {{
            javaChains.length
              ? javaChains.map((item) => item.name).slice(0, 2).join(' / ')
              : t('report.noExploitChains')
          }}
        </p>
        <div class="chip-row">
          <span v-for="framework in report.environment.frameworks.slice(0, 4)" :key="framework" class="capsule">
            {{ framework }}
          </span>
        </div>
      </article>

      <article class="panel focus-card">
        <p class="eyebrow">{{ t('report.focusRuntime') }}</p>
        <strong>{{ formatStatus(report.dockerVerification.status) }}</strong>
        <p>
          {{
            report.dockerVerification.requiresLogin
              ? report.dockerVerification.loginHint ?? t('report.loginRequired')
              : report.dockerVerification.strategy
          }}
        </p>
        <div class="chip-row">
          <span class="capsule emphasis">{{ report.dockerVerification.status }}</span>
          <span v-if="report.dockerVerification.requiresLogin" class="capsule warning-pill">
            {{ t('report.loginRequired') }}
          </span>
        </div>
      </article>
    </section>

    <section v-if="report" class="panel">
      <p class="eyebrow">{{ t('report.environmentTitle') }}</p>
      <div class="detail-grid">
        <article class="row-card">
          <strong>{{ t('report.environmentLanguages') }}</strong>
          <div class="chip-row">
            <span v-for="item in report.environment.languages" :key="item" class="capsule">{{ item }}</span>
            <span v-if="!report.environment.languages.length" class="capsule">-</span>
          </div>
        </article>
        <article class="row-card">
          <strong>{{ t('report.environmentFrameworks') }}</strong>
          <div class="chip-row">
            <span v-for="item in report.environment.frameworks" :key="item" class="capsule">{{ item }}</span>
            <span v-if="!report.environment.frameworks.length" class="capsule">-</span>
          </div>
        </article>
        <article class="row-card">
          <strong>{{ t('report.environmentRuntime') }}</strong>
          <div class="chip-row">
            <span v-for="item in report.environment.runtimeHints" :key="item" class="capsule">{{ item }}</span>
            <span v-if="!report.environment.runtimeHints.length" class="capsule">-</span>
          </div>
        </article>
        <article class="row-card">
          <strong>{{ t('report.environmentPackaging') }}</strong>
          <div class="chip-row">
            <span v-for="item in report.environment.packaging" :key="item" class="capsule">{{ item }}</span>
            <span v-if="!report.environment.packaging.length" class="capsule">-</span>
          </div>
        </article>
      </div>

      <div class="table-list">
        <article class="row-card">
          <strong>{{ t('report.environmentBuildFiles') }}</strong>
          <p v-for="item in report.environment.buildFiles" :key="item">{{ item }}</p>
          <p v-if="!report.environment.buildFiles.length">-</p>
        </article>
      </div>
    </section>

    <section v-if="report" class="two-column">
      <section class="panel">
        <p class="eyebrow">{{ t('report.dependenciesTitle') }}</p>
        <div v-if="report.dependencies.length" class="table-list">
          <article
            v-for="dependency in report.dependencies"
            :key="`${dependency.ecosystem}-${dependency.name}-${dependency.sourceFile}`"
            class="row-card"
          >
            <strong>{{ dependency.name }}</strong>
            <span>{{ dependency.ecosystem }} / {{ dependency.version ?? '-' }}</span>
            <p>{{ dependency.sourceFile }}</p>
            <small>{{ dependency.scope ?? '-' }}</small>
          </article>
        </div>
        <p v-else class="notice">{{ t('report.noDependencies') }}</p>
      </section>

      <section class="panel">
        <p class="eyebrow">{{ t('report.controlsTitle') }}</p>
        <div v-if="report.falsePositiveControls.length" class="table-list">
          <article v-for="control in report.falsePositiveControls" :key="control.rule" class="row-card">
            <strong>{{ control.rule }}</strong>
            <span :class="statusClass(control.verdict)">{{ formatStatus(control.verdict) }}</span>
            <p>{{ control.detail }}</p>
          </article>
        </div>
        <p v-else class="notice">{{ t('report.noControls') }}</p>
      </section>
    </section>

    <section v-if="report" class="panel">
      <p class="eyebrow">{{ t('report.exploitChainsTitle') }}</p>
      <div v-if="report.exploitChains.length" class="chain-stack">
        <div v-if="javaChains.length" class="table-list">
          <article class="section-flag">
            <strong>{{ t('report.javaChainsTitle') }}</strong>
          </article>
          <article v-for="chain in javaChains" :key="chain.id" class="row-card chain-card">
            <div class="chain-header">
              <div>
                <strong>{{ chain.name }}</strong>
                <span>{{ chain.category }} / {{ chain.confidence }}</span>
              </div>
              <div class="chip-row compact">
                <span class="capsule emphasis">{{ chain.confidence }}</span>
                <span class="capsule">{{ chain.checks.length }} {{ t('report.checks') }}</span>
              </div>
            </div>
            <p>{{ chain.rationale }}</p>
            <small>{{ t('report.prerequisites') }}: {{ chain.prerequisites.join(' -> ') || '-' }}</small>
            <small>{{ t('report.linkedFindings') }}: {{ chain.sourceFindings.join(', ') || '-' }}</small>
            <small>{{ t('report.nextStep') }}: {{ chain.nextStep }}</small>
            <div class="chip-row">
              <span v-for="item in chain.matchedDependencies" :key="item" class="capsule">{{ item }}</span>
            </div>
            <div class="check-list">
              <article v-for="check in chain.checks" :key="`${chain.id}-${check.target}`" class="check-card">
                <strong>{{ check.target }}</strong>
                <span :class="statusClass(check.status)">{{ formatStatus(check.status) }}</span>
                <p>{{ check.reason }}</p>
              </article>
            </div>
          </article>
        </div>

        <div v-if="nonJavaChains.length" class="table-list">
          <article class="section-flag">
            <strong>{{ t('report.otherChainsTitle') }}</strong>
          </article>
          <article v-for="chain in nonJavaChains" :key="chain.id" class="row-card chain-card">
            <div class="chain-header">
              <div>
                <strong>{{ chain.name }}</strong>
                <span>{{ chain.category }} / {{ chain.confidence }}</span>
              </div>
              <div class="chip-row compact">
                <span class="capsule">{{ chain.category }}</span>
              </div>
            </div>
            <p>{{ chain.rationale }}</p>
            <small>{{ t('report.prerequisites') }}: {{ chain.prerequisites.join(' -> ') || '-' }}</small>
            <small>{{ t('report.linkedFindings') }}: {{ chain.sourceFindings.join(', ') || '-' }}</small>
            <small>{{ t('report.nextStep') }}: {{ chain.nextStep }}</small>
            <div class="chip-row">
              <span v-for="item in chain.matchedDependencies" :key="item" class="capsule">{{ item }}</span>
            </div>
            <div class="check-list">
              <article v-for="check in chain.checks" :key="`${chain.id}-${check.target}`" class="check-card">
                <strong>{{ check.target }}</strong>
                <span :class="statusClass(check.status)">{{ formatStatus(check.status) }}</span>
                <p>{{ check.reason }}</p>
              </article>
            </div>
          </article>
        </div>
      </div>
      <p v-else class="notice">{{ t('report.noExploitChains') }}</p>
    </section>

    <section v-if="report" class="two-column">
      <section class="panel">
        <p class="eyebrow">{{ t('report.dockerTitle') }}</p>
        <article class="row-card">
          <strong>{{ formatStatus(report.dockerVerification.status) }}</strong>
          <p>{{ report.dockerVerification.strategy }}</p>
          <small v-if="report.dockerVerification.dockerfile">Dockerfile: {{ report.dockerVerification.dockerfile }}</small>
          <small v-if="report.dockerVerification.composeFile">Compose: {{ report.dockerVerification.composeFile }}</small>
          <small v-if="report.dockerVerification.imageTag">Image: {{ report.dockerVerification.imageTag }}</small>
          <small v-if="report.dockerVerification.containerName">Container: {{ report.dockerVerification.containerName }}</small>
          <small v-if="report.dockerVerification.loginHint">{{ report.dockerVerification.loginHint }}</small>

          <div v-if="report.dockerVerification.requiresLogin" class="runtime-alert">
            <strong>{{ t('report.loginRequired') }}</strong>
            <p>{{ report.dockerVerification.loginHint ?? t('report.loginRequired') }}</p>
          </div>
        </article>

        <div class="table-list">
          <article class="row-card">
            <strong>{{ t('report.commandsTitle') }}</strong>
            <pre v-for="command in report.dockerVerification.commands" :key="command" class="code-block">{{ command }}</pre>
            <p v-if="!report.dockerVerification.commands.length">{{ t('report.noCommands') }}</p>
          </article>
          <article class="row-card">
            <strong>{{ t('report.logsTitle') }}</strong>
            <pre v-for="log in report.dockerVerification.logs" :key="log" class="code-block">{{ log }}</pre>
            <p v-if="!report.dockerVerification.logs.length">{{ t('report.noLogs') }}</p>
          </article>
        </div>
      </section>

      <section class="panel">
        <p class="eyebrow">{{ t('report.endpointTitle') }}</p>
        <div class="table-list">
          <article
            v-for="endpoint in report.endpointMap"
            :key="`${endpoint.file}-${endpoint.handler}-${endpoint.path}`"
            class="row-card"
          >
            <strong>{{ endpoint.method }} {{ endpoint.path }}</strong>
            <span>{{ endpoint.framework }} / {{ endpoint.handler }}</span>
            <p>{{ endpoint.file }}</p>
            <small v-if="endpoint.flow.length">{{ endpoint.flow.join(' -> ') }}</small>
          </article>
        </div>
      </section>
    </section>

    <section v-if="report" class="panel">
      <p class="eyebrow">{{ t('report.findingTitle') }}</p>
      <div class="table-list">
        <article v-for="finding in report.findings" :key="finding.id" class="row-card finding-card">
          <div class="chain-header">
            <strong>{{ finding.title }}</strong>
            <span :class="statusClass(finding.severity)">{{ finding.severity }} / {{ finding.category }}</span>
          </div>
          <p>{{ finding.file }}:{{ finding.line }}</p>
          <small>{{ finding.summary }}</small>
          <small>{{ finding.evidence }}</small>
          <small v-if="finding.chain.length">{{ finding.chain.join(' -> ') }}</small>
        </article>
      </div>
    </section>

    <section v-if="report" class="two-column">
      <section class="panel">
        <p class="eyebrow">{{ t('report.testsTitle') }}</p>
        <div class="table-list">
          <article v-for="test in report.interfaceTests" :key="`${test.method}-${test.path}`" class="row-card">
            <strong>{{ test.method }} {{ test.path }}</strong>
            <p>{{ test.objective }}</p>
            <small>{{ test.payloadHint }}</small>
          </article>
        </div>
      </section>

      <section class="panel">
        <p class="eyebrow">{{ t('report.recommendationsTitle') }}</p>
        <div class="table-list">
          <article v-for="item in report.recommendations" :key="item" class="row-card">
            <p>{{ item }}</p>
          </article>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from '../i18n';
import { ApiError, fetchAudit, fetchAuditReport } from '../services/api';
import type { AuditJob, AuditReport } from '../types';

const route = useRoute();
const { locale, t } = useI18n();

const jobId = String(route.params.jobId);
const report = ref<AuditReport | null>(null);
const job = ref<AuditJob | null>(null);
const notReady = ref(false);
const loading = ref(false);
const errorMessage = ref('');
const pollHandle = ref<number | null>(null);

function isJavaChain(category: string) {
  return ['jndi', 'fastjson', 'hessian', 'xstream', 'deserialization', 'expression'].includes(category);
}

const javaChains = computed(() => report.value?.exploitChains.filter((item) => isJavaChain(item.category)) ?? []);
const nonJavaChains = computed(() => report.value?.exploitChains.filter((item) => !isJavaChain(item.category)) ?? []);
const featuredChain = computed(() => report.value?.exploitChains[0] ?? null);

function parseError(error: unknown) {
  if (error instanceof ApiError) {
    return error.message.replace(/^"+|"+$/g, '');
  }

  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}

function formatDate(value: string | null) {
  if (!value) {
    return '-';
  }
  return new Date(value).toLocaleString();
}

function formatStatus(value: string) {
  const statusMap: Record<string, { en: string; zh: string }> = {
    queued: { en: 'Queued', zh: '排队中' },
    running: { en: 'Running', zh: '运行中' },
    completed: { en: 'Completed', zh: '已完成' },
    failed: { en: 'Failed', zh: '失败' },
    pending: { en: 'Pending', zh: '待处理' },
    planned: { en: 'Planned', zh: '已规划' },
    skipped: { en: 'Skipped', zh: '已跳过' },
    kept: { en: 'Kept', zh: '保留' },
    demoted: { en: 'Demoted', zh: '降级' },
    blocked: { en: 'Blocked', zh: '阻断' },
    applicable: { en: 'Applicable', zh: '适用' },
    uncertain: { en: 'Uncertain', zh: '待确认' },
    critical: { en: 'Critical', zh: '严重' },
    high: { en: 'High', zh: '高危' },
    medium: { en: 'Medium', zh: '中危' },
    low: { en: 'Low', zh: '低危' },
    ready: { en: 'Ready', zh: '就绪' },
  };

  const translated = statusMap[value];
  if (!translated) {
    return value;
  }

  return locale.value === 'zh-CN' ? translated.zh : translated.en;
}

function statusClass(value: string) {
  if (['critical', 'high', 'failed', 'blocked'].includes(value)) {
    return 'status-high';
  }
  if (['medium', 'running', 'uncertain', 'demoted', 'planned'].includes(value)) {
    return 'status-medium';
  }
  if (['completed', 'applicable', 'kept', 'ready'].includes(value)) {
    return 'status-ok';
  }
  return 'status-neutral';
}

function startPolling() {
  if (pollHandle.value) {
    return;
  }

  pollHandle.value = window.setInterval(() => {
    void loadReport(false);
  }, 5000);
}

function stopPolling() {
  if (!pollHandle.value) {
    return;
  }

  window.clearInterval(pollHandle.value);
  pollHandle.value = null;
}

async function loadReport(showLoading = true) {
  if (showLoading) {
    loading.value = true;
  }
  errorMessage.value = '';
  notReady.value = false;

  try {
    report.value = await fetchAuditReport(locale.value, jobId);
    job.value = await fetchAudit(locale.value, jobId);
    stopPolling();
  } catch (error) {
    if (error instanceof ApiError && error.status === 409) {
      notReady.value = true;
      report.value = null;
      job.value = await fetchAudit(locale.value, jobId);
      startPolling();
    } else {
      errorMessage.value = parseError(error);
    }
  } finally {
    loading.value = false;
  }
}

watch(
  locale,
  () => {
    void loadReport();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.section-heading,
.job-top,
.progress-row,
.chain-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.page h1,
.job-top h2 {
  margin: 10px 0 0;
  font-size: clamp(2rem, 5vw, 3.8rem);
}

.job-top h2 {
  font-size: 1.4rem;
}

.ghost-button {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-main);
  cursor: pointer;
}

.ghost-button:disabled {
  opacity: 0.6;
  cursor: progress;
}

.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 18px;
  color: var(--text-soft);
}

.focus-grid,
.stats-grid,
.detail-grid,
.two-column {
  display: grid;
  gap: 16px;
}

.focus-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stats-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 24px;
}

.detail-grid,
.two-column {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.stat-card,
.row-card,
.check-card,
.focus-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.focus-card strong {
  display: block;
  margin-top: 8px;
  font-size: 1.2rem;
}

.stat-card span,
.row-card span,
.row-card p,
.row-card small,
.notice,
.job-top p,
.check-card span,
.check-card p,
.focus-card p {
  color: var(--text-dim);
}

.stat-card strong {
  display: block;
  margin-top: 8px;
  font-size: 2rem;
}

.warning {
  background:
    radial-gradient(circle at top right, rgba(255, 122, 26, 0.16), transparent 30%),
    rgba(255, 255, 255, 0.03);
}

.table-list,
.stack-list,
.check-list,
.chain-stack {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

.row-card strong,
.check-card strong {
  display: block;
  margin-bottom: 8px;
}

.chain-card,
.finding-card {
  background:
    radial-gradient(circle at top right, rgba(0, 212, 170, 0.08), transparent 26%),
    rgba(255, 255, 255, 0.03);
}

.section-flag {
  padding: 0 4px;
  color: var(--text-soft);
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.compact {
  margin-top: 0;
}

.progress-bar {
  margin-top: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(255, 122, 26, 0.95), rgba(0, 212, 170, 0.95));
}

.code-block {
  margin: 10px 0 0;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(4, 10, 14, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #d8fff2;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Consolas', 'SFMono-Regular', monospace;
  font-size: 0.9rem;
}

.runtime-alert {
  margin-top: 16px;
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 122, 26, 0.1);
  border: 1px solid rgba(255, 122, 26, 0.2);
}

.runtime-alert p {
  margin-bottom: 0;
}

.emphasis {
  border-color: rgba(0, 212, 170, 0.28);
  background: rgba(0, 212, 170, 0.14);
}

.warning-pill,
.status-high {
  color: #ffbf9f;
}

.status-high,
.status-medium,
.status-ok,
.status-neutral {
  display: inline-flex;
  padding: 4px 8px;
  border-radius: 999px;
}

.status-high {
  background: rgba(255, 122, 26, 0.12);
}

.status-medium {
  background: rgba(255, 211, 102, 0.1);
  color: #ffe29a;
}

.status-ok {
  background: rgba(0, 212, 170, 0.12);
  color: #84ffd9;
}

.status-neutral {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-soft);
}

.error-text {
  color: #ff9b6a;
}

@media (max-width: 960px) {
  .focus-grid,
  .stats-grid,
  .detail-grid,
  .two-column {
    grid-template-columns: 1fr;
  }

  .section-heading,
  .job-top,
  .chain-header {
    flex-direction: column;
  }
}
</style>
