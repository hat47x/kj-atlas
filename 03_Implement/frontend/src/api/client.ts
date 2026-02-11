import type { Card, Document, DocumentV2, Island } from "../domain/types";

const API_BASE = "/api";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

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

export async function getDocument(docId: string): Promise<Document> {
  const response = await fetch(`${API_BASE}/docs/${docId}`);

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response));
  }

  return normalizeDocument((await response.json()) as Document);
}

export async function putDocument(docId: string, document: DocumentV2): Promise<DocumentV2> {
  const response = await fetch(`${API_BASE}/docs/${docId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(document),
  });

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response));
  }

  const normalizedDocument = normalizeDocument((await response.json()) as Document);

  if (normalizedDocument.version !== 2) {
    throw new ApiError(500, "Unexpected document version in update response");
  }

  return normalizedDocument;
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
