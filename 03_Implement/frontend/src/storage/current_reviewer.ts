const CURRENT_REVIEWER_STORAGE_KEY = "kj-atlas/current-reviewer-ref";

export type ReviewerRefSource = "local" | "sso" | "unknown";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
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

export function loadCurrentReviewerRef(): string {
  if (!isStorageAvailable()) {
    return "";
  }

  return sanitizeReviewerRef(window.localStorage.getItem(CURRENT_REVIEWER_STORAGE_KEY));
}

export function initializeCurrentReviewerRef(): string {
  const existing = loadCurrentReviewerRef();
  if (existing.length > 0) {
    return existing;
  }

  const generated = buildLocalReviewerRef();
  saveCurrentReviewerRef(generated);
  return generated;
}

export function saveCurrentReviewerRef(value: string): string {
  const sanitized = sanitizeReviewerRef(value);
  if (isStorageAvailable()) {
    window.localStorage.setItem(CURRENT_REVIEWER_STORAGE_KEY, sanitized);
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
