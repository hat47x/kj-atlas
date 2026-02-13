import type { Card, Document, DocumentV2, Island, Narrative } from "../domain/types";

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

function normalizeNarrative(narrative: Narrative): Narrative {
  return {
    ...narrative,
    title: typeof narrative.title === "string" ? narrative.title : undefined,
    basedOnReadingOrder: Array.isArray(narrative.basedOnReadingOrder) ? narrative.basedOnReadingOrder : [],
    reviewed: typeof narrative.reviewed === "boolean" ? narrative.reviewed : false,
    notes: typeof narrative.notes === "string" ? narrative.notes : undefined,
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
    narratives: (document.narratives ?? []).map(normalizeNarrative),
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
  cardIds: string[];
  mergedTextDraft: string;
  rationale?: string;
};

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

  return { suggestions: body.suggestions };
}
