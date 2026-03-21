import { computed, ref } from 'vue';
import { defaultLocale, localeOptions, messages } from './messages';
const STORAGE_KEY = 'canglong.locale';
function detectLocale() {
    if (typeof window === 'undefined') {
        return defaultLocale;
    }
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === 'en' || saved === 'zh-CN') {
        return saved;
    }
    return navigator.language.toLowerCase().startsWith('zh') ? 'zh-CN' : defaultLocale;
}
const currentLocale = ref(detectLocale());
function syncDocumentLang(locale) {
    if (typeof document !== 'undefined') {
        document.documentElement.lang = locale;
    }
}
syncDocumentLang(currentLocale.value);
function resolveMessage(locale, key) {
    const segments = key.split('.');
    let cursor = messages[locale];
    for (const segment of segments) {
        if (typeof cursor !== 'object' || cursor === null || !(segment in cursor)) {
            cursor = messages[defaultLocale];
            for (const fallbackSegment of segments) {
                if (typeof cursor !== 'object' ||
                    cursor === null ||
                    !(fallbackSegment in cursor)) {
                    return key;
                }
                cursor = cursor[fallbackSegment];
            }
            break;
        }
        cursor = cursor[segment];
    }
    return typeof cursor === 'string' ? cursor : key;
}
function interpolate(template, params) {
    if (!params) {
        return template;
    }
    return template.replace(/\{(\w+)\}/g, (_, token) => String(params[token] ?? `{${token}}`));
}
export function setLocale(locale) {
    currentLocale.value = locale;
    syncDocumentLang(locale);
    if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, locale);
    }
}
export function useI18n() {
    function t(key, params) {
        return interpolate(resolveMessage(currentLocale.value, key), params);
    }
    return {
        locale: computed(() => currentLocale.value),
        locales: localeOptions,
        setLocale,
        t,
    };
}
