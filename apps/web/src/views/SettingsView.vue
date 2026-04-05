<template>
  <!--
    SettingsView - 设置页面组件
    SettingsView - Settings page component
    
    管理LLM模型配置和系统设置
    Manages LLM model configurations and system settings
  -->
  <div class="page">
    <!-- 英雄区域 / Hero section -->
    <section class="hero panel">
      <div class="hero-content">
        <p class="eyebrow">{{ t('settings.heroEyebrow') }}</p>
        <h1>{{ t('settings.title') }}</h1>
        <p class="hero-copy">{{ t('settings.description') }}</p>
      </div>

      <!-- 就绪状态卡片 / Readiness status card -->
      <article class="readiness-card" :class="{ 'is-ready': settings?.hasUsableModel }">
        <p class="eyebrow">{{ t('settings.readinessEyebrow') }}</p>
        <h3>{{ settings?.hasUsableModel ? t('settings.readinessReady') : t('settings.readinessMissing') }}</h3>
        <p>{{ t('settings.defaultModel') }}: {{ settings?.defaultModelLabel ?? '-' }}</p>
        <p>{{ t('settings.readinessNextAction') }}: {{ settings?.nextAction ?? '-' }}</p>
      </article>
    </section>

    <!-- 双列布局区域 / Two-column layout section -->
    <section class="two-column">
      <!-- 配置指南 / Configuration guidance -->
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

      <!-- 自定义模型创建 / Custom model creation -->
      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.customEyebrow') }}</p>
            <h2>{{ t('settings.customTitle') }}</h2>
          </div>
        </div>

        <!-- 消息提示 / Message alerts -->
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>

        <!-- 创建表单 / Creation form -->
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
          <button type="submit" :disabled="creatingCustom" class="btn-primary">
            {{ creatingCustom ? t('settings.creating') : t('settings.create') }}
          </button>
        </form>
      </section>
    </section>

    <!-- 模型列表 / Model list -->
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
            <div class="model-info">
              <h3>{{ model.displayName }}</h3>
              <p>{{ model.provider }}</p>
            </div>
            <div class="badge-row">
              <span class="capsule" :class="model.status === 'configured' ? 'status-configured' : 'status-incomplete'">
                {{ model.status === 'configured' ? t('settings.statusConfigured') : t('settings.statusIncomplete') }}
              </span>
              <span v-if="model.isDefault" class="capsule status-default">{{ t('settings.defaultBadge') }}</span>
            </div>
          </div>

          <p class="model-description">{{ model.description }}</p>
          <p class="model-hint">{{ model.setupHint }}</p>

          <!-- 模型编辑表单 / Model edit form -->
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
              <span v-if="model.apiKeyPreview" class="api-preview">{{ model.apiKeyPreview }}</span>
            </div>
            <div class="action-row">
              <button type="submit" :disabled="savingId === model.id" class="btn-primary">
                {{ savingId === model.id ? t('settings.saving') : t('settings.save') }}
              </button>
              <button
                type="button"
                class="btn-secondary"
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
/**
 * SettingsView 组件脚本
 * SettingsView component script
 * 
 * 管理模型配置的状态和操作
 * Manages model configuration state and operations
 */
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

// 可编辑模型类型 / Editable model type
type EditableModel = ModelConnection & { apiKey: string; tagsInput: string };

// 国际化钩子 / i18n hook
const { locale, t } = useI18n();

// 状态管理 / State management
const settings = ref<ModelSettingsData | null>(null);
const modelForms = ref<EditableModel[]>([]);
const loading = ref(true);
const savingId = ref<string | null>(null);
const settingDefaultId = ref<string | null>(null);
const creatingCustom = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// 自定义模型表单 / Custom model form
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

/**
 * 解析错误信息
 * Parse error message
 * 
 * 从API错误中提取可读的错误消息
 * Extracts readable error message from API error
 */
function parseError(error: unknown) {
  if (error instanceof ApiError) {
    return error.message.replace(/^"+|"+$/g, '');
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

/**
 * 转换为可编辑模型
 * Convert to editable model
 * 
 * 将模型连接对象转换为可编辑表单对象
 * Converts model connection object to editable form object
 */
function toEditableModel(model: ModelConnection): EditableModel {
  return {
    ...model,
    apiKey: '',
    tagsInput: model.capabilityTags.join(', '),
  };
}

/**
 * 解析标签字符串
 * Parse tags string
 * 
 * 将逗号分隔的标签字符串转换为数组
 * Converts comma-separated tags string to array
 */
function parseTags(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

/**
 * 加载设置数据
 * Load settings data
 * 
 * 从API获取模型设置并更新表单状态
 * Fetches model settings from API and updates form state
 */
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

/**
 * 保存模型设置
 * Save model settings
 * 
 * 更新指定模型的配置
 * Updates configuration for specified model
 */
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

/**
 * 设置默认模型
 * Set default model
 * 
 * 将指定模型设置为默认使用
 * Sets specified model as default
 */
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

/**
 * 创建自定义模型
 * Create custom model
 * 
 * 添加新的自定义模型配置
 * Adds new custom model configuration
 */
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
    // 重置表单 / Reset form
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

// 监听语言变化并重新加载数据 / Watch locale changes and reload data
watch(
  locale,
  () => {
    void loadSettings();
  },
  { immediate: true },
);
</script>

<style scoped>
/*
  设置页面样式 - 商业化设计系统
  Settings page styles - Commercial design system
  
  使用CSS变量实现一致的品牌视觉
  Uses CSS variables for consistent brand visuals
*/

/* 页面容器 / Page container */
.page {
  display: grid;
  gap: 24px;
}

/* 英雄区域和双列布局 / Hero and two-column layout */
.hero,
.two-column {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
}

/* 英雄区域样式 / Hero section styles */
.hero {
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 34%),
    radial-gradient(circle at right, rgba(16, 185, 129, 0.1), transparent 38%),
    rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* 英雄内容区域 / Hero content area */
.hero-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 英雄标题 / Hero title */
.hero h1 {
  margin: 10px 0 12px;
  font-size: clamp(2rem, 5vw, 3.8rem);
  line-height: 1;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 英雄说明文字 / Hero description */
.hero-copy {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 就绪状态卡片 / Readiness card */
.readiness-card {
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

/* 就绪状态 - 已就绪 / Readiness - Ready */
.readiness-card.is-ready {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.2);
}

/* 就绪状态 - 未就绪 / Readiness - Not ready */
.readiness-card:not(.is-ready) {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.2);
}

/* 就绪卡片标题 / Readiness card title */
.readiness-card h3 {
  margin: 8px 0;
  color: var(--text-primary);
}

/* 就绪卡片段落 / Readiness card paragraph */
.readiness-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 4px 0;
}

/* 章节标题 / Section heading */
.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

/* 章节标题文字 / Section heading text */
.section-heading h2 {
  margin: 8px 0 0;
  color: var(--text-primary);
}

/* 指南列表 / Guidance list */
.guidance-list,
.model-grid {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

/* 模型网格 / Model grid */
.model-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

/* 指南卡片 / Guidance card */
.guidance-card {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

/* 指南卡片悬停 / Guidance card hover */
.guidance-card:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.15);
}

/* 指南卡片文字 / Guidance card text */
.guidance-card p {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* 模型卡片 / Model card */
.model-card {
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

/* 模型卡片悬停 / Model card hover */
.model-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

/* 模型顶部区域 / Model top area */
.model-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

/* 模型信息 / Model info */
.model-info h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.model-info p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* 徽章行 / Badge row */
.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 状态徽章 - 已配置 / Status badge - Configured */
.capsule.status-configured {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-accent);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* 状态徽章 - 未完成 / Status badge - Incomplete */
.capsule.status-incomplete {
  background: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* 状态徽章 - 默认 / Status badge - Default */
.capsule.status-default {
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* 模型描述 / Model description */
.model-description,
.model-hint {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 12px 0 0;
}

/* 配置表单 / Config form */
.config-form {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

/* 表单输入框 / Form inputs */
.config-form input {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

/* 输入框聚焦 / Input focus */
.config-form input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 输入框占位符 / Input placeholder */
.config-form input::placeholder {
  color: var(--text-muted);
}

/* 主按钮 / Primary button */
.btn-primary {
  padding: 12px 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, #2563eb 100%);
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

/* 主按钮悬停 / Primary button hover */
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
}

/* 主按钮禁用 / Primary button disabled */
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 次要按钮 / Secondary button */
.btn-secondary {
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 次要按钮悬停 / Secondary button hover */
.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 次要按钮禁用 / Secondary button disabled */
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 复选框行 / Checkbox row */
.checkbox-row {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

/* 复选框文字 / Checkbox text */
.checkbox-row span {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 复选框样式 / Checkbox style */
.checkbox-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

/* 元数据行 / Meta row */
.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

/* API预览 / API preview */
.api-preview {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 6px;
}

/* 操作行 / Action row */
.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

/* 成功提示文字 / Success text */
.success-text {
  color: var(--color-accent);
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  font-size: 0.9rem;
}

/* 错误提示文字 / Error text */
.error-text {
  color: var(--color-danger);
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  font-size: 0.9rem;
}

/* 小提示文字 / Small hint text */
small {
  color: var(--text-muted);
  font-size: 0.75rem;
}

/* 响应式设计 - 中等屏幕 / Responsive - Medium screens */
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

/* 响应式设计 - 小屏幕 / Responsive - Small screens */
@media (max-width: 760px) {
  .model-top {
    flex-direction: column;
    gap: 12px;
  }
  
  .badge-row {
    align-self: flex-start;
  }
}
</style>
