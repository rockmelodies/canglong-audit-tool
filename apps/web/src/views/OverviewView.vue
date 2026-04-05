<template>
  <!--
    OverviewView - 概览页面组件
    OverviewView - Overview page component
    
    展示审计仪表板，包含关键指标、威胁流程、能力网格等
    Displays audit dashboard with key metrics, threat flow, capability grid, etc.
  -->
  <div class="page">
    <!-- 英雄区域 / Hero section -->
    <section class="hero panel">
      <div class="hero-content">
        <p class="eyebrow">{{ t('overview.heroEyebrow') }}</p>
        <h1>{{ dashboard.codename }} / {{ dashboard.repository }}</h1>
        <p class="hero-copy">{{ t('overview.focusPrefix') }}: {{ dashboard.focus }}</p>
      </div>
      <div class="hero-rail">
        <div class="hero-stat">
          <span>{{ t('overview.confidence') }}</span>
          <strong>{{ dashboard.confidence }}</strong>
        </div>
        <div class="hero-stat">
          <span>{{ t('overview.mode') }}</span>
          <strong>{{ t('overview.modeValue') }}</strong>
        </div>
      </div>
    </section>

    <!-- 指标卡片网格 / Metric card grid -->
    <section class="metric-grid">
      <MetricCard v-for="metric in dashboard.metrics" :key="metric.id" :item="metric" />
    </section>

    <!-- 威胁流程图 / Threat flow diagram -->
    <ThreatFlow :stages="dashboard.flow" />

    <!-- 双列布局区域 / Two-column layout section -->
    <section class="two-column">
      <CapabilityGrid :items="dashboard.capabilities" />
      <section class="panel hot-paths">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('overview.hotPathsEyebrow') }}</p>
            <h2>{{ t('overview.hotPathsTitle') }}</h2>
          </div>
          <span class="capsule">{{ t('overview.hotPathsTag') }}</span>
        </div>

        <div class="path-list">
          <article v-for="path in dashboard.hotPaths" :key="path.path" class="path-item">
            <div class="path-top">
              <strong>{{ path.path }}</strong>
              <span class="capsule" :class="getRiskClass(path.risk)">{{ path.risk }}</span>
            </div>
            <p>{{ path.evidence }}</p>
          </article>
        </div>
      </section>
    </section>

    <!-- LLM模型网格 / LLM model mesh -->
    <ModelMesh
      :strategy="llmStack.strategy"
      :providers="llmStack.providers"
      :enablement="llmStack.enablement"
    />

    <!-- Agent运维面板 / Agent operations panel -->
    <AgentOps :blueprints="llmStack.blueprints" :runs="llmStack.runs" />

    <!-- 活动流 / Activity feed -->
    <ActivityFeed :items="dashboard.feed" />
  </div>
</template>

<script setup lang="ts">
/**
 * OverviewView 组件脚本
 * OverviewView component script
 * 
 * 管理仪表板数据和LLM堆栈状态
 * Manages dashboard data and LLM stack state
 */
import { ref, watch } from 'vue';
import ActivityFeed from '../components/ActivityFeed.vue';
import AgentOps from '../components/AgentOps.vue';
import CapabilityGrid from '../components/CapabilityGrid.vue';
import MetricCard from '../components/MetricCard.vue';
import ModelMesh from '../components/ModelMesh.vue';
import ThreatFlow from '../components/ThreatFlow.vue';
import { useI18n } from '../i18n';
import type { Locale } from '../i18n/messages';
import { fetchDashboard, fetchLlmStack } from '../services/api';
import type { DashboardData, LlmStackData } from '../types';

// 仪表板数据状态 / Dashboard data state
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

// LLM堆栈数据状态 / LLM stack data state
const llmStack = ref<LlmStackData>({
  strategy: '',
  providers: [],
  enablement: [],
  blueprints: [],
  runs: [],
});

// 国际化钩子 / i18n hook
const { locale, t } = useI18n();

/**
 * 加载概览数据
 * Load overview data
 * 
 * 并行获取仪表板和LLM堆栈数据
 * Fetches dashboard and LLM stack data in parallel
 */
async function loadOverview(selectedLocale: Locale) {
  const [dashboardData, llmStackData] = await Promise.all([
    fetchDashboard(selectedLocale),
    fetchLlmStack(selectedLocale),
  ]);

  dashboard.value = dashboardData;
  llmStack.value = llmStackData;
}

/**
 * 获取风险等级样式类
 * Get risk level style class
 * 
 * 根据风险等级返回对应的CSS类名
 * Returns corresponding CSS class based on risk level
 */
function getRiskClass(risk: string): string {
  const riskLower = risk.toLowerCase();
  if (riskLower.includes('critical') || riskLower.includes('严重')) {
    return 'risk-critical';
  }
  if (riskLower.includes('high') || riskLower.includes('高')) {
    return 'risk-high';
  }
  if (riskLower.includes('medium') || riskLower.includes('中')) {
    return 'risk-medium';
  }
  return 'risk-low';
}

// 监听语言变化并重新加载数据 / Watch locale changes and reload data
watch(
  locale,
  (selectedLocale) => {
    void loadOverview(selectedLocale);
  },
  { immediate: true },
);
</script>

<style scoped>
/*
  概览页面样式 - 商业化设计系统
  Overview page styles - Commercial design system
  
  使用CSS变量实现一致的品牌视觉
  Uses CSS variables for consistent brand visuals
*/

/* 页面容器 / Page container */
.page {
  display: grid;
  gap: 24px;
}

/* 英雄区域 / Hero section */
.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  min-height: 260px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.15), transparent 34%),
    radial-gradient(circle at right, rgba(16, 185, 129, 0.12), transparent 38%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 20px 40px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  position: relative;
  overflow: hidden;
}

/* 英雄区域装饰背景 / Hero decorative background */
.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(59, 130, 246, 0.5) 20%, 
    rgba(16, 185, 129, 0.5) 80%, 
    transparent
  );
}

/* 英雄内容区域 / Hero content area */
.hero-content {
  position: relative;
  z-index: 1;
}

/* 英雄标题 / Hero title */
.hero h1 {
  max-width: 12ch;
  margin: 10px 0 0;
  font-size: clamp(2.2rem, 6vw, 4.5rem);
  line-height: 0.94;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 英雄说明文字 / Hero description text */
.hero-copy {
  max-width: 56ch;
  margin: 20px 0 0;
  color: var(--text-secondary);
  font-size: 1.05rem;
  line-height: 1.6;
}

/* 英雄侧边栏 / Hero rail */
.hero-rail {
  display: grid;
  gap: 14px;
  min-width: 240px;
  position: relative;
  z-index: 1;
}

/* 英雄统计卡片 / Hero stat card */
.hero-stat {
  padding: 18px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

/* 英雄统计卡片悬停 / Hero stat card hover */
.hero-stat:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

/* 英雄统计标签 / Hero stat label */
.hero-stat span {
  display: block;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

/* 英雄统计数值 / Hero stat value */
.hero-stat strong {
  display: block;
  margin-top: 6px;
  font-size: 1.5rem;
  color: var(--text-primary);
}

/* 指标卡片网格 / Metric card grid */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

/* 双列布局 / Two-column layout */
.two-column {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
}

/* 热门路径面板 / Hot paths panel */
.hot-paths {
  background: 
    radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.08), transparent 40%),
    rgba(15, 23, 42, 0.95);
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

/* 路径列表 / Path list */
.path-list {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}

/* 路径项 / Path item */
.path-item {
  padding: 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

/* 路径项悬停 / Path item hover */
.path-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(59, 130, 246, 0.15);
  transform: translateX(4px);
}

/* 路径顶部区域 / Path top area */
.path-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

/* 路径名称 / Path name */
.path-top strong {
  color: var(--text-primary);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.9rem;
}

/* 路径说明 / Path description */
.path-item p {
  margin: 10px 0 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

/* 风险等级标签 - 严重 / Risk badge - Critical */
.capsule.risk-critical {
  background: rgba(244, 63, 94, 0.15);
  color: var(--color-danger);
  border: 1px solid rgba(244, 63, 94, 0.3);
}

/* 风险等级标签 - 高 / Risk badge - High */
.capsule.risk-high {
  background: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* 风险等级标签 - 中 / Risk badge - Medium */
.capsule.risk-medium {
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* 风险等级标签 - 低 / Risk badge - Low */
.capsule.risk-low {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-accent);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* 响应式设计 - 中等屏幕 / Responsive - Medium screens */
@media (max-width: 1100px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .two-column {
    grid-template-columns: 1fr;
  }
}

/* 响应式设计 - 小屏幕 / Responsive - Small screens */
@media (max-width: 760px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    min-height: auto;
    padding: 24px;
  }

  .hero-rail {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
  
  .hero h1 {
    font-size: clamp(1.8rem, 5vw, 3rem);
  }
}

/* 响应式设计 - 移动端 / Responsive - Mobile */
@media (max-width: 480px) {
  .hero-rail {
    grid-template-columns: 1fr;
  }
  
  .path-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
