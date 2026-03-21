import { computed, ref } from 'vue';
import type { Locale } from '../i18n/messages';
import type { LoginResponse, UserProfile } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:9000';
const TOKEN_KEY = 'canglong.token';
const USER_KEY = 'canglong.user';

const accessToken = ref<string | null>(typeof window === 'undefined' ? null : window.localStorage.getItem(TOKEN_KEY));
const user = ref<UserProfile | null>(
  typeof window === 'undefined' ? null : JSON.parse(window.localStorage.getItem(USER_KEY) ?? 'null'),
);

function persist() {
  if (typeof window === 'undefined') {
    return;
  }

  if (accessToken.value) {
    window.localStorage.setItem(TOKEN_KEY, accessToken.value);
  } else {
    window.localStorage.removeItem(TOKEN_KEY);
  }

  if (user.value) {
    window.localStorage.setItem(USER_KEY, JSON.stringify(user.value));
  } else {
    window.localStorage.removeItem(USER_KEY);
  }
}

export function getAccessToken() {
  return accessToken.value;
}

export function clearSession() {
  accessToken.value = null;
  user.value = null;
  persist();
}

export async function login(username: string, password: string, locale: Locale): Promise<void> {
  const response = await fetch(`${API_BASE}/api/auth/login?lang=${encodeURIComponent(locale)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  const data = (await response.json()) as LoginResponse;
  accessToken.value = data.access_token;
  user.value = data.user;
  persist();
}

export async function restoreSession(locale: Locale): Promise<void> {
  if (!accessToken.value) {
    return;
  }

  const response = await fetch(`${API_BASE}/api/auth/me?lang=${encodeURIComponent(locale)}`, {
    headers: {
      Authorization: `Bearer ${accessToken.value}`,
    },
  });

  if (!response.ok) {
    clearSession();
    return;
  }

  user.value = (await response.json()) as UserProfile;
  persist();
}

export function useSession() {
  return {
    accessToken: computed(() => accessToken.value),
    user: computed(() => user.value),
    isAuthenticated: computed(() => Boolean(accessToken.value && user.value)),
    login,
    clearSession,
    restoreSession,
  };
}
