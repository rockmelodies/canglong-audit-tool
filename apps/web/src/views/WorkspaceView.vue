<template>
  <div class="page">
    <section class="hero panel workspace-hero">
      <div>
        <p class="eyebrow">{{ t('workspace.heroEyebrow') }}</p>
        <h1>{{ t('workspace.title') }}</h1>
        <p>{{ t('workspace.description') }}</p>
      </div>

      <article class="helper-card">
        <p class="eyebrow">{{ t('workspace.helperTitle') }}</p>
        <p>{{ t('workspace.helperBody') }}</p>
      </article>
    </section>

    <section class="workspace-grid">
      <section class="panel">
        <p class="eyebrow">{{ t('workspace.readinessEyebrow') }}</p>
        <h2>{{ modelReady ? t('workspace.readinessReady') : t('workspace.readinessMissing') }}</h2>
        <p class="form-helper">{{ modelNextAction }}</p>
        <button type="button" class="settings-link" @click="router.push('/settings')">
          {{ t('workspace.readinessAction') }}
        </button>
      </section>

      <section class="panel">
        <p class="eyebrow">{{ t('workspace.guideTitle') }}</p>
        <div class="guide-list">
          <article class="guide-card">{{ t('workspace.guideStepOne') }}</article>
          <article class="guide-card">{{ t('workspace.guideStepTwo') }}</article>
          <article class="guide-card">{{ t('workspace.guideStepThree') }}</article>
        </div>
      </section>
    </section>

    <section class="workspace-grid">
      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('workspace.repoSectionEyebrow') }}</p>
            <h2>{{ t('workspace.repoSectionTitle') }}</h2>
          </div>
        </div>

        <p v-if="workspaceError" class="error-text">{{ workspaceError }}</p>
        <p v-if="feedbackMessage" class="success-text">{{ feedbackMessage }}</p>

        <form class="repo-form" @submit.prevent="handleCreateRepo">
          <div class="source-switch">
            <button
              type="button"
              class="source-option"
              :class="{ active: form.sourceType === 'git' }"
              @click="form.sourceType = 'git'"
            >
              {{ t('workspace.formSourceGit') }}
            </button>
            <button
              type="button"
              class="source-option"
              :class="{ active: form.sourceType === 'local' }"
              @click="form.sourceType = 'local'"
            >
              {{ t('workspace.formSourceLocal') }}
            </button>
          </div>

          <p class="form-helper">
            {{ form.sourceType === 'git' ? t('workspace.formHelpGit') : t('workspace.formHelpLocal') }}
          </p>

          <input v-model="form.name" :placeholder="t('workspace.formName')" />
          <input
            v-if="form.sourceType === 'git'"
            v-model="form.url"
            :placeholder="t('workspace.formUrl')"
          />
          <input
            v-else
            v-model="form.localPath"
            :placeholder="t('workspace.formLocalPath')"
          />
          <input v-model="form.branch" :placeholder="t('workspace.formBranch')" />
          <input v-model="form.defaultBaseUrl" :placeholder="t('workspace.formBaseUrl')" />
          <button type="submit" :disabled="creatingRepo">
            {{ creatingRepo ? t('workspace.creatingRepo') : t('workspace.formSubmit') }}
          </button>
        </form>

        <div v-if="loading" class="empty-state">{{ t('report.loading') }}</div>
        <div v-else-if="repos.length" class="repo-list">
          <article v-for="repo in repos" :key="repo.id" class="repo-card">
            <div class="repo-top">
              <div>
                <h3>{{ repo.name }}</h3>
                <p>{{ repo.url }}</p>
              </div>
              <div class="status-column">
                <span class="capsule">{{ formatSourceType(repo.sourceType) }}</span>
                <span class="capsule status-pill">{{ formatStatus(repo.status) }}</span>
              </div>
            </div>

            <div class="repo-meta">
              <span>{{ repo.branch }}</span>
              <span>{{ t('workspace.sourceType') }}: {{ repo.provider }}</span>
              <span>{{ t('workspace.localPath') }}: {{ repo.localPath }}</span>
            </div>

            <p class="repo-summary">{{ repo.summary }}</p>

            <div class="repo-meta">
              <span>{{ t('workspace.lastSync') }}: {{ formatDate(repo.lastSyncAt) }}</span>
              <span>{{ t('workspace.lastAudit') }}: {{ formatDate(repo.lastAuditAt) }}</span>
            </div>

            <div class="repo-actions">
              <p class="action-hint">{{ t('workspace.repoActionHint') }}</p>
              <button type="button" :disabled="syncingRepoId === repo.id" @click="handleSync(repo.id)">
                {{ syncingRepoId === repo.id ? t('workspace.syncing') : t('workspace.sync') }}
              </button>
              <button
                type="button"
                class="accent"
                :disabled="auditingRepoId === repo.id"
                @click="handleStartAudit(repo.id)"
              >
                {{ auditingRepoId === repo.id ? t('workspace.startingAudit') : t('workspace.startAuditStep') }}
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-state">{{ t('workspace.noRepos') }}</p>
      </section>

      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('workspace.auditSectionEyebrow') }}</p>
            <h2>{{ t('workspace.auditSectionTitle') }}</h2>
          </div>
        </div>

        <div v-if="loading" class="empty-state">{{ t('report.loading') }}</div>
        <div v-else-if="audits.length" class="audit-list">
          <article v-for="audit in audits" :key="audit.id" class="audit-card">
            <div class="repo-top">
              <div>
                <h3>{{ audit.repoName }}</h3>
                <p>{{ audit.currentStep }}</p>
              </div>
              <div class="status-column">
                <span class="capsule status-pill">{{ formatStatus(audit.status) }}</span>
                <span class="capsule">{{ formatStatus(audit.verificationStatus) }}</span>
              </div>
            </div>

            <div class="progress-row">
              <span>{{ t('workspace.progress') }}</span>
              <strong>{{ audit.progress }}%</strong>
            </div>
            <div class="progress-bar">
              <span :style="{ width: `${audit.progress}%` }"></span>
            </div>

            <div class="repo-meta">
              <span>{{ t('workspace.findingsCount', { count: audit.findings }) }}</span>
              <span>{{ t('workspace.endpointsCount', { count: audit.endpoints }) }}</span>
              <span>{{ t('workspace.verification') }}: {{ formatStatus(audit.verificationStatus) }}</span>
              <span>{{ t('workspace.updatedAt') }}: {{ formatDate(audit.updatedAt) }}</span>
            </div>

            <div class="stage-list">
              <div v-for="stage in audit.stages" :key="stage.name" class="stage-item">
                <strong>{{ stage.name }}</strong>
                <span>{{ formatStatus(stage.status) }}</span>
                <p>{{ stage.detail }}</p>
              </div>
            </div>

            <div class="repo-actions">
              <button
                v-if="audit.reportId"
                type="button"
                class="accent"
                @click="router.push(`/reports/${audit.id}`)"
              >
                {{ t('workspace.viewReport') }}
              </button>
            </div>

            <p v-if="audit.error" class="error-text">{{ audit.error }}</p>
          </article>
        </div>
        <p v-else class="empty-state">{{ t('workspace.noAudits') }}</p>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from '../i18n';
import { ApiError, createRepo, fetchAudits, fetchModelSettings, fetchRepos, startAudit, syncRepo } from '../services/api';
import type { AuditJob, RepoConfig } from '../types';

const router = useRouter();
const { locale, t } = useI18n();

const repos = ref<RepoConfig[]>([]);
const audits = ref<AuditJob[]>([]);
const loading = ref(true);
const creatingRepo = ref(false);
const syncingRepoId = ref<string | null>(null);
const auditingRepoId = ref<string | null>(null);
const workspaceError = ref('');
const feedbackMessage = ref('');
const pollHandle = ref<number | null>(null);
const modelReady = ref(false);
const modelNextAction = ref('');

const form = reactive({
  sourceType: 'git' as 'git' | 'local',
  name: '',
  url: '',
  localPath: '',
  branch: 'main',
  defaultBaseUrl: '',
});

function parseError(error: unknown) {
  if (error instanceof ApiError) {
    return error.message.replace(/^"+|"+$/g, '');
  }

  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}

function clearMessages() {
  workspaceError.value = '';
  feedbackMessage.value = '';
}

async function loadWorkspace(showLoading = true) {
  if (showLoading) {
    loading.value = true;
  }
  workspaceError.value = '';

  try {
    const [repoData, auditData, modelSettings] = await Promise.all([
      fetchRepos(locale.value),
      fetchAudits(locale.value),
      fetchModelSettings(locale.value),
    ]);
    repos.value = repoData;
    audits.value = auditData;
    modelReady.value = modelSettings.hasUsableModel;
    modelNextAction.value = modelSettings.nextAction;
  } catch (error) {
    workspaceError.value = `${t('workspace.loadError')} ${parseError(error)}`;
  } finally {
    loading.value = false;
  }
}

async function handleCreateRepo() {
  clearMessages();
  const isGit = form.sourceType === 'git';
  if (isGit && !form.url.trim()) {
    workspaceError.value = t('workspace.invalidGitUrl');
    return;
  }
  if (!isGit && !form.localPath.trim()) {
    workspaceError.value = t('workspace.invalidLocalPath');
    return;
  }

  creatingRepo.value = true;
  try {
    await createRepo(locale.value, {
      sourceType: form.sourceType,
      name: form.name || undefined,
      url: isGit ? form.url : undefined,
      localPath: isGit ? undefined : form.localPath,
      branch: form.branch || 'main',
      defaultBaseUrl: form.defaultBaseUrl || undefined,
    });
    feedbackMessage.value = t('workspace.createSuccess');
    form.name = '';
    form.url = '';
    form.localPath = '';
    form.branch = 'main';
    form.defaultBaseUrl = '';
    await loadWorkspace(false);
  } catch (error) {
    workspaceError.value = parseError(error);
  } finally {
    creatingRepo.value = false;
  }
}

async function handleSync(repoId: string) {
  clearMessages();
  syncingRepoId.value = repoId;
  try {
    await syncRepo(locale.value, repoId);
    feedbackMessage.value = t('workspace.syncSuccess');
    await loadWorkspace(false);
  } catch (error) {
    workspaceError.value = parseError(error);
  } finally {
    syncingRepoId.value = null;
  }
}

async function handleStartAudit(repoId: string) {
  clearMessages();
  auditingRepoId.value = repoId;
  try {
    await startAudit(locale.value, repoId);
    feedbackMessage.value = t('workspace.auditSuccess');
    await loadWorkspace(false);
  } catch (error) {
    workspaceError.value = parseError(error);
  } finally {
    auditingRepoId.value = null;
  }
}

function formatDate(value: string | null) {
  if (!value) {
    return '-';
  }
  return new Date(value).toLocaleString();
}

function formatSourceType(value: string) {
  if (value === 'local') {
    return t('workspace.formSourceLocal');
  }
  return t('workspace.formSourceGit');
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
    ready: { en: 'Ready', zh: '就绪' },
    idle: { en: 'Idle', zh: '空闲' },
    sync_failed: { en: 'Sync failed', zh: '同步失败' },
    audit_failed: { en: 'Audit failed', zh: '审计失败' },
  };

  const translated = statusMap[value];
  if (!translated) {
    return value;
  }

  return locale.value === 'zh-CN' ? translated.zh : translated.en;
}

onMounted(async () => {
  await loadWorkspace();
  pollHandle.value = window.setInterval(() => {
    void loadWorkspace(false);
  }, 5000);
});

watch(locale, () => {
  void loadWorkspace();
});

onBeforeUnmount(() => {
  if (pollHandle.value) {
    window.clearInterval(pollHandle.value);
  }
});
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.workspace-hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
  align-items: start;
}

.workspace-hero h1 {
  margin: 10px 0 12px;
  font-size: clamp(2rem, 5vw, 3.8rem);
  line-height: 1;
}

.workspace-hero p:last-child {
  max-width: 64ch;
  color: var(--text-dim);
}

.helper-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.helper-card p:last-child {
  margin-bottom: 0;
  color: var(--text-dim);
}

.workspace-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 24px;
}

.guide-list {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.guide-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-soft);
}

.section-heading h2 {
  margin: 8px 0 0;
}

.repo-form {
  display: grid;
  gap: 12px;
  margin-top: 22px;
}

.source-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.source-option,
.repo-form input,
.repo-form button,
.repo-actions button {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-main);
}

.source-option,
.repo-form button,
.repo-actions button {
  cursor: pointer;
}

.source-option.active,
.repo-form button,
.repo-actions .accent {
  background: rgba(0, 212, 170, 0.16);
  border-color: rgba(0, 212, 170, 0.3);
}

.repo-form button:disabled,
.repo-actions button:disabled {
  opacity: 0.6;
  cursor: progress;
}

.form-helper,
.repo-top p,
.repo-summary,
.stage-item p,
.empty-state {
  color: var(--text-dim);
}

.repo-list,
.audit-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.repo-card,
.audit-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.repo-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.repo-top h3 {
  margin: 0;
}

.status-column {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.status-pill {
  background: rgba(255, 122, 26, 0.16);
  border-color: rgba(255, 122, 26, 0.2);
}

.repo-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 14px;
  color: var(--text-soft);
}

.repo-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.action-hint {
  width: 100%;
  margin: 0;
  color: var(--text-dim);
}

.settings-link {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(0, 212, 170, 0.28);
  background: rgba(0, 212, 170, 0.14);
  color: var(--text-main);
  cursor: pointer;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  margin-top: 18px;
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

.stage-list {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.stage-item {
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.stage-item span {
  display: block;
  margin-top: 6px;
  color: var(--text-soft);
}

.success-text {
  color: #84ffd9;
}

.error-text {
  color: #ff9b6a;
}

@media (max-width: 1100px) {
  .workspace-hero,
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}
</style>
