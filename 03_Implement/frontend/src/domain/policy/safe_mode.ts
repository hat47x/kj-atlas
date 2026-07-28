import { fnv1aHash } from "../../utils/fnv1a_hash";

export type SafeMode = boolean;

export type SafeModeContext = "ui" | "share" | "review-pack" | "diff";
export type SafeModeEntity = "card.text" | "island.summary" | "relation.summary" | "trace.text" | "diagnostics.detail" | "markdown.copy";

const REDACTED = "[REDACTED]";

function shortHash(text: string): string {
  return `h${fnv1aHash(text)}`;
}

export const SafeModePolicy = {
  canExposeText(entity: SafeModeEntity, context: SafeModeContext, safeMode: SafeMode): boolean {
    if (!safeMode) {
      return true;
    }

    if (context === "share" || context === "review-pack") {
      return false;
    }

    if (context === "diff") {
      return entity !== "card.text" && entity !== "relation.summary" && entity !== "island.summary";
    }

    return true;
  },

  redactText(text: string, mode: SafeMode): string {
    if (!mode) {
      return text;
    }

    const length = text.trim().length;
    return `${REDACTED}${length > 0 ? ` (len:${length})` : ""}`;
  },

  summarizeForSafeMode(text: string): string {
    const trimmed = text.trim();
    if (trimmed.length === 0) {
      return REDACTED;
    }

    return `${REDACTED}:${shortHash(trimmed)}`;
  },
} as const;
