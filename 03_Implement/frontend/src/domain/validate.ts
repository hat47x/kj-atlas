import type { Card, DeterministicTieBreak, DocumentV2, EvidenceLink, Island, Transform } from "./types";
import { canUsePolygonPoints } from "./geometry/polygon_edit";
import {
  validateHilRsCritiqueInput,
  validateHilRsRediffPayload,
  validateHilRsReviewAttribution,
} from "./hil_rs_contract";

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



function parseClaimType(value: unknown): "fact" | "claim" | "hypothesis" | "unknown" | undefined {
  if (value === "fact" || value === "claim" || value === "hypothesis" || value === "unknown") {
    return value;
  }

  return undefined;
}

function parseCritiqueTags(value: unknown): string[] | undefined {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const critiqueTags = value.filter((tag): tag is string => typeof tag === "string");
  if (critiqueTags.length === 0) {
    return undefined;
  }

  return critiqueTags;
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
      mergedIntoCardId: typeof item.mergedIntoCardId === "string" ? item.mergedIntoCardId : undefined,
      claimType: parseClaimType(item.claimType),
      repOf:
        Array.isArray(item.repOf) && item.repOf.every((cardId) => typeof cardId === "string")
          ? item.repOf
          : undefined,
      canonicalId: typeof item.canonicalId === "string" ? item.canonicalId : undefined,
      sources:
        Array.isArray(item.sources) && item.sources.every((sourceId) => typeof sourceId === "string")
          ? item.sources
          : undefined,
      critique: typeof item.critique === "string" ? item.critique : undefined,
      critiqueTags: parseCritiqueTags(item.critiqueTags),
      textReviewed: typeof item.textReviewed === "boolean" ? item.textReviewed : undefined,
      holdState:
        item.holdState === "held" || item.holdState === "pending" || item.holdState === "shelved"
          ? item.holdState
          : undefined,
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
      fromKind: item.fromKind === "island" ? "island" : "card",
      toKind: item.toKind === "island" ? "island" : "card",
      type: item.type,
    });
  }

  return edges;
}

function parseIslandGeometry(value: unknown): Island["geometry"] | undefined {
  if (!isRecord(value)) {
    return undefined;
  }

  if (value.type === "rect") {
    const x = toNumber(value.x);
    const y = toNumber(value.y);
    const w = toNumber(value.w);
    const h = toNumber(value.h);
    return {
      type: "rect",
      x: x ?? undefined,
      y: y ?? undefined,
      w: w ?? undefined,
      h: h ?? undefined,
    };
  }

  if (value.type === "polygon") {
    const rawPoints = Array.isArray(value.points)
      ? value.points
      : isRecord(value.polygon) && Array.isArray(value.polygon.points)
        ? value.polygon.points
        : [];

    const points = rawPoints
      .filter((point): point is { x: number; y: number } => isRecord(point) && toNumber(point.x) !== null && toNumber(point.y) !== null)
      .map((point) => ({ x: Number(point.x), y: Number(point.y) }));

    if (canUsePolygonPoints(points)) {
      return { type: "polygon", points };
    }
  }

  return undefined;
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
    let shape: Island["shape"] | undefined;
    const geometry = parseIslandGeometry(item.geometry);
    if (isRecord(item.shape)) {
      const kind = item.shape.kind;
      let generatedFrom: { cardIds: string[]; versionToken: string } | undefined;

      if (isRecord(item.shape.generatedFrom) && Array.isArray(item.shape.generatedFrom.cardIds)) {
        const generatedFromCardIds = item.shape.generatedFrom.cardIds.filter(
          (cardId): cardId is string => typeof cardId === "string"
        );

        if (typeof item.shape.generatedFrom.versionToken === "string") {
          generatedFrom = {
            cardIds: generatedFromCardIds,
            versionToken: item.shape.generatedFrom.versionToken,
          };
        }
      }

      if (kind === "rect") {
        shape = { kind: "rect", generatedFrom };
      } else if (kind === "polygon" && Array.isArray(item.shape.points)) {
        const points = item.shape.points
          .filter((point): point is { x: number; y: number } => {
            return isRecord(point) && toNumber(point.x) !== null && toNumber(point.y) !== null;
          })
          .map((point) => ({ x: Number(point.x), y: Number(point.y) }));

        if (canUsePolygonPoints(points)) {
          shape = { kind: "polygon", points, generatedFrom };
        }
      }
    }

    if (!shape && geometry?.type === "polygon") {
      shape = {
        kind: "polygon",
        points: geometry.points,
      };
    }

    if (!shape && geometry?.type === "rect") {
      shape = { kind: "rect" };
    }

    if (!shape && !geometry) {
      shape = { kind: "rect" };
    }

    const normalizedGeometry = geometry
      ?? (shape?.kind === "polygon"
        ? { type: "polygon", points: shape.points }
        : shape?.kind === "rect"
          ? { type: "rect" }
          : undefined);
    islands.push({
      id: item.id,
      cardIds,
      parentIslandId: typeof item.parentIslandId === "string" ? item.parentIslandId : undefined,
      placardCardId: typeof item.placardCardId === "string" ? item.placardCardId : undefined,
      collapsed: typeof item.collapsed === "boolean" ? item.collapsed : false,
      title: typeof item.title === "string" ? item.title : undefined,
      imageUrl: typeof item.imageUrl === "string" ? item.imageUrl : undefined,
      critique: typeof item.critique === "string" ? item.critique : undefined,
      critiqueTags: parseCritiqueTags(item.critiqueTags),
      geometry: normalizedGeometry,
      shape,
      shapeStale: typeof item.shapeStale === "boolean" ? item.shapeStale : undefined,
    });
  }

  const islandsById = new Map(islands.map((island) => [island.id, island]));

  const resolveParentIslandId = (islandId: string, parentIslandId: string | undefined): string | undefined => {
    if (!parentIslandId) {
      return undefined;
    }

    const visited = new Set<string>([islandId]);
    let cursor: string | undefined = parentIslandId;

    while (cursor) {
      if (visited.has(cursor)) {
        return undefined;
      }

      const parent = islandsById.get(cursor);
      if (!parent) {
        return undefined;
      }

      visited.add(cursor);
      cursor = parent.parentIslandId;
    }

    return parentIslandId;
  };

  return islands.map((island) => {
    const parentIslandId = resolveParentIslandId(island.id, island.parentIslandId);
    if (parentIslandId === island.parentIslandId) {
      return island;
    }

    return {
      ...island,
      parentIslandId,
    };
  });
}


function parseEvidenceLinks(value: unknown): EvidenceLink[] | undefined {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const evidenceLinks: EvidenceLink[] = [];
  const seenIds = new Set<string>();
  const seenKeys = new Set<string>();

  for (const item of value) {
    if (!isRecord(item)) {
      continue;
    }

    if (typeof item.id !== "string" || typeof item.fromCardId !== "string" || typeof item.toCardId !== "string") {
      continue;
    }

    if (item.type !== "supports" && item.type !== "contradicts") {
      continue;
    }

    if (item.fromCardId === item.toCardId || seenIds.has(item.id)) {
      continue;
    }

    const duplicateKey = `${item.fromCardId}:${item.toCardId}:${item.type}`;
    if (seenKeys.has(duplicateKey)) {
      continue;
    }

    seenIds.add(item.id);
    seenKeys.add(duplicateKey);
    evidenceLinks.push({
      id: item.id,
      type: item.type,
      fromCardId: item.fromCardId,
      toCardId: item.toCardId,
      note: typeof item.note === "string" ? item.note : undefined,
      createdAt: typeof item.createdAt === "string" ? item.createdAt : undefined,
    });
  }

  return evidenceLinks;
}

function parseCritiqueInputs(value: unknown): DocumentV2["critiqueInputs"] | undefined {
  if (!Array.isArray(value)) {
    return undefined;
  }

  return value.filter(validateHilRsCritiqueInput);
}

function parseReproposalDiffs(value: unknown): DocumentV2["reproposalDiffs"] | undefined {
  if (!Array.isArray(value)) {
    return undefined;
  }

  return value.filter(validateHilRsRediffPayload);
}

function parseReviewAttribution(value: unknown): DocumentV2["reviewAttribution"] | undefined {
  return validateHilRsReviewAttribution(value) ? value : undefined;
}

function parseDeterministicTieBreak(value: unknown): DeterministicTieBreak | undefined {
  if (!isRecord(value)) {
    return undefined;
  }

  const expectedOrder: DeterministicTieBreak["order"] = [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
  ];
  const order = value.order;
  if (
    value.schemaVersion !== "1.0.0"
    || !Array.isArray(order)
    || expectedOrder.some((entry, index) => order[index] !== entry)
  ) {
    return undefined;
  }

  return {
    schemaVersion: "1.0.0",
    order: expectedOrder,
  };
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
  const critiqueInputs = parseCritiqueInputs(value.critiqueInputs);
  const reproposalDiffs = parseReproposalDiffs(value.reproposalDiffs);
  const reviewAttribution = parseReviewAttribution(value.reviewAttribution);
  const deterministicTieBreak = parseDeterministicTieBreak(value.deterministicTieBreak);

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
      evidenceLinks: parseEvidenceLinks(value.evidenceLinks) ?? [],
      ...(critiqueInputs !== undefined ? { critiqueInputs } : {}),
      ...(reproposalDiffs !== undefined ? { reproposalDiffs } : {}),
      ...(reviewAttribution !== undefined ? { reviewAttribution } : {}),
      ...(deterministicTieBreak !== undefined ? { deterministicTieBreak } : {}),
    },
  };
}
