import { DEFAULT_LOCALE, isLocale, type Locale } from "./translate";

const LOCALE_QUERY_KEYS = ["locale", "lang", "uiLocale"] as const;

export type ResolvedViewLocaleSource = "url" | "view-metadata" | "local-storage" | "default";

export type ResolveViewLocaleInput = {
  search: string;
  metadataLocale?: string | null;
  persistedLocale?: string | null;
  isReadOnly: boolean;
};

export type ResolvedViewLocale = {
  locale: Locale;
  source: ResolvedViewLocaleSource;
  shouldPersist: boolean;
};

export function resolveLocaleFromSearch(search: string): Locale | null {
  const params = new URLSearchParams(search);
  for (const key of LOCALE_QUERY_KEYS) {
    const value = params.get(key);
    if (value && isLocale(value)) {
      return value;
    }
  }

  return null;
}

export function resolveViewLocale(input: ResolveViewLocaleInput): ResolvedViewLocale {
  const fromSearch = resolveLocaleFromSearch(input.search);
  if (fromSearch) {
    return {
      locale: fromSearch,
      source: "url",
      shouldPersist: false,
    };
  }

  if (input.metadataLocale && isLocale(input.metadataLocale)) {
    return {
      locale: input.metadataLocale,
      source: "view-metadata",
      shouldPersist: !input.isReadOnly,
    };
  }

  if (input.persistedLocale && isLocale(input.persistedLocale)) {
    return {
      locale: input.persistedLocale,
      source: "local-storage",
      shouldPersist: !input.isReadOnly,
    };
  }

  return {
    locale: DEFAULT_LOCALE,
    source: "default",
    shouldPersist: !input.isReadOnly,
  };
}
