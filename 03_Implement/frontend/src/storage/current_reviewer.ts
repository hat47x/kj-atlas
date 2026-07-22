import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const CURRENT_REVIEWER_STORAGE_KEY = "kj-atlas/current-reviewer-ref";

export type ReviewerRefSource = "local" | "sso" | "unknown";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function currentReviewerStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(CURRENT_REVIEWER_STORAGE_KEY, scope) : CURRENT_REVIEWER_STORAGE_KEY;
}

export function buildLocalReviewerRef(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `user:local:${crypto.randomUUID()}`;
  }

  return `user:local:${Math.random().toString(16).slice(2, 10)}`;
}

export function sanitizeReviewerRef(input: unknown): string {
  if (typeof input !== "string") {
    return "";
  }

  return input.trim();
}

export function loadCurrentReviewerRef(scope?: TenantBrowserStorageScope): string {
  if (!isStorageAvailable()) {
    return "";
  }

  return sanitizeReviewerRef(window.localStorage.getItem(currentReviewerStorageKey(scope)));
}

export function initializeCurrentReviewerRef(scope?: TenantBrowserStorageScope): string {
  const existing = loadCurrentReviewerRef(scope);
  if (existing.length > 0) {
    return existing;
  }

  const generated = buildLocalReviewerRef();
  saveCurrentReviewerRef(generated, scope);
  return generated;
}

export function saveCurrentReviewerRef(
  value: string,
  scope?: TenantBrowserStorageScope,
): string {
  const sanitized = sanitizeReviewerRef(value);
  if (isStorageAvailable()) {
    try {
      window.localStorage.setItem(currentReviewerStorageKey(scope), sanitized);
    } catch {
      // Storage may be disabled or full. The in-memory reviewer ref remains usable.
    }
  }

  return sanitized;
}


export function inferReviewerRefSource(value: string): ReviewerRefSource {
  const reviewerRef = sanitizeReviewerRef(value);
  if (reviewerRef.startsWith("user:local:")) {
    return "local";
  }
  if (reviewerRef.startsWith("user:sso:")) {
    return "sso";
  }
  return "unknown";
}
