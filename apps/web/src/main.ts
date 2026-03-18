import { createApp } from 'vue';
import App from './App.vue';
import { restoreSession } from './auth/session';
import { defaultLocale } from './i18n/messages';
import router from './router';
import './styles/base.css';

void restoreSession(defaultLocale).finally(() => {
  createApp(App).use(router).mount('#app');
});
