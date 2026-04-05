<template>
  <div class="shell">
    <aside class="sidebar panel">
      <div class="brand">
        <div class="brand-mark">苍</div>
        <div>
          <p class="eyebrow">CANG LONG</p>
          <h1>{{ t('shell.title') }}</h1>
        </div>
      </div>

      <nav class="nav">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <span class="nav-icon">{{ item.icon }}</span>
          <div class="nav-content">
            <span>{{ item.label }}</span>
            <small>{{ item.meta }}</small>
          </div>
        </RouterLink>
      </nav>

      <div class="language-card">
        <p class="eyebrow">{{ t('shell.languageEyebrow') }}</p>
        <h3>{{ t('shell.languageTitle') }}</h3>
        <div class="language-actions">
          <button
            v-for="option in locales"
            :key="option.code"
            type="button"
            class="language-button"
            :class="{ active: locale === option.code }"
            @click="setLocale(option.code)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <div class="sidebar-card">
        <p class="eyebrow">{{ t('shell.doctrineEyebrow') }}</p>
        <h3>{{ t('shell.doctrineTitle') }}</h3>
        <p>{{ t('shell.doctrineBody') }}</p>
      </div>

      <button type="button" class="logout-button" @click="handleLogout">
        <span class="logout-icon">🚪</span>
        {{ t('shell.logout') }}
      </button>
    </aside>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { clearSession } from '../auth/session';
import { useI18n } from '../i18n';

const router = useRouter();
const { locale, locales, setLocale, t } = useI18n();

const navItems = computed(() => [
  { to: '/projects', label: t('shell.nav.projectsLabel'), meta: t('shell.nav.projectsMeta'), icon: '📁' },
  { to: '/overview', label: t('shell.nav.overviewLabel'), meta: t('shell.nav.overviewMeta'), icon: '📊' },
  { to: '/workspace', label: t('shell.nav.workspaceLabel'), meta: t('shell.nav.workspaceMeta'), icon: '🔧' },
  { to: '/missions', label: t('shell.nav.missionsLabel'), meta: t('shell.nav.missionsMeta'), icon: '🎯' },
  { to: '/users', label: t('shell.nav.usersLabel'), meta: t('shell.nav.usersMeta'), icon: '👥' },
  { to: '/settings', label: t('shell.nav.settingsLabel'), meta: t('shell.nav.settingsMeta'), icon: '⚙️' },
]);

function handleLogout() {
  clearSession();
  void router.push('/login');
}
</script>

<style scoped>
/* ============================================
   App Shell - Commercial Design System
   应用外壳 - 商业化设计系统
   ============================================ */

/* Shell Layout / 外壳布局 */
.shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: var(--space-6);
  min-height: 100vh;
  padding: var(--space-6);
}

/* Sidebar / 侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  position: sticky;
  top: var(--space-6);
  height: calc(100vh - var(--space-6) * 2);
  overflow-y: auto;
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(12px);
}

/* Brand Section / 品牌区域 */
.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--surface-border);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--gradient-primary);
  color: white;
  font-size: var(--text-2xl);
  font-weight: 800;
  box-shadow: var(--shadow-md), var(--shadow-glow-primary);
}

.brand h1 {
  margin: var(--space-1) 0 0;
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.brand .eyebrow {
  font-size: var(--text-xs);
  color: var(--color-primary);
  letter-spacing: 0.15em;
}

/* Navigation / 导航 */
.nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  text-decoration: none;
  background: transparent;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.nav-icon {
  font-size: var(--text-xl);
  width: 32px;
  text-align: center;
  opacity: 0.8;
}

.nav-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-content span {
  font-weight: 500;
  color: var(--text-primary);
}

.nav-link small {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
}

.nav-link.router-link-active {
  background: var(--color-primary-light);
  border-color: rgba(59, 130, 246, 0.3);
}

.nav-link.router-link-active .nav-icon {
  opacity: 1;
}

.nav-link:hover:not(.router-link-active) {
  background: var(--bg-hover);
  transform: translateX(4px);
}

/* Language Card / 语言卡片 */
.language-card {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
  border: 1px solid var(--surface-border);
}

.language-card .eyebrow {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.language-card h3 {
  margin: var(--space-2) 0 0;
  font-size: var(--text-base);
  color: var(--text-primary);
}

.language-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.language-button {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--surface-border);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.language-button.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.language-button:hover:not(.active) {
  background: var(--bg-hover);
  border-color: var(--surface-border-hover);
  color: var(--text-primary);
}

/* Sidebar Card / 侧边栏卡片 */
.sidebar-card {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, transparent 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.sidebar-card .eyebrow {
  font-size: var(--text-xs);
  color: var(--color-primary);
}

.sidebar-card h3 {
  margin: var(--space-2) 0;
  font-size: var(--text-base);
  color: var(--text-primary);
}

.sidebar-card p:last-child {
  margin-bottom: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.6;
}

/* Logout Button / 登出按钮 */
.logout-button {
  margin-top: auto;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--surface-border);
  border-radius: var(--radius-lg);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  transition: all var(--transition-fast);
}

.logout-button:hover {
  background: var(--color-danger-light);
  border-color: rgba(244, 63, 94, 0.3);
  color: var(--color-danger);
}

.logout-icon {
  font-size: var(--text-lg);
}

/* Content Area / 内容区域 */
.content {
  min-width: 0;
  flex: 1;
}

/* Responsive Design / 响应式设计 */
@media (max-width: 1024px) {
  .shell {
    grid-template-columns: 1fr;
    padding: var(--space-4);
  }
  
  .sidebar {
    position: relative;
    top: 0;
    height: auto;
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--space-3);
  }
  
  .brand {
    flex: 1;
    min-width: 200px;
    border-bottom: none;
    padding-bottom: 0;
    border-right: 1px solid var(--surface-border);
    padding-right: var(--space-4);
  }
  
  .nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
  
  .nav-link {
    padding: var(--space-2) var(--space-3);
  }
  
  .nav-content small {
    display: none;
  }
  
  .language-card,
  .sidebar-card {
    flex: 1;
    min-width: 200px;
  }
  
  .logout-button {
    flex: 1;
    justify-content: center;
    margin-top: 0;
  }
}

@media (max-width: 640px) {
  .shell {
    padding: var(--space-3);
    gap: var(--space-4);
  }
  
  .sidebar {
    padding: var(--space-3);
  }
  
  .brand {
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--surface-border);
    padding-right: 0;
    padding-bottom: var(--space-3);
  }
  
  .nav {
    width: 100%;
  }
  
  .nav-link {
    flex: 1;
    justify-content: center;
  }
  
  .nav-icon {
    width: auto;
  }
  
  .nav-content {
    display: none;
  }
  
  .language-card,
  .sidebar-card {
    width: 100%;
  }
  
  .logout-button {
    width: 100%;
  }
}
</style>
