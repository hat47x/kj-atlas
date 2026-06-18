import type { A1TargetRef } from "./types";

export const HIL_RS_CRITIQUE_TYPES = [
  "too_close",
  "too_far",
  "not_the_same",
  "feels_off",
  "no_articulable_reason",
] as const;

export const HIL_RS_CONTRACT_IDS = {
  critique: "A1-CRITIQUE-IF",
  rediff: "A1-REDIFF-IF",
  attribution: "A1-ATTR-IF",
  error: "A1-ERROR-IF",
} as const;

export const HIL_RS_CRITIQUE_SCHEMA_VERSION = "1.0.0" as const;
export const HIL_RS_REDIFF_SCHEMA_VERSION = "1.0.0" as const;
export const HIL_RS_REVIEW_ATTRIBUTION_SCHEMA_VERSION = "1.0.0" as const;
export const HIL_RS_ERROR_SCHEMA_VERSION = "1.0.0" as const;

export const HIL_RS_ERROR_CODES = [
  "A1_SCHEMA_VERSION_MISMATCH",
  "A1_REQUIRED_FIELD_MISSING",
  "A1_TRACE_KEY_MISSING",
  "A1_OVERRIDE_POLICY_VIOLATION",
  "A1_PII_POLICY_VIOLATION",
] as const;

export const HIL_RS_CRITIQUE_REQUIRED_FIELDS = [
  "critiqueId",
  "targetRef",
  "critiqueType",
  "createdAt",
  "iteration",
] as const;

export const HIL_RS_REVIEW_AUDIT_FIELDS = [
  "reviewState",
  "reviewedAt",
  "reviewerRef",
  "auditRecordedAt",
] as const;

export type HilRsCritiqueType = (typeof HIL_RS_CRITIQUE_TYPES)[number];

export type HilRsCritiqueInput = {
  schemaVersion: typeof HIL_RS_CRITIQUE_SCHEMA_VERSION;
  critiqueId: string;
  targetRef: A1TargetRef;
  critiqueType: HilRsCritiqueType;
  createdAt: string;
  iteration: number;
  comment?: string;
  constraintHints?: string[];
};

export const HIL_RS_DIFF_OP_TYPES = ["add", "remove", "move", "regroup", "relabel"] as const;

export type HilRsDiffOpType = (typeof HIL_RS_DIFF_OP_TYPES)[number];

export type HilRsDiffOp = {
  opId: string;
  opType: HilRsDiffOpType;
  targetRef: A1TargetRef;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  rationale?: string;
};

export type HilRsRediffPayload = {
  schemaVersion: typeof HIL_RS_REDIFF_SCHEMA_VERSION;
  proposalId: string;
  basedOnIteration: number;
  diffOps: HilRsDiffOp[];
  traceKey: string;
  rationale?: string;
};

export type HilRsErrorCode = (typeof HIL_RS_ERROR_CODES)[number];

export type HilRsContractErrorEnvelope = {
  schemaVersion: typeof HIL_RS_ERROR_SCHEMA_VERSION;
  errorCode: HilRsErrorCode;
  message: string;
  contractId: (typeof HIL_RS_CONTRACT_IDS)["critique"] | (typeof HIL_RS_CONTRACT_IDS)["rediff"] | (typeof HIL_RS_CONTRACT_IDS)["attribution"];
  retryable: boolean;
  occurredAt: string;
};

export const HIL_RS_REVIEW_STATES = ["unreviewed", "human_reviewed"] as const;

export type HilRsReviewState = (typeof HIL_RS_REVIEW_STATES)[number];

export type HilRsReviewAttribution = {
  schemaVersion: typeof HIL_RS_REVIEW_ATTRIBUTION_SCHEMA_VERSION;
  reviewState: HilRsReviewState;
  reviewedAt: string | null;
  reviewerRef: string;
  auditRecordedAt: string;
  overridePolicy: "human_dual_control_only";
  reviewContext?: string;
  ownerRef?: string;
};

const HIL_RS_CRITIQUE_ALLOWED_KEYS = new Set([
  "schemaVersion",
  "critiqueId",
  "targetRef",
  "critiqueType",
  "createdAt",
  "iteration",
  "comment",
  "constraintHints",
]);

const HIL_RS_REDIFF_ALLOWED_KEYS = new Set(["schemaVersion", "proposalId", "basedOnIteration", "diffOps", "traceKey", "rationale"]);

const HIL_RS_DIFF_OP_ALLOWED_KEYS = new Set(["opId", "opType", "targetRef", "before", "after", "rationale"]);
const HIL_RS_REVIEW_PROTECTED_KEYS = new Set([
  "textReviewed",
  "reviewed",
  "reviewState",
  "reviewedAt",
  "reviewerRef",
  "reviewAttribution",
]);

const HIL_RS_ATTRIBUTION_ALLOWED_KEYS = new Set([
  "schemaVersion",
  "reviewState",
  "reviewedAt",
  "reviewerRef",
  "auditRecordedAt",
  "overridePolicy",
  "reviewContext",
  "ownerRef",
]);

const HIL_RS_ERROR_ALLOWED_KEYS = new Set(["schemaVersion", "errorCode", "message", "contractId", "retryable", "occurredAt"]);

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isA1TargetRef(value: unknown): value is A1TargetRef {
  return (
    typeof value === "string"
    && /^(card|island|cluster|edge|proposal):[^:\s][^\s]*$/.test(value)
  );
}

function isPlainPayloadObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isIsoTimestamp(value: string): boolean {
  return Number.isFinite(Date.parse(value));
}

function hasPiiLikeIdentityFields(value: Record<string, unknown>): boolean {
  return ["provider", "external_uid", "email"].some((key) => key in value);
}

function hasPiiLikeText(value: string): boolean {
  return /@|external_uid|provider\s+user\s+id|provider_user_id/i.test(value);
}

function hasOnlyAllowedKeys(value: Record<string, unknown>, allowedKeys: ReadonlySet<string>): boolean {
  return Object.keys(value).every((key) => allowedKeys.has(key));
}

function hasReviewProtectedField(value: unknown): boolean {
  if (Array.isArray(value)) {
    return value.some(hasReviewProtectedField);
  }
  if (typeof value !== "object" || value === null) {
    return false;
  }
  return Object.entries(value).some(
    ([key, nested]) => HIL_RS_REVIEW_PROTECTED_KEYS.has(key) || hasReviewProtectedField(nested),
  );
}

export function validateHilRsCritiqueInput(value: unknown): value is HilRsCritiqueInput {
  if (typeof value !== "object" || value === null) return false;
  const input = value as Record<string, unknown>;

  if (!hasOnlyAllowedKeys(input, HIL_RS_CRITIQUE_ALLOWED_KEYS)) return false;
  if (input.schemaVersion !== HIL_RS_CRITIQUE_SCHEMA_VERSION) return false;
  if (!isNonEmptyString(input.critiqueId)) return false;
  if (!isA1TargetRef(input.targetRef)) return false;
  if (!isNonEmptyString(input.createdAt) || !isIsoTimestamp(input.createdAt)) return false;
  if (!Number.isInteger(input.iteration) || (input.iteration as number) < 1) return false;
  if (!HIL_RS_CRITIQUE_TYPES.includes(input.critiqueType as HilRsCritiqueType)) return false;
  if (input.comment !== undefined && typeof input.comment !== "string") return false;
  if (input.constraintHints !== undefined && !Array.isArray(input.constraintHints)) return false;
  if (Array.isArray(input.constraintHints) && input.constraintHints.some((item) => typeof item !== "string")) return false;
  if ("reviewed" in input || "reviewState" in input || "reviewedAt" in input || "reviewerRef" in input) return false;
  if (hasPiiLikeIdentityFields(input)) return false;

  return true;
}

export function validateHilRsRediffPayload(value: unknown): value is HilRsRediffPayload {
  if (typeof value !== "object" || value === null) return false;
  const payload = value as Record<string, unknown>;

  if (!hasOnlyAllowedKeys(payload, HIL_RS_REDIFF_ALLOWED_KEYS)) return false;
  if (payload.schemaVersion !== HIL_RS_REDIFF_SCHEMA_VERSION) return false;
  if (!isNonEmptyString(payload.proposalId)) return false;
  if (!Number.isInteger(payload.basedOnIteration) || (payload.basedOnIteration as number) < 1) return false;
  if (!isNonEmptyString(payload.traceKey)) return false;
  if (payload.rationale !== undefined && typeof payload.rationale !== "string") return false;
  if (!Array.isArray(payload.diffOps) || payload.diffOps.length === 0) return false;

  for (const op of payload.diffOps) {
    if (typeof op !== "object" || op === null) return false;
    const parsed = op as Record<string, unknown>;
    if (!hasOnlyAllowedKeys(parsed, HIL_RS_DIFF_OP_ALLOWED_KEYS)) return false;
    if (!isNonEmptyString(parsed.opId)) return false;
    if (!HIL_RS_DIFF_OP_TYPES.includes(parsed.opType as HilRsDiffOpType)) return false;
    if (!isA1TargetRef(parsed.targetRef)) return false;
    if (!("before" in parsed) || !("after" in parsed)) return false;
    if (parsed.before === null && parsed.after === null) return false;
    if (parsed.before !== null && !isPlainPayloadObject(parsed.before)) return false;
    if (parsed.after !== null && !isPlainPayloadObject(parsed.after)) return false;
    if (hasReviewProtectedField(parsed.before) || hasReviewProtectedField(parsed.after)) return false;
    if (parsed.rationale !== undefined && typeof parsed.rationale !== "string") return false;
  }

  return true;
}

export function validateHilRsContractErrorEnvelope(value: unknown): value is HilRsContractErrorEnvelope {
  if (typeof value !== "object" || value === null) return false;
  const envelope = value as Record<string, unknown>;

  if (!hasOnlyAllowedKeys(envelope, HIL_RS_ERROR_ALLOWED_KEYS)) return false;
  if (envelope.schemaVersion !== HIL_RS_ERROR_SCHEMA_VERSION) return false;
  if (!HIL_RS_ERROR_CODES.includes(envelope.errorCode as HilRsErrorCode)) return false;
  if (!isNonEmptyString(envelope.message) || hasPiiLikeText(envelope.message)) return false;
  if (
    envelope.contractId !== HIL_RS_CONTRACT_IDS.critique
    && envelope.contractId !== HIL_RS_CONTRACT_IDS.rediff
    && envelope.contractId !== HIL_RS_CONTRACT_IDS.attribution
  ) {
    return false;
  }
  if (typeof envelope.retryable !== "boolean") return false;
  if (!isNonEmptyString(envelope.occurredAt) || !isIsoTimestamp(envelope.occurredAt)) return false;

  return true;
}

export function validateHilRsReviewAttribution(value: unknown): value is HilRsReviewAttribution {
  if (typeof value !== "object" || value === null) return false;
  const attribution = value as Record<string, unknown>;

  if (!hasOnlyAllowedKeys(attribution, HIL_RS_ATTRIBUTION_ALLOWED_KEYS)) return false;
  if (attribution.schemaVersion !== HIL_RS_REVIEW_ATTRIBUTION_SCHEMA_VERSION) return false;
  if (!HIL_RS_REVIEW_STATES.includes(attribution.reviewState as HilRsReviewState)) return false;
  if (!isNonEmptyString(attribution.reviewerRef)) return false;
  if (hasPiiLikeText(attribution.reviewerRef)) return false;
  if (!isNonEmptyString(attribution.auditRecordedAt) || !isIsoTimestamp(attribution.auditRecordedAt)) return false;
  if (attribution.overridePolicy !== "human_dual_control_only") return false;
  if (attribution.reviewContext !== undefined && typeof attribution.reviewContext !== "string") return false;
  if (attribution.ownerRef !== undefined && typeof attribution.ownerRef !== "string") return false;
  if (typeof attribution.ownerRef === "string" && hasPiiLikeText(attribution.ownerRef)) return false;
  if (!(typeof attribution.reviewedAt === "string" || attribution.reviewedAt === null)) return false;
  if (typeof attribution.reviewedAt === "string" && !isIsoTimestamp(attribution.reviewedAt)) return false;
  if (attribution.reviewState === "human_reviewed" && !isNonEmptyString(attribution.reviewedAt)) return false;
  if (attribution.reviewState === "unreviewed" && attribution.reviewedAt !== null) return false;
  if (hasPiiLikeIdentityFields(attribution)) return false;

  return true;
}
