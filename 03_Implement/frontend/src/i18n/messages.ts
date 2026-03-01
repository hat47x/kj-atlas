import en from "./locales/en.json";
import ja from "./locales/ja.json";

export const DEFAULT_LOCALE = "ja" as const;
export const SUPPORTED_LOCALES = ["ja", "en"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];
export type MessageCatalog = Record<string, string>;

export const JA_MESSAGES: MessageCatalog = ja;
export const EN_MESSAGES: MessageCatalog = en;

export const MESSAGES_BY_LOCALE: Record<Locale, MessageCatalog> = {
  ja: JA_MESSAGES,
  en: EN_MESSAGES,
};

export type MessageKey = string;
