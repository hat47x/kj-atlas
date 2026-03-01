import { t } from "../../i18n/translate";

const READ_ONLY_KEYS = ["readonly", "readOnly", "isReadOnly"] as const;

function normalizeFlagValue(value: string | null): string {
  return (value ?? "").trim().toLowerCase();
}

function isTruthyFlag(value: string | null): boolean {
  const normalized = normalizeFlagValue(value);
  return normalized === "1" || normalized === "true" || normalized === "yes" || normalized === "on";
}

export function resolveReadOnlyFromSearch(search: string): boolean {
  const params = new URLSearchParams(search);
  for (const key of READ_ONLY_KEYS) {
    if (!params.has(key)) {
      continue;
    }

    if (isTruthyFlag(params.get(key))) {
      return true;
    }
  }

  const mode = normalizeFlagValue(params.get("mode"));
  if (mode === "readonly" || mode === "read-only") {
    return true;
  }

  return false;
}

export function buildReadOnlyBlockedMessage(actionLabel?: string): string {
  if (!actionLabel) {
    return t("read_only.blocked.generic");
  }

  return t("read_only.blocked.with_action", { actionLabel });
}
