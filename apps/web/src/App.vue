<template>
  <AppShell v-if="showShell">
    <RouterView />
  </AppShell>
  <RouterView v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import { useSession } from './auth/session';
import AppShell from './components/AppShell.vue';

const route = useRoute();
const { isAuthenticated } = useSession();

const showShell = computed(() => isAuthenticated.value && route.path !== '/login');
</script>
