import type { DocumentV1 } from "../domain/types";

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

export async function getDocument(docId: string): Promise<DocumentV1> {
  const response = await fetch(`${API_BASE}/docs/${docId}`);

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response));
  }

  return (await response.json()) as DocumentV1;
}

export async function putDocument(docId: string, document: DocumentV1): Promise<DocumentV1> {
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

  return (await response.json()) as DocumentV1;
}
