<template>
  <!--
    LoginView - 登录页面组件
    LoginView - Login page component
    
    提供用户认证界面，支持多语言和响应式设计
    Provides user authentication interface with i18n and responsive design support
  -->
  <div class="login-page">
    <!-- 背景装饰动画 / Background decorative animation -->
    <div class="login-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>
    
    <!-- 登录面板 / Login panel -->
    <section class="login-panel panel">
      <!-- 品牌标识区域 / Brand identity section -->
      <div class="login-header">
        <div class="brand-mark-large">苍</div>
        <p class="eyebrow">{{ t('auth.eyebrow') }}</p>
        <h1>{{ t('auth.title') }}</h1>
        <p class="login-copy">{{ t('auth.description') }}</p>
      </div>

      <!-- 登录表单 / Login form -->
      <form class="login-form" @submit.prevent="handleSubmit">
        <label>
          <span>{{ t('auth.username') }}</span>
          <input v-model="username" type="text" autocomplete="username" :placeholder="t('auth.username')" />
        </label>

        <label>
          <span>{{ t('auth.password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" :placeholder="t('auth.password')" />
        </label>

        <button type="submit" :disabled="loading" class="submit-button">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Logging in...' : t('auth.submit') }}
        </button>
      </form>

      <p class="helper">{{ t('auth.helper') }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      
      <!-- 功能特性预览 / Feature preview -->
      <div class="features-preview">
        <div class="feature-item">
          <span class="feature-icon">🔍</span>
          <span>Static Analysis</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🐳</span>
          <span>Docker Verification</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🤖</span>
          <span>AI-Powered</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * LoginView 组件脚本
 * LoginView component script
 * 
 * 处理用户登录认证逻辑
 * Handles user login authentication logic
 */
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../auth/session';
import { useI18n } from '../i18n';

// 路由实例 / Router instance
const router = useRouter();

// 国际化钩子 / i18n hook
const { locale, t } = useI18n();

// 表单数据 / Form data
const username = ref('admin');
const password = ref('Canglong123!');

// 状态管理 / State management
const loading = ref(false);
const errorMessage = ref('');

/**
 * 处理表单提交
 * Handle form submission
 * 
 * 执行用户登录并导航到概览页面
 * Performs user login and navigates to overview page
 */
async function handleSubmit() {
  loading.value = true;
  errorMessage.value = '';
  try {
    await login(username.value, password.value, locale.value);
    await router.push('/overview');
  } catch {
    errorMessage.value = t('auth.error');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
/*
  登录页面样式 - 商业化设计系统
  Login page styles - Commercial design system
  
  使用CSS变量实现一致的品牌视觉
  Uses CSS variables for consistent brand visuals
*/

/* 页面容器 / Page container */
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--bg-primary) 0%, #0c1222 50%, var(--bg-primary) 100%);
}

/* 背景装饰层 / Background decoration layer */
.login-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

/* 渐变光球基础样式 / Gradient orb base styles */
.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 20s ease-in-out infinite;
}

/* 主色光球 - 蓝色 / Primary orb - Blue */
.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent 70%);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

/* 强调色光球 - 翡翠绿 / Accent orb - Emerald */
.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.35), transparent 70%);
  bottom: -150px;
  right: -150px;
  animation-delay: -7s;
}

/* 辅助色光球 - 紫色 / Secondary orb - Purple */
.orb-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.25), transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

/* 浮动动画 / Float animation */
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

/* 登录面板 / Login panel */
.login-panel {
  width: min(560px, 100%);
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.15), transparent 32%),
    radial-gradient(circle at right, rgba(16, 185, 129, 0.12), transparent 36%),
    rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  position: relative;
  z-index: 1;
  border-radius: 24px;
  padding: 48px;
}

/* 登录头部区域 / Login header section */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

/* 大型品牌标识 / Large brand mark */
.brand-mark-large {
  display: inline-grid;
  place-items: center;
  width: 80px;
  height: 80px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: #ffffff;
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 20px;
  box-shadow: 
    0 10px 30px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 标题样式 / Title styles */
.login-panel h1 {
  margin: 10px 0 0;
  font-size: clamp(2rem, 5vw, 3.4rem);
  line-height: 1;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 眉毛文字 / Eyebrow text */
.eyebrow {
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

/* 登录说明文字 / Login description text */
.login-copy {
  color: var(--text-secondary);
  margin-top: 12px;
  font-size: 1rem;
  line-height: 1.6;
}

/* 登录表单 / Login form */
.login-form {
  display: grid;
  gap: 18px;
  margin-top: 28px;
}

/* 表单标签 / Form labels */
.login-form label {
  display: grid;
  gap: 8px;
}

/* 标签文字 / Label text */
.login-form span {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 输入框样式 / Input styles */
.login-form input {
  width: 100%;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
}

/* 输入框聚焦状态 / Input focus state */
.login-form input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 0 0 3px rgba(59, 130, 246, 0.15),
    0 0 20px rgba(59, 130, 246, 0.1);
}

/* 输入框占位符 / Input placeholder */
.login-form input::placeholder {
  color: var(--text-muted);
}

/* 提交按钮 / Submit button */
.submit-button {
  margin-top: 8px;
  padding: 16px 20px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, #2563eb 100%);
  color: #ffffff;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

/* 按钮悬停效果 / Button hover effect */
.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(59, 130, 246, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  background: linear-gradient(135deg, #4f8ff7 0%, var(--color-primary) 100%);
}

/* 按钮按下效果 / Button active effect */
.submit-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

/* 禁用状态 / Disabled state */
.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* 加载旋转器 / Loading spinner */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

/* 旋转动画 / Spin animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 帮助提示文字 / Helper text */
.helper {
  margin-top: 20px;
  color: var(--text-muted);
  text-align: center;
  font-size: 0.875rem;
}

/* 错误提示 / Error message */
.error {
  color: var(--color-danger);
  text-align: center;
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  font-size: 0.875rem;
  font-weight: 500;
}

/* 功能特性预览区域 / Features preview section */
.features-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* 功能项卡片 / Feature item card */
.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

/* 功能项悬停效果 / Feature item hover effect */
.feature-item:hover {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

/* 功能图标 / Feature icon */
.feature-icon {
  font-size: 1.5rem;
  line-height: 1;
}

/* 功能文字 / Feature text */
.feature-item span:last-child {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
  font-weight: 500;
}

/* 响应式设计 - 移动端 / Responsive design - Mobile */
@media (max-width: 600px) {
  .login-panel {
    padding: 32px 24px;
    border-radius: 20px;
  }
  
  .features-preview {
    grid-template-columns: 1fr;
  }
  
  .brand-mark-large {
    width: 64px;
    height: 64px;
    font-size: 2rem;
    border-radius: 18px;
  }
}

/* 响应式设计 - 小屏幕 / Responsive design - Small screens */
@media (max-width: 480px) {
  .login-page {
    padding: 16px;
  }
  
  .login-panel {
    padding: 24px 20px;
  }
  
  .login-form input {
    padding: 12px 14px;
  }
  
  .submit-button {
    padding: 14px 18px;
  }
}
</style>
