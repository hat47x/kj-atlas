export const REVIEW_EVENT_LOG_LIMIT = 2000;

export type ReviewTargetKind = "island" | "card" | "relation" | "summary";

export type ReviewAction = "markReviewed" | "unreview";

export type ReviewEvent = {
  id: string;
  target: {
    kind: ReviewTargetKind;
    id: string;
  };
  action: ReviewAction;
  createdAt: string;
  reviewerRef?: string;
  contextLabel?: string;
};

type ReviewEventAppendInput = {
  target: ReviewEvent["target"];
  reviewed: boolean;
  createdAt?: string;
  reviewerRef?: string;
  contextLabel?: string;
};

type ReviewEventAppendOptions = {
  maxEvents?: number;
};

function isObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function sanitizeOneEvent(input: unknown): ReviewEvent | null {
  if (!isObject(input)) {
    return null;
  }

  const id = input.id;
  const target = input.target;
  const action = input.action;
  const createdAt = input.createdAt;
  if (typeof id !== "string" || id.trim().length === 0) {
    return null;
  }
  if (!isObject(target) || typeof target.id !== "string") {
    return null;
  }
  if (target.kind !== "island" && target.kind !== "card" && target.kind !== "relation" && target.kind !== "summary") {
    return null;
  }
  if (action !== "markReviewed" && action !== "unreview") {
    return null;
  }
  if (typeof createdAt !== "string") {
    return null;
  }

  return {
    id,
    target: {
      kind: target.kind,
      id: target.id,
    },
    action,
    createdAt,
    ...(typeof input.reviewerRef === "string" && input.reviewerRef.trim().length > 0 ? { reviewerRef: input.reviewerRef } : {}),
    ...(typeof input.contextLabel === "string" && input.contextLabel.trim().length > 0 ? { contextLabel: input.contextLabel } : {}),
  };
}

export function sanitizeReviewEvents(input: unknown, options?: ReviewEventAppendOptions): ReviewEvent[] {
  if (!Array.isArray(input)) {
    return [];
  }

  const maxEvents = Math.max(1, options?.maxEvents ?? REVIEW_EVENT_LOG_LIMIT);
  const sanitized = input.map((entry) => sanitizeOneEvent(entry)).filter((entry): entry is ReviewEvent => Boolean(entry));
  if (sanitized.length <= maxEvents) {
    return sanitized;
  }

  return sanitized.slice(sanitized.length - maxEvents);
}

function buildEventId(createdAt: string, target: ReviewEvent["target"], action: ReviewAction): string {
  return `review-${createdAt}-${target.kind}-${target.id}-${action}-${Math.random().toString(16).slice(2, 10)}`;
}

export function appendReviewEvent(events: ReviewEvent[], input: ReviewEventAppendInput, options?: ReviewEventAppendOptions): ReviewEvent[] {
  const createdAt = input.createdAt ?? new Date().toISOString();
  const action: ReviewAction = input.reviewed ? "markReviewed" : "unreview";
  const maxEvents = Math.max(1, options?.maxEvents ?? REVIEW_EVENT_LOG_LIMIT);
  const nextEvent: ReviewEvent = {
    id: buildEventId(createdAt, input.target, action),
    target: input.target,
    action,
    createdAt,
    ...(typeof input.reviewerRef === "string" && input.reviewerRef.trim().length > 0 ? { reviewerRef: input.reviewerRef } : {}),
    ...(typeof input.contextLabel === "string" && input.contextLabel.trim().length > 0 ? { contextLabel: input.contextLabel } : {}),
  };

  const next = [...events, nextEvent];
  if (next.length <= maxEvents) {
    return next;
  }

  return next.slice(next.length - maxEvents);
}
