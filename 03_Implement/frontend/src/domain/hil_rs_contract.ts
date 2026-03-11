export const HIL_RS_CRITIQUE_TYPES = [
  "too_close",
  "too_far",
  "not_the_same",
  "feels_off",
  "no_articulable_reason",
] as const;

export type HilRsCritiqueType = (typeof HIL_RS_CRITIQUE_TYPES)[number];

export type HilRsCritiqueInput = {
  critiqueId: string;
  targetRef: string;
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
  targetRef: string;
  before: unknown | null;
  after: unknown | null;
  rationale?: string;
};

export type HilRsRediffPayload = {
  proposalId: string;
  basedOnIteration: number;
  diffOps: HilRsDiffOp[];
  traceKey: string;
};

export const HIL_RS_REVIEW_STATES = ["unreviewed", "human_reviewed"] as const;

export type HilRsReviewState = (typeof HIL_RS_REVIEW_STATES)[number];

export type HilRsReviewAttribution = {
  reviewState: HilRsReviewState;
  reviewedAt?: string;
  reviewerRef: string;
  reviewContext?: string;
  ownerRef?: string;
};

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isIsoTimestamp(value: string): boolean {
  return Number.isFinite(Date.parse(value));
}

function hasPiiLikeIdentityFields(value: Record<string, unknown>): boolean {
  return ["provider", "external_uid", "email"].some((key) => key in value);
}

export function validateHilRsCritiqueInput(value: unknown): value is HilRsCritiqueInput {
  if (typeof value !== "object" || value === null) return false;
  const input = value as Record<string, unknown>;

  if (!isNonEmptyString(input.critiqueId)) return false;
  if (!isNonEmptyString(input.targetRef)) return false;
  if (!isNonEmptyString(input.createdAt) || !isIsoTimestamp(input.createdAt)) return false;
  if (!Number.isInteger(input.iteration) || (input.iteration as number) < 1) return false;
  if (!HIL_RS_CRITIQUE_TYPES.includes(input.critiqueType as HilRsCritiqueType)) return false;
  if (input.comment !== undefined && typeof input.comment !== "string") return false;
  if (input.constraintHints !== undefined && !Array.isArray(input.constraintHints)) return false;
  if (Array.isArray(input.constraintHints) && input.constraintHints.some((item) => typeof item !== "string")) return false;
  if (hasPiiLikeIdentityFields(input)) return false;

  return true;
}

export function validateHilRsRediffPayload(value: unknown): value is HilRsRediffPayload {
  if (typeof value !== "object" || value === null) return false;
  const payload = value as Record<string, unknown>;

  if (!isNonEmptyString(payload.proposalId)) return false;
  if (!Number.isInteger(payload.basedOnIteration) || (payload.basedOnIteration as number) < 1) return false;
  if (!isNonEmptyString(payload.traceKey)) return false;
  if (!Array.isArray(payload.diffOps) || payload.diffOps.length === 0) return false;

  for (const op of payload.diffOps) {
    if (typeof op !== "object" || op === null) return false;
    const parsed = op as Record<string, unknown>;
    if (!isNonEmptyString(parsed.opId)) return false;
    if (!HIL_RS_DIFF_OP_TYPES.includes(parsed.opType as HilRsDiffOpType)) return false;
    if (!isNonEmptyString(parsed.targetRef)) return false;
    if (!("before" in parsed) || !("after" in parsed)) return false;
    if (parsed.before === null && parsed.after === null) return false;
    if (parsed.rationale !== undefined && typeof parsed.rationale !== "string") return false;
  }

  return true;
}

export function validateHilRsReviewAttribution(value: unknown): value is HilRsReviewAttribution {
  if (typeof value !== "object" || value === null) return false;
  const attribution = value as Record<string, unknown>;

  if (!HIL_RS_REVIEW_STATES.includes(attribution.reviewState as HilRsReviewState)) return false;
  if (!isNonEmptyString(attribution.reviewerRef)) return false;
  if (attribution.reviewContext !== undefined && typeof attribution.reviewContext !== "string") return false;
  if (attribution.ownerRef !== undefined && typeof attribution.ownerRef !== "string") return false;
  if (attribution.reviewedAt !== undefined && (!isNonEmptyString(attribution.reviewedAt) || !isIsoTimestamp(attribution.reviewedAt))) {
    return false;
  }
  if (attribution.reviewState === "human_reviewed" && !isNonEmptyString(attribution.reviewedAt)) return false;
  if (attribution.reviewState === "unreviewed" && attribution.reviewedAt !== undefined) return false;
  if (hasPiiLikeIdentityFields(attribution)) return false;

  return true;
}
