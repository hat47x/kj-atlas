import type { Card, Document, DocumentV2, Island } from "../domain/types";
import { STREAM_B_CONTRACTS } from "../domain/stream_b_contract";

const API_BASE = "/api";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export type DocumentWithEtag<TDocument extends Document> = {
  document: TDocument;
  etag?: string;
};

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      return body.detail;
    }
  } catch {
    // ignore json parse failure and fallback to status text
  }

  return response.statusText || "Request failed";
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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

export async function suggestIslandSummary(doc: DocumentV2, islandId: string): Promise<SuggestIslandSummaryResult> {
  const response = await fetch(`${API_BASE}/ai/suggest-island-summary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc, islandId }),
  });

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
    throw new ApiError(response.status, await parseErrorMessage(response));
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
