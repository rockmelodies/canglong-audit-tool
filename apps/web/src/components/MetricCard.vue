<template>
  <!--
    MetricCard - 指标卡片组件
    MetricCard - Metric card component
    
    显示单个关键指标，包含标签、数值和变化量
    Displays a single key metric with label, value, and delta
  -->
  <article class="metric-card" :class="[`tone-${item.tone}`]">
    <div class="metric-header">
      <div class="metric-icon" :class="`icon-${item.tone}`">
        <svg v-if="item.id === 'coverage'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 2a10 10 0 0 1 10 10"/>
          <path d="M12 12L12 2"/>
          <path d="M12 12L20 16"/>
        </svg>
        <svg v-else-if="item.id === 'findings'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <svg v-else-if="item.id === 'breakpoints'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4"/>
          <path d="M12 18v4"/>
          <path d="M4.93 4.93l2.83 2.83"/>
          <path d="M16.24 16.24l2.83 2.83"/>
          <path d="M2 12h4"/>
          <path d="M18 12h4"/>
          <path d="M4.93 19.07l2.83-2.83"/>
          <path d="M16.24 7.76l2.83-2.83"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M3 9h18"/>
          <path d="M9 21V9"/>
        </svg>
      </div>
      <span class="metric-label">{{ item.label }}</span>
    </div>
    
    <div class="metric-body">
      <div class="metric-value">{{ item.value }}</div>
      <div class="metric-delta" :class="{ positive: isPositiveDelta }">
        <svg v-if="isPositiveDelta" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="delta-icon">
          <path d="M18 15l-6-6-6 6"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="delta-icon">
          <circle cx="12" cy="12" r="1"/>
        </svg>
        <span>{{ item.delta }}</span>
      </div>
    </div>
    
    <div class="metric-glow" :class="`glow-${item.tone}`"></div>
  </article>
</template>

<script setup lang="ts">
/**
 * MetricCard 组件脚本
 * MetricCard component script
 * 
 * 显示关键指标的可视化卡片
 * Visual card for displaying key metrics
 */
import { computed } from 'vue';
import type { MetricCardItem } from '../types';

// Props definition / Props定义
const props = defineProps<{
  item: MetricCardItem;
}>();

// Check if delta is positive / 检查delta是否为正值
const isPositiveDelta = computed(() => {
  const delta = props.item.delta;
  return delta.startsWith('+') || delta.includes('confirmed') || delta.includes('已确认') || delta.includes('ready') || delta.includes('就绪') || delta.includes('hot') || delta.includes('热点');
});
</script>

<style scoped>
/*
  指标卡片样式 - 商业化设计系统
  Metric card styles - Commercial design system
  
  使用CSS变量和渐变实现现代化视觉效果
  Uses CSS variables and gradients for modern visual effects
*/

/* 卡片容器 / Card container */
.metric-card {
  position: relative;
  padding: 24px;
  border-radius: 20px;
  background: 
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 4px 24px -4px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  overflow: hidden;
  transition: all 0.3s ease;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 卡片悬停效果 / Card hover effect */
.metric-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 12px 32px -8px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
}

/* 卡片头部 / Card header */
.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 指标图标容器 / Metric icon container */
.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.metric-icon svg {
  width: 22px;
  height: 22px;
}

/* 图标色调变体 - 强调色 / Icon tone variant - Accent */
.icon-accent {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-accent);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

/* 图标色调变体 - 警告色 / Icon tone variant - Warning */
.icon-warning {
  background: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

/* 图标色调变体 - 中性色 / Icon tone variant - Neutral */
.icon-neutral {
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* 指标标签 / Metric label */
.metric-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

/* 卡片主体 / Card body */
.metric-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 指标数值 / Metric value */
.metric-value {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}

/* 指标变化量 / Metric delta */
.metric-delta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--text-dim);
  font-weight: 500;
}

/* 正向变化样式 / Positive delta style */
.metric-delta.positive {
  color: var(--color-accent);
}

/* 变化图标 / Delta icon */
.delta-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 发光效果 / Glow effect */
.metric-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.4;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

/* 卡片悬停时增强发光 / Enhanced glow on hover */
.metric-card:hover .metric-glow {
  opacity: 0.6;
}

/* 发光色调 - 强调色 / Glow tone - Accent */
.glow-accent {
  background: radial-gradient(circle, rgba(16, 185, 129, 0.4), transparent 70%);
}

/* 发光色调 - 警告色 / Glow tone - Warning */
.glow-warning {
  background: radial-gradient(circle, rgba(245, 158, 11, 0.4), transparent 70%);
}

/* 发光色调 - 中性色 / Glow tone - Neutral */
.glow-neutral {
  background: radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent 70%);
}

/* 色调变体 - 强调色背景 / Tone variant - Accent background */
.tone-accent {
  background: 
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 50%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95));
}

/* 色调变体 - 警告色背景 / Tone variant - Warning background */
.tone-warning {
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.12), transparent 50%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95));
}

/* 色调变体 - 中性色背景 / Tone variant - Neutral background */
.tone-neutral {
  background: 
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 50%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95));
}

/* 响应式设计 - 小屏幕 / Responsive - Small screens */
@media (max-width: 760px) {
  .metric-card {
    padding: 20px;
    min-height: 140px;
  }
  
  .metric-icon {
    width: 36px;
    height: 36px;
  }
  
  .metric-icon svg {
    width: 18px;
    height: 18px;
  }
}
</style>
