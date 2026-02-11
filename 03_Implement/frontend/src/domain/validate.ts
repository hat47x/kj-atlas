import type { Card, DocumentV2, Island, Transform } from "./types";

type ValidateResult =
  | {
      ok: true;
      document: DocumentV2;
    }
  | {
      ok: false;
      error: string;
    };

type ImportedVersion = 1 | 2 | "v1" | "v2";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function parseTransform(value: unknown): Transform | null {
  if (!isRecord(value)) {
    return null;
  }

  const panX = toNumber(value.panX);
  const panY = toNumber(value.panY);
  const zoom = toNumber(value.zoom);

  if (panX === null || panY === null || zoom === null) {
    return null;
  }

  return { panX, panY, zoom };
}

function parseCards(value: unknown): Card[] | null {
  if (!Array.isArray(value)) {
    return null;
  }

  const cards: Card[] = [];

  for (const item of value) {
    if (!isRecord(item)) {
      return null;
    }

    const x = toNumber(item.x);
    const y = toNumber(item.y);

    if (typeof item.id !== "string" || typeof item.text !== "string" || x === null || y === null) {
      return null;
    }

    cards.push({
      id: item.id,
      text: item.text,
      x,
      y,
    });
  }

  return cards;
}


function parseEdges(value: unknown): DocumentV2["edges"] {
  if (!Array.isArray(value)) {
    return [];
  }

  const edges: DocumentV2["edges"] = [];

  for (const item of value) {
    if (!isRecord(item)) {
      continue;
    }

    if (
      typeof item.id !== "string" ||
      typeof item.fromId !== "string" ||
      typeof item.toId !== "string" ||
      (item.type !== "related" && item.type !== "negate")
    ) {
      continue;
    }

    edges.push({
      id: item.id,
      fromId: item.fromId,
      toId: item.toId,
      type: item.type,
    });
  }

  return edges;
}

function parseIslands(value: unknown): Island[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const islands: Island[] = [];

  for (const item of value) {
    if (!isRecord(item) || typeof item.id !== "string" || !Array.isArray(item.cardIds)) {
      continue;
    }

    const cardIds = item.cardIds.filter((cardId): cardId is string => typeof cardId === "string");
    islands.push({
      id: item.id,
      cardIds,
      title: typeof item.title === "string" ? item.title : undefined,
      imageUrl: typeof item.imageUrl === "string" ? item.imageUrl : undefined,
    });
  }

  return islands;
}

function normalizeVersion(value: unknown): 1 | 2 | null {
  if (value === 1 || value === "v1") {
    return 1;
  }

  if (value === 2 || value === "v2") {
    return 2;
  }

  return null;
}

function parseIsoDate(value: unknown, fallback: string): string {
  if (typeof value !== "string") {
    return fallback;
  }

  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) {
    return fallback;
  }

  return new Date(timestamp).toISOString();
}

export function validateAndUpgradeImportedDocument(value: unknown): ValidateResult {
  if (!isRecord(value)) {
    return { ok: false, error: "Imported data must be a JSON object." };
  }

  if (!("version" in value)) {
    return { ok: false, error: "Document version is required." };
  }

  const version = normalizeVersion(value.version as ImportedVersion);
  if (version === null) {
    return { ok: false, error: "Unsupported document version. Only v1 and v2 are supported." };
  }

  if (!("id" in value) || !("transform" in value) || !("cards" in value)) {
    return { ok: false, error: "Document must include id, transform, and cards." };
  }

  if (typeof value.id !== "string") {
    return { ok: false, error: "Document id must be a string." };
  }

  const transform = parseTransform(value.transform);
  if (!transform) {
    return { ok: false, error: "Document transform must include numeric panX, panY, and zoom." };
  }

  const cards = parseCards(value.cards);
  if (!cards) {
    return { ok: false, error: "Document cards must be an array of {id, text, x, y}." };
  }

  const now = new Date().toISOString();
  const createdAt = parseIsoDate(value.createdAt, now);
  const updatedAt = parseIsoDate(value.updatedAt, now);

  return {
    ok: true,
    document: {
      version: 2,
      id: value.id,
      title: typeof value.title === "string" ? value.title : undefined,
      createdAt,
      updatedAt,
      transform,
      cards,
      edges: parseEdges(value.edges),
      islands: version === 1 ? [] : parseIslands(value.islands),
    },
  };
}
