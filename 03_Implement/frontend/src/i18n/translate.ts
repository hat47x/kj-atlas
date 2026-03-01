import {
  DEFAULT_LOCALE,
  MESSAGES_BY_LOCALE,
  SUPPORTED_LOCALES,
  type Locale,
  type MessageCatalog,
  type MessageKey,
} from "./messages";

export { DEFAULT_LOCALE, type Locale } from "./messages";

type TranslateValues = Record<string, string | number>;

type LocaleValidationResult = {
  ok: boolean;
  errors: string[];
};

export function isLocale(value: string): value is Locale {
  return SUPPORTED_LOCALES.includes(value as Locale);
}

export function validateLocaleMessages(payload: unknown): LocaleValidationResult {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return { ok: false, errors: ["Locale messages must be a JSON object."] };
  }

  const errors: string[] = [];
  for (const [key, value] of Object.entries(payload)) {
    if (typeof value !== "string") {
      errors.push(`Locale message value for key "${key}" must be a string.`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export function resolveTemplateFromCatalogs(
  key: MessageKey,
  requestedLocale: Locale,
  catalogs: Record<Locale, MessageCatalog>,
): string {
  const requestedTemplate = catalogs[requestedLocale]?.[key];
  if (typeof requestedTemplate === "string") {
    return requestedTemplate;
  }

  const defaultTemplate = catalogs[DEFAULT_LOCALE]?.[key];
  if (typeof defaultTemplate === "string") {
    return defaultTemplate;
  }

  return key;
}

export function resolveTemplate(key: MessageKey, locale?: string): string {
  const requestedLocale: Locale = locale && isLocale(locale) ? locale : DEFAULT_LOCALE;
  return resolveTemplateFromCatalogs(key, requestedLocale, MESSAGES_BY_LOCALE);
}

export function t(key: MessageKey | string, values?: TranslateValues, locale?: string): string {
  const template = resolveTemplate(key, locale);
  if (!values) {
    return template;
  }

  return Object.entries(values).reduce((acc, [name, value]) => {
    return acc.split(`{${name}}`).join(String(value));
  }, template);
}
