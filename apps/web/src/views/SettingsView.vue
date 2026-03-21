<template>
  <div class="page">
    <section class="hero panel">
      <div>
        <p class="eyebrow">{{ t('settings.heroEyebrow') }}</p>
        <h1>{{ t('settings.title') }}</h1>
        <p class="hero-copy">{{ t('settings.description') }}</p>
      </div>

      <article class="readiness-card">
        <p class="eyebrow">{{ t('settings.readinessEyebrow') }}</p>
        <h3>{{ settings?.hasUsableModel ? t('settings.readinessReady') : t('settings.readinessMissing') }}</h3>
        <p>{{ t('settings.defaultModel') }}: {{ settings?.defaultModelLabel ?? '-' }}</p>
        <p>{{ t('settings.readinessNextAction') }}: {{ settings?.nextAction ?? '-' }}</p>
      </article>
    </section>

    <section class="two-column">
      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.guidanceEyebrow') }}</p>
            <h2>{{ t('settings.guidanceTitle') }}</h2>
          </div>
        </div>
        <div class="guidance-list">
          <article v-for="item in settings?.guidance ?? []" :key="item" class="guidance-card">
            <p>{{ item }}</p>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.customEyebrow') }}</p>
            <h2>{{ t('settings.customTitle') }}</h2>
          </div>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>

        <form class="config-form" @submit.prevent="handleCreateCustom">
          <input v-model="customForm.displayName" :placeholder="t('settings.formDisplayName')" />
          <input v-model="customForm.provider" :placeholder="t('settings.formProvider')" />
          <input v-model="customForm.modelSlug" :placeholder="t('settings.formModelSlug')" />
          <input v-model="customForm.baseUrl" :placeholder="t('settings.formBaseUrl')" />
          <input v-model="customForm.description" :placeholder="t('settings.formDescription')" />
          <input v-model="customForm.apiKey" type="password" :placeholder="t('settings.formApiKey')" />
          <input v-model="customForm.tagsInput" :placeholder="t('settings.formTags')" />
          <label class="checkbox-row">
            <input v-model="customForm.enabled" type="checkbox" />
            <span>{{ t('settings.formEnabled') }}</span>
          </label>
          <small>{{ t('settings.emptyTagsHint') }}</small>
          <button type="submit" :disabled="creatingCustom">
            {{ creatingCustom ? t('settings.creating') : t('settings.create') }}
          </button>
        </form>
      </section>
    </section>

    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('settings.listEyebrow') }}</p>
          <h2>{{ t('settings.listTitle') }}</h2>
        </div>
      </div>

      <p v-if="loading" class="hero-copy">{{ t('report.loading') }}</p>

      <div v-else class="model-grid">
        <article v-for="model in modelForms" :key="model.id" class="model-card">
          <div class="model-top">
            <div>
              <h3>{{ model.displayName }}</h3>
              <p>{{ model.provider }}</p>
            </div>
            <div class="badge-row">
              <span class="capsule">{{ model.status === 'configured' ? t('settings.statusConfigured') : t('settings.statusIncomplete') }}</span>
              <span v-if="model.isDefault" class="capsule accent-pill">{{ t('settings.defaultBadge') }}</span>
            </div>
          </div>

          <p class="model-description">{{ model.description }}</p>
          <p class="model-hint">{{ model.setupHint }}</p>

          <form class="config-form" @submit.prevent="handleSaveModel(model.id)">
            <input v-model="model.displayName" :placeholder="t('settings.formDisplayName')" />
            <input v-model="model.provider" :placeholder="t('settings.formProvider')" />
            <input v-model="model.modelSlug" :placeholder="t('settings.formModelSlug')" />
            <input v-model="model.baseUrl" :placeholder="t('settings.formBaseUrl')" />
            <input v-model="model.description" :placeholder="t('settings.formDescription')" />
            <input v-model="model.apiKey" type="password" :placeholder="t('settings.formApiKey')" />
            <input v-model="model.tagsInput" :placeholder="t('settings.formTags')" />
            <label class="checkbox-row">
              <input v-model="model.enabled" type="checkbox" />
              <span>{{ t('settings.formEnabled') }}</span>
            </label>
            <div class="meta-row">
              <span>{{ model.apiKeySet ? t('settings.apiKeyConfigured') : t('settings.apiKeyMissing') }}</span>
              <span v-if="model.apiKeyPreview">{{ model.apiKeyPreview }}</span>
            </div>
            <div class="action-row">
              <button type="submit" :disabled="savingId === model.id">
                {{ savingId === model.id ? t('settings.saving') : t('settings.save') }}
              </button>
              <button
                type="button"
                class="secondary-button"
                :disabled="settingDefaultId === model.id"
                @click="handleSetDefault(model.id)"
              >
                {{ settingDefaultId === model.id ? t('settings.saving') : t('settings.setDefault') }}
              </button>
            </div>
          </form>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { useI18n } from '../i18n';
import {
  ApiError,
  createModelSettings,
  fetchModelSettings,
  setDefaultModel,
  updateModelSettings,
} from '../services/api';
import type { ModelConnection, ModelSettingsData } from '../types';

type EditableModel = ModelConnection & { apiKey: string; tagsInput: string };

const { locale, t } = useI18n();

const settings = ref<ModelSettingsData | null>(null);
const modelForms = ref<EditableModel[]>([]);
const loading = ref(true);
const savingId = ref<string | null>(null);
const settingDefaultId = ref<string | null>(null);
const creatingCustom = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const customForm = reactive({
  displayName: '',
  provider: '',
  modelSlug: '',
  baseUrl: '',
  description: '',
  apiKey: '',
  tagsInput: '',
  enabled: true,
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

function toEditableModel(model: ModelConnection): EditableModel {
  return {
    ...model,
    apiKey: '',
    tagsInput: model.capabilityTags.join(', '),
  };
}

function parseTags(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

async function loadSettings() {
  loading.value = true;
  errorMessage.value = '';
  try {
    settings.value = await fetchModelSettings(locale.value);
    modelForms.value = settings.value.models.map(toEditableModel);
  } catch (error) {
    errorMessage.value = `${t('settings.loadError')} ${parseError(error)}`;
  } finally {
    loading.value = false;
  }
}

async function handleSaveModel(modelId: string) {
  const model = modelForms.value.find((item) => item.id === modelId);
  if (!model) {
    return;
  }
  savingId.value = modelId;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    await updateModelSettings(locale.value, modelId, {
      displayName: model.displayName,
      provider: model.provider,
      modelSlug: model.modelSlug,
      description: model.description,
      baseUrl: model.baseUrl,
      apiKey: model.apiKey || undefined,
      enabled: model.enabled,
      capabilityTags: parseTags(model.tagsInput),
    });
    successMessage.value = t('settings.saveSuccess');
    await loadSettings();
  } catch (error) {
    errorMessage.value = parseError(error);
  } finally {
    savingId.value = null;
  }
}

async function handleSetDefault(modelId: string) {
  settingDefaultId.value = modelId;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    await setDefaultModel(locale.value, modelId);
    successMessage.value = t('settings.defaultSuccess');
    await loadSettings();
  } catch (error) {
    errorMessage.value = parseError(error);
  } finally {
    settingDefaultId.value = null;
  }
}

async function handleCreateCustom() {
  creatingCustom.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    await createModelSettings(locale.value, {
      displayName: customForm.displayName,
      provider: customForm.provider,
      modelSlug: customForm.modelSlug,
      description: customForm.description,
      baseUrl: customForm.baseUrl,
      apiKey: customForm.apiKey || undefined,
      enabled: customForm.enabled,
      capabilityTags: parseTags(customForm.tagsInput),
    });
    successMessage.value = t('settings.createSuccess');
    customForm.displayName = '';
    customForm.provider = '';
    customForm.modelSlug = '';
    customForm.baseUrl = '';
    customForm.description = '';
    customForm.apiKey = '';
    customForm.tagsInput = '';
    customForm.enabled = true;
    await loadSettings();
  } catch (error) {
    errorMessage.value = parseError(error);
  } finally {
    creatingCustom.value = false;
  }
}

watch(
  locale,
  () => {
    void loadSettings();
  },
  { immediate: true },
);
</script>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.hero,
.two-column {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
}

.hero h1 {
  margin: 10px 0 12px;
  font-size: clamp(2rem, 5vw, 3.8rem);
  line-height: 1;
}

.hero-copy,
.readiness-card p,
.guidance-card p,
.model-description,
.model-hint {
  color: var(--text-dim);
}

.readiness-card,
.guidance-card,
.model-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
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

.guidance-list,
.model-grid {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

.model-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.model-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.model-top h3 {
  margin: 0;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.accent-pill {
  background: rgba(0, 212, 170, 0.16);
  border-color: rgba(0, 212, 170, 0.24);
}

.config-form {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.config-form input,
.config-form button {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-main);
}

.config-form button,
.secondary-button {
  cursor: pointer;
}

.config-form button {
  background: rgba(0, 212, 170, 0.16);
  border-color: rgba(0, 212, 170, 0.3);
}

.secondary-button {
  background: rgba(255, 255, 255, 0.05) !important;
}

.checkbox-row,
.meta-row,
.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.checkbox-row span,
.meta-row {
  color: var(--text-soft);
}

.action-row {
  justify-content: space-between;
}

.success-text {
  color: #84ffd9;
}

.error-text {
  color: #ff9b6a;
}

@media (max-width: 1100px) {
  .hero,
  .two-column,
  .model-grid {
    grid-template-columns: 1fr;
  }

  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
