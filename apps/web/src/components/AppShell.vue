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
          <span>{{ item.label }}</span>
          <small>{{ item.meta }}</small>
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
  { to: '/overview', label: t('shell.nav.overviewLabel'), meta: t('shell.nav.overviewMeta') },
  { to: '/workspace', label: t('shell.nav.workspaceLabel'), meta: t('shell.nav.workspaceMeta') },
  { to: '/missions', label: t('shell.nav.missionsLabel'), meta: t('shell.nav.missionsMeta') },
]);

function handleLogout() {
  clearSession();
  void router.push('/login');
}
</script>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 24px;
  min-height: 100vh;
  padding: 24px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 24px;
  height: calc(100vh - 48px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 122, 26, 0.95), rgba(0, 212, 170, 0.9));
  color: #04110f;
  font-size: 1.5rem;
  font-weight: 800;
}

.brand h1 {
  margin: 4px 0 0;
  font-size: 1.25rem;
}

.nav {
  display: grid;
  gap: 10px;
}

.nav-link {
  display: grid;
  gap: 2px;
  padding: 14px 16px;
  border-radius: 16px;
  color: var(--text-main);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  transition: 180ms ease;
}

.nav-link small {
  color: var(--text-dim);
}

.nav-link.router-link-active {
  border-color: rgba(0, 212, 170, 0.45);
  background: rgba(0, 212, 170, 0.08);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
}

.nav-link:hover {
  transform: translateY(-1px);
}

.language-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.language-card h3 {
  margin: 8px 0 0;
}

.language-actions {
  display: flex;
  gap: 10px;
  margin-top: 18px;
}

.language-button {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-main);
  cursor: pointer;
  transition: 180ms ease;
}

.language-button.active {
  border-color: rgba(0, 212, 170, 0.45);
  background: rgba(0, 212, 170, 0.12);
}

.language-button:hover {
  transform: translateY(-1px);
}

.sidebar-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 122, 26, 0.14), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-card h3 {
  margin: 8px 0;
}

.sidebar-card p:last-child {
  margin-bottom: 0;
  color: var(--text-dim);
}

.logout-button {
  margin-top: auto;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-main);
  cursor: pointer;
}

.content {
  min-width: 0;
}

@media (max-width: 980px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
  }

  .logout-button {
    margin-top: 0;
  }
}
</style>
