import { computed, ref } from 'vue';
import { defaultLocale, localeOptions, messages, type Locale } from './messages';

const STORAGE_KEY = 'canglong.locale';

function detectLocale(): Locale {
  if (typeof window === 'undefined') {
    return defaultLocale;
  }

  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === 'en' || saved === 'zh-CN') {
    return saved;
  }

  return navigator.language.toLowerCase().startsWith('zh') ? 'zh-CN' : defaultLocale;
}

const currentLocale = ref<Locale>(detectLocale());

function syncDocumentLang(locale: Locale) {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale;
  }
}

syncDocumentLang(currentLocale.value);

function resolveMessage(locale: Locale, key: string): string {
  const segments = key.split('.');
  let cursor: unknown = messages[locale];

  for (const segment of segments) {
    if (typeof cursor !== 'object' || cursor === null || !(segment in cursor)) {
      cursor = messages[defaultLocale];
      for (const fallbackSegment of segments) {
        if (
          typeof cursor !== 'object' ||
          cursor === null ||
          !(fallbackSegment in (cursor as Record<string, unknown>))
        ) {
          return key;
        }
        cursor = (cursor as Record<string, unknown>)[fallbackSegment];
      }
      break;
    }

    cursor = (cursor as Record<string, unknown>)[segment];
  }

  return typeof cursor === 'string' ? cursor : key;
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) {
    return template;
  }

  return template.replace(/\{(\w+)\}/g, (_, token: string) => String(params[token] ?? `{${token}}`));
}

export function setLocale(locale: Locale) {
  currentLocale.value = locale;
  syncDocumentLang(locale);

  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, locale);
  }
}

export function useI18n() {
  function t(key: string, params?: Record<string, string | number>) {
    return interpolate(resolveMessage(currentLocale.value, key), params);
  }

  return {
    locale: computed(() => currentLocale.value),
    locales: localeOptions,
    setLocale,
    t,
  };
}
