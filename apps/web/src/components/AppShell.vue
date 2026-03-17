<template>
  <div class="shell">
    <aside class="sidebar panel">
      <div class="brand">
        <div class="brand-mark">苍</div>
        <div>
          <p class="eyebrow">CANG LONG</p>
          <h1>Command Center</h1>
        </div>
      </div>

      <nav class="nav">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <span>{{ item.label }}</span>
          <small>{{ item.meta }}</small>
        </RouterLink>
      </nav>

      <div class="sidebar-card">
        <p class="eyebrow">Operating Doctrine</p>
        <h3>Low noise, high proof</h3>
        <p>
          Evidence-first audit flow with runtime confirmation, dockerized reenactment, and reverse-engineering lanes.
        </p>
      </div>
    </aside>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const navItems = [
  { to: '/overview', label: 'Overview', meta: 'Signal map' },
  { to: '/missions', label: 'Missions', meta: 'Audit queue' },
];
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

.sidebar-card {
  margin-top: auto;
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
}
</style>

