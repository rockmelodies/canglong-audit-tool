<template>
  <div class="login-page">
    <section class="login-panel panel">
      <p class="eyebrow">{{ t('auth.eyebrow') }}</p>
      <h1>{{ t('auth.title') }}</h1>
      <p class="login-copy">{{ t('auth.description') }}</p>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label>
          <span>{{ t('auth.username') }}</span>
          <input v-model="username" type="text" autocomplete="username" />
        </label>

        <label>
          <span>{{ t('auth.password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>

        <button type="submit" :disabled="loading">
          {{ t('auth.submit') }}
        </button>
      </form>

      <p class="helper">{{ t('auth.helper') }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../auth/session';
import { useI18n } from '../i18n';

const router = useRouter();
const { locale, t } = useI18n();

const username = ref('admin');
const password = ref('Canglong123!');
const loading = ref(false);
const errorMessage = ref('');

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
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-panel {
  width: min(520px, 100%);
  background:
    radial-gradient(circle at top left, rgba(255, 122, 26, 0.2), transparent 32%),
    radial-gradient(circle at right, rgba(0, 212, 170, 0.16), transparent 36%),
    rgba(14, 20, 25, 0.9);
}

.login-panel h1 {
  margin: 10px 0 0;
  font-size: clamp(2rem, 5vw, 3.4rem);
  line-height: 1;
}

.login-copy {
  color: var(--text-dim);
}

.login-form {
  display: grid;
  gap: 16px;
  margin-top: 28px;
}

.login-form label {
  display: grid;
  gap: 8px;
}

.login-form span {
  color: var(--text-soft);
}

.login-form input {
  width: 100%;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-main);
}

.login-form button {
  margin-top: 8px;
  padding: 14px 16px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, rgba(255, 122, 26, 0.95), rgba(0, 212, 170, 0.88));
  color: #05110f;
  font-weight: 800;
  cursor: pointer;
}

.helper {
  margin-top: 20px;
  color: var(--text-dim);
}

.error {
  color: #ff9b6a;
}
</style>

