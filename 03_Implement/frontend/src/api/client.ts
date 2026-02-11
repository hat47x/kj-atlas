import type { Document, DocumentV2, Island } from "../domain/types";

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

function normalizeIsland(island: Island): Island {
  return {
    ...island,
    imageUrl: typeof island.imageUrl === "string" ? island.imageUrl : undefined,
  };
}

function normalizeDocument(document: Document): Document {
  if (document.version !== 2) {
    return document;
  }

  return {
    ...document,
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
