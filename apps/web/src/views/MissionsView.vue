<template>
  <!--
    MissionsView - 任务页面组件
    MissionsView - Missions page component
    
    展示审计任务列表和优先级
    Displays audit mission list and priorities
  -->
  <div class="page">
    <!-- 英雄区域 / Hero section -->
    <section class="hero panel missions-hero">
      <div class="hero-content">
        <p class="eyebrow">{{ t('missions.heroEyebrow') }}</p>
        <h1>{{ t('missions.title') }}</h1>
        <p class="hero-copy">{{ t('missions.description') }}</p>
      </div>
      <div class="hero-tags">
        <span class="capsule tag-docker">{{ t('missions.tagDocker') }}</span>
        <span class="capsule tag-decompiler">{{ t('missions.tagDecompiler') }}</span>
        <span class="capsule tag-runtime">{{ t('missions.tagRuntime') }}</span>
      </div>
    </section>

    <!-- 任务轨道 / Mission rail -->
    <MissionRail :title="t('missions.priorityTitle')" :items="missions" />
  </div>
</template>

<script setup lang="ts">
/**
 * MissionsView 组件脚本
 * MissionsView component script
 * 
 * 管理任务列表数据
 * Manages mission list data
 */
import { ref, watch } from 'vue';
import MissionRail from '../components/MissionRail.vue';
import { useI18n } from '../i18n';
import type { Locale } from '../i18n/messages';
import { fetchMissions } from '../services/api';
import type { Mission } from '../types';

// 任务列表状态 / Mission list state
const missions = ref<Mission[]>([]);

// 国际化钩子 / i18n hook
const { locale, t } = useI18n();

/**
 * 加载任务数据
 * Load mission data
 * 
 * 从API获取任务列表
 * Fetches mission list from API
 */
async function loadMissions(selectedLocale: Locale) {
  missions.value = await fetchMissions(selectedLocale);
}

// 监听语言变化并重新加载数据 / Watch locale changes and reload data
watch(
  locale,
  (selectedLocale) => {
    void loadMissions(selectedLocale);
  },
  { immediate: true },
);
</script>

<style scoped>
/*
  任务页面样式 - 商业化设计系统
  Missions page styles - Commercial design system
  
  使用CSS变量实现一致的品牌视觉
  Uses CSS variables for consistent brand visuals
*/

/* 页面容器 / Page container */
.page {
  display: grid;
  gap: 24px;
}

/* 任务英雄区域 / Missions hero section */
.missions-hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  min-height: 220px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 34%),
    radial-gradient(circle at right, rgba(16, 185, 129, 0.1), transparent 38%),
    rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 20px 40px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  position: relative;
  overflow: hidden;
}

/* 英雄区域装饰背景 / Hero decorative background */
.missions-hero::before {
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
.missions-hero h1 {
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
  max-width: 56ch;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 英雄标签区域 / Hero tags area */
.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  position: relative;
  z-index: 1;
}

/* Docker标签 / Docker tag */
.capsule.tag-docker {
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* 反编译器标签 / Decompiler tag */
.capsule.tag-decompiler {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

/* 运行时标签 / Runtime tag */
.capsule.tag-runtime {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-accent);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* 响应式设计 - 小屏幕 / Responsive - Small screens */
@media (max-width: 760px) {
  .missions-hero {
    flex-direction: column;
    align-items: flex-start;
    min-height: auto;
    padding: 24px;
  }

  .hero-tags {
    justify-content: flex-start;
    width: 100%;
  }
  
  .missions-hero h1 {
    font-size: clamp(1.8rem, 5vw, 3rem);
  }
}

/* 响应式设计 - 移动端 / Responsive - Mobile */
@media (max-width: 480px) {
  .hero-tags {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .capsule {
    width: 100%;
    text-align: center;
  }
}
</style>
