<template>
  <div class="user-guide-overlay" v-if="isVisible">
    <div class="user-guide-modal">
      <div class="guide-header">
        <h2>🚀 {{ t('guide.welcomeTitle') }}</h2>
        <button class="close-btn" @click="closeGuide">✕</button>
      </div>
      
      <div class="guide-content">
        <div class="guide-steps">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="guide-step"
            :class="{ active: currentStep === index, completed: currentStep > index }"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
              <div v-if="step.tips" class="step-tips">
                <div v-for="tip in step.tips" :key="tip" class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span>{{ tip }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="guide-actions">
          <button 
            v-if="currentStep > 0" 
            class="btn-secondary"
            @click="prevStep"
          >
            {{ t('guide.previous') }}
          </button>
          <button 
            v-if="currentStep < steps.length - 1"
            class="btn-primary"
            @click="nextStep"
          >
            {{ t('guide.next') }}
          </button>
          <button 
            v-if="currentStep === steps.length - 1"
            class="btn-accent"
            @click="finishGuide"
          >
            {{ t('guide.startNow') }}
          </button>
        </div>
      </div>
      
      <div class="guide-footer">
        <label class="skip-checkbox">
          <input type="checkbox" v-model="dontShowAgain" />
          <span>{{ t('guide.dontShowAgain') }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from '../i18n';

const { t, locale } = useI18n();
const isVisible = ref(false);
const currentStep = ref(0);
const dontShowAgain = ref(false);

const steps = computed(() => [
  {
    title: locale.value === 'zh-CN' ? '配置模型' : 'Configure Model',
    description: locale.value === 'zh-CN' 
      ? '首先需要在设置页面配置AI模型，支持OpenAI、Anthropic、Gemini等多种模型。'
      : 'First, configure your AI model in the settings page. Supports OpenAI, Anthropic, Gemini, and more.',
    tips: locale.value === 'zh-CN' 
      ? ['至少配置一个模型才能开始审计', '可以使用API Key或OAuth认证']
      : ['At least one model is required to start auditing', 'API Key or OAuth authentication available']
  },
  {
    title: locale.value === 'zh-CN' ? '添加代码仓库' : 'Add Code Repository',
    description: locale.value === 'zh-CN'
      ? '在工作台添加要审计的代码仓库，支持Git URL或本地目录。'
      : 'Add the code repository to audit in the workspace. Supports Git URL or local directory.',
    tips: locale.value === 'zh-CN'
      ? ['Git仓库需要先同步代码', '本地目录会自动扫描文件']
      : ['Git repositories need to sync first', 'Local directories are automatically scanned']
  },
  {
    title: locale.value === 'zh-CN' ? '启动审计任务' : 'Start Audit Task',
    description: locale.value === 'zh-CN'
      ? '点击"启动审计"按钮开始自动化代码审计，系统会自动检测安全漏洞。'
      : 'Click "Start Audit" to begin automated code auditing. The system will detect security vulnerabilities.',
    tips: locale.value === 'zh-CN'
      ? ['审计过程可能需要几分钟', '可以实时查看进度和状态']
      : ['Audit process may take several minutes', 'View progress and status in real-time']
  },
  {
    title: locale.value === 'zh-CN' ? '查看审计报告' : 'View Audit Report',
    description: locale.value === 'zh-CN'
      ? '审计完成后查看详细报告，包括漏洞详情、利用链分析和修复建议。'
      : 'View detailed reports after audit completion, including vulnerability details, exploit chain analysis, and fix recommendations.',
    tips: locale.value === 'zh-CN'
      ? ['报告包含严重程度分级', '提供具体的修复建议和代码示例']
      : ['Reports include severity classification', 'Provides specific fix recommendations and code examples']
  }
]);

const emit = defineEmits<{
  close: [];
  finish: [];
}>();

function nextStep() {
  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

function closeGuide() {
  isVisible.value = false;
  emit('close');
}

function finishGuide() {
  if (dontShowAgain.value) {
    localStorage.setItem('canglong-guide-completed', 'true');
  }
  isVisible.value = false;
  emit('finish');
}

function showGuide() {
  const completed = localStorage.getItem('canglong-guide-completed');
  if (!completed) {
    isVisible.value = true;
  }
}

onMounted(() => {
  showGuide();
});

defineExpose({
  showGuide
});
</script>

<style scoped>
.user-guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.user-guide-modal {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 24px;
  max-width: 700px;
  width: 90%;
  max-height: 85vh;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 170, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 212, 170, 0.05);
}

.guide-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #00d4aa;
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 107, 107, 0.3);
}

.guide-content {
  padding: 28px;
  max-height: 60vh;
  overflow-y: auto;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.guide-step {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s;
}

.guide-step.active {
  background: rgba(0, 212, 170, 0.1);
  border-color: rgba(0, 212, 170, 0.3);
}

.guide-step.completed {
  opacity: 0.6;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 212, 170, 0.2);
  color: #00d4aa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.guide-step.active .step-number {
  background: #00d4aa;
  color: #1a1a2e;
}

.step-content h3 {
  margin: 0 0 8px;
  color: #fff;
  font-size: 1.1rem;
}

.step-content p {
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.step-tips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.tip-icon {
  font-size: 1rem;
}

.guide-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.guide-actions button {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-primary {
  background: rgba(0, 212, 170, 0.2);
  color: #00d4aa;
  border: 1px solid rgba(0, 212, 170, 0.3);
}

.btn-primary:hover {
  background: rgba(0, 212, 170, 0.3);
}

.btn-accent {
  background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
  color: #1a1a2e;
  font-weight: 600;
}

.btn-accent:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 170, 0.4);
}

.guide-footer {
  padding: 16px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.skip-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.skip-checkbox input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}
</style>
