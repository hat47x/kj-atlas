import type { Card, Document, DocumentV2, Island } from "../domain/types";
import { STREAM_B_CONTRACTS } from "../domain/stream_b_contract";

function resolveApiBase(): string {
  const rawValue = (import.meta.env.KJ_ATLAS_FRONTEND_API_BASE ?? "/api").trim();

  if (rawValue.length === 0) {
    return "/api";
  }

  const normalized = rawValue.endsWith("/") ? rawValue.slice(0, -1) : rawValue;
  return normalized.startsWith("/") ? normalized : "/api";
}

const API_BASE = resolveApiBase();

export class ApiError extends Error {
  readonly status: number;
  /**
   * PROV-ERROR-01: structured provider error code, mirrored from the backend's
   * ProviderError.to_contract() ("provider_unavailable" | "provider_timeout" |
   * "provider_validation"), when the failure originated from an LLM provider call.
   * Undefined for non-provider errors.
   */
  readonly code?: string;
  /**
   * Present only for ProviderDisabledError (provider=none), distinguishing an
   * intentionally-disabled provider from one that is configured but unreachable.
   */
  readonly disabledReason?: string;

  constructor(status: number, message: string, options?: { code?: string; disabledReason?: string }) {
    super(message);
    this.status = status;
    this.code = options?.code;
    this.disabledReason = options?.disabledReason;
  }
}

export type DocumentWithEtag<TDocument extends Document> = {
  document: TDocument;
  etag?: string;
};

type ParsedErrorDetail = {
  message: string;
  code?: string;
  disabledReason?: string;
};

/**
 * PROV-ERROR-01: the backend's /ai/* routes send `detail` as the full
 * ProviderError.to_contract() object (code/message/disabled_reason/...) for
 * provider failures, not a plain string. The previous `typeof detail ===
 * "string"` check silently discarded that object and fell back to
 * response.statusText, losing the distinction between "provider disabled"
 * and "provider configured but unreachable/timing out/invalid". This reads
 * both shapes: a plain string `detail` (most routes) or the structured
 * provider-error object.
 */
async function parseErrorDetail(response: Response): Promise<ParsedErrorDetail> {
  try {
    const body = await response.json();
    const detail = body?.detail;

    if (typeof detail === "string") {
      return { message: detail };
    }

    if (detail && typeof detail === "object") {
      const code = typeof detail.code === "string" ? detail.code : undefined;
      const disabledReason = typeof detail.disabled_reason === "string" ? detail.disabled_reason : undefined;
      const message = typeof detail.message === "string" ? detail.message : response.statusText || "Request failed";
      return { message, code, disabledReason };
    }
  } catch {
    // ignore json parse failure and fallback to status text
  }

  return { message: response.statusText || "Request failed" };
}

function normalizeCard(card: Card): Card {
  return {
    ...card,
    critique: typeof card.critique === "string" ? card.critique : undefined,
    textReviewed: typeof card.textReviewed === "boolean" ? card.textReviewed : undefined,
  };
}

function normalizeIsland(island: Island): Island {
  return {
    ...island,
    imageUrl: typeof island.imageUrl === "string" ? island.imageUrl : undefined,
    critique: typeof island.critique === "string" ? island.critique : undefined,
  };
}

function normalizeDocument(document: Document): Document {
  if (document.version !== 2) {
    return document;
  }

  return {
    ...document,
    cards: document.cards.map(normalizeCard),
    islands: document.islands.map(normalizeIsland),
  };
}

function normalizeEtag(rawEtag: string | null): string | undefined {
  if (!rawEtag) {
    return undefined;
  }

  let value = rawEtag.trim();
  if (value.startsWith("W/")) {
    value = value.slice(2).trim();
  }

  if (value.startsWith('"') && value.endsWith('"') && value.length >= 2) {
    return value.slice(1, -1);
  }

  return value.length > 0 ? value : undefined;
}

function formatIfMatchHeader(etag: string): string {
  return etag === "*" ? etag : `"${etag}"`;
}

async function sha256Hex(value: string): Promise<string | undefined> {
  if (!globalThis.crypto?.subtle) {
    return undefined;
  }

  const encoded = new TextEncoder().encode(value);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", encoded);
  const bytes = Array.from(new Uint8Array(digest));
  return bytes.map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function parseDocumentResponse(responseBody: string): Document {
  return JSON.parse(responseBody) as Document;
}

export async function getDocument(docId: string): Promise<DocumentWithEtag<Document>> {
  const response = await fetch(`${API_BASE}/docs/${docId}`);

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  return {
    document: normalizeDocument(parseDocumentResponse(await response.text())),
    etag: normalizeEtag(response.headers.get("ETag")),
  };
}

export async function putDocument(
  docId: string,
  document: DocumentV2,
  ifMatch?: string
): Promise<DocumentWithEtag<DocumentV2>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (ifMatch) {
    headers["If-Match"] = formatIfMatchHeader(ifMatch);
  }

  const response = await fetch(`${API_BASE}/docs/${docId}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(document),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const responseBody = await response.text();
  const normalizedDocument = normalizeDocument(parseDocumentResponse(responseBody));

  if (normalizedDocument.version !== 2) {
    throw new ApiError(500, "Unexpected document version in update response");
  }

  return {
    document: normalizedDocument,
    etag: normalizeEtag(response.headers.get("ETag")) ?? (await sha256Hex(responseBody)),
  };
}

export type ProviderKind = "none" | "local" | "large-scale";

/**
 * PROV-VIS-01 (ADR-0050 D1): read-only echo of the configured LLM provider.
 * This is a static config echo, not a connectivity check.
 */
export async function getProviderStatus(): Promise<ProviderKind> {
  const response = await fetch(`${API_BASE}/ai/provider-status`);

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as { providerKind: ProviderKind };
  return body.providerKind;
}

export type SuggestLayoutResult = {
  suggestionId: string;
  suggestedDoc: DocumentV2;
  notes?: string;
};

export async function suggestLayout(doc: DocumentV2, instruction?: string): Promise<SuggestLayoutResult> {
  const response = await fetch(`${API_BASE}/ai/suggest-layout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, instruction }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as {
    suggestionId: string;
    suggestedDoc: Document;
    notes?: string;
  };

  const suggestedDoc = normalizeDocument(body.suggestedDoc);
  if (suggestedDoc.version !== 2) {
    throw new ApiError(500, "Unexpected document version in suggestion response");
  }

  return {
    suggestionId: body.suggestionId,
    suggestedDoc,
    notes: body.notes,
  };
}


export type MergeSuggestion = {
  groupId: string;
  targetCardId: string;
  candidateCardIds: string[];
  scoreSummary: {
    min: number;
    max: number;
    avg: number;
  };
  reasonCodes: string[];
  snapshotVersion: string;
  cardIds: string[];
  mergedTextDraft: string;
  rationale?: string;
};

const CANDIDATE_GROUP_CONTRACT_VERSION = STREAM_B_CONTRACTS.candidateGroup.contractId;

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => isNonEmptyString(entry));
}

function isMergeSuggestion(value: unknown): value is MergeSuggestion {
  if (!value || typeof value !== "object") {
    return false;
  }

  const suggestion = value as Partial<MergeSuggestion>;
  const summary = suggestion.scoreSummary;
  if (!summary || typeof summary !== "object") {
    return false;
  }

  return (
    isNonEmptyString(suggestion.groupId)
    && isNonEmptyString(suggestion.targetCardId)
    && isStringArray(suggestion.candidateCardIds)
    && isFiniteNumber(summary.min)
    && isFiniteNumber(summary.max)
    && isFiniteNumber(summary.avg)
    && isStringArray(suggestion.reasonCodes)
    && suggestion.snapshotVersion === CANDIDATE_GROUP_CONTRACT_VERSION
    && isStringArray(suggestion.cardIds)
    && isNonEmptyString(suggestion.mergedTextDraft)
    && (suggestion.rationale === undefined || isNonEmptyString(suggestion.rationale))
  );
}

export async function suggestMerges(doc: DocumentV2, instruction?: string): Promise<{ suggestions: MergeSuggestion[] }> {
  const response = await fetch(`${API_BASE}/ai/suggest-merges`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, instruction }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as { suggestions?: MergeSuggestion[] };
  if (!Array.isArray(body.suggestions)) {
    throw new ApiError(500, "Invalid merge suggestions response");
  }

  if (!body.suggestions.every((suggestion) => isMergeSuggestion(suggestion))) {
    throw new ApiError(500, "Invalid merge suggestions contract payload");
  }

  return { suggestions: body.suggestions };
}


export type SuggestIslandSummaryResult = {
  summaryText: string;
  groundingIds: string[];
  warnings?: string[];
};

export type IslandSummaryProposal = {
  proposalId: string;
  type: "island_summary";
  status: "proposed";
  sourceBundleHash: string;
  diff: {
    entityType: "island_summary";
    targetId: string;
    field: "summaryText";
    before?: string;
    after: string;
    groundingIds: string[];
    warnings?: string[];
  };
  rationale: string;
};

export async function proposeIslandSummary(
  doc: DocumentV2,
  islandId: string,
  sourceBundleHash: string
): Promise<IslandSummaryProposal> {
  const response = await fetch(`${API_BASE}/ai/proposals/island-summary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, islandId, sourceBundleHash }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  return (await response.json()) as IslandSummaryProposal;
}

export async function recordProposalDecision(
  proposalId: string,
  decision: "adopt" | "reject" | "hold",
  actor: string,
  reason?: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/ai/proposals/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ proposalId, decision, actor, reason }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }
}

export async function suggestIslandSummary(doc: DocumentV2, islandId: string): Promise<SuggestIslandSummaryResult> {
  const response = await fetch(`${API_BASE}/ai/suggest-island-summary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, islandId }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as SuggestIslandSummaryResult;
  if (typeof body.summaryText !== "string" || body.summaryText.trim().length === 0) {
    throw new ApiError(500, "Invalid island summary suggestion response");
  }

  if (!Array.isArray(body.groundingIds) || body.groundingIds.length === 0 || body.groundingIds.length > 10) {
    throw new ApiError(500, "Invalid island summary grounding ids");
  }

  if (!body.groundingIds.every((id) => typeof id === "string" && id.length > 0)) {
    throw new ApiError(500, "Invalid island summary grounding ids");
  }

  if (new Set(body.groundingIds).size !== body.groundingIds.length) {
    throw new ApiError(500, "Duplicate island summary grounding ids");
  }

  if (body.warnings !== undefined && !Array.isArray(body.warnings)) {
    throw new ApiError(500, "Invalid island summary warnings");
  }

  return body;
}


export type SummarizeIslandRelationPayload = {
  doc: DocumentV2;
  islandAId: string;
  islandBId: string;
  relationType: "related" | "negate" | "unknown";
  derived: boolean;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  edgeTexts?: { edgeId: string; type: string; from: string; to: string }[];
  cardTexts: { id: string; text: string }[];
};

export type SummarizeIslandRelationResult = {
  text: string;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  warnings: string[];
};

export async function summarizeIslandRelation(
  payload: SummarizeIslandRelationPayload
): Promise<SummarizeIslandRelationResult> {
  const response = await fetch(`${API_BASE}/ai/summarize-island-relation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as SummarizeIslandRelationResult;
  if (typeof body.text !== "string" || body.text.trim().length === 0) {
    throw new ApiError(500, "Invalid relation summary text");
  }

  if (!Array.isArray(body.groundingCardIds) || !Array.isArray(body.groundingEdgeIds) || !Array.isArray(body.warnings)) {
    throw new ApiError(500, "Invalid relation summary response shape");
  }

  return body;
}

export type NarrativeIssueReference = {
  id: string;
  kind: "card" | "island";
};

export type NarrativeIssue = {
  severity: "info" | "warn" | "error";
  message: string;
  references?: NarrativeIssueReference[];
};

export async function checkNarrative(
  doc: DocumentV2,
  narrativeText: string,
  basedOnReadingOrder?: string[]
): Promise<{ issues: NarrativeIssue[] }> {
  const response = await fetch(`${API_BASE}/ai/check-narrative`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, narrativeText, basedOnReadingOrder }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as { issues?: NarrativeIssue[] };
  if (!Array.isArray(body.issues)) {
    throw new ApiError(500, "Invalid narrative consistency response");
  }

  return { issues: body.issues };
}


export type GenerateNarrativeResult = {
  text: string;
  basedOnReadingOrder: string[];
  warnings?: string[];
};

export async function generateNarrative(doc: DocumentV2, narrativeTitle?: string): Promise<GenerateNarrativeResult> {
  const response = await fetch(`${API_BASE}/ai/generate-narrative`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, narrativeTitle }),
  });

  if (!response.ok) {
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, { code: errorDetail.code, disabledReason: errorDetail.disabledReason });
  }

  const body = (await response.json()) as GenerateNarrativeResult;
  if (typeof body.text !== "string" || !Array.isArray(body.basedOnReadingOrder)) {
    throw new ApiError(500, "Invalid narrative generation response");
  }

  if (body.warnings !== undefined && !Array.isArray(body.warnings)) {
    throw new ApiError(500, "Invalid narrative generation warnings");
  }

  return body;
}
