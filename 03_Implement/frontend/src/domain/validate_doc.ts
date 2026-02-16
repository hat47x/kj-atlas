import type { DocumentV2, EdgeType, Island, Narrative, RelationSummary } from "./types";

type ValidationSuccess = {
  ok: true;
  document: DocumentV2;
};

type ValidationFailure = {
  ok: false;
  errors: string[];
};

export type ValidateDocumentV2StrictResult = ValidationSuccess | ValidationFailure;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function hasOnlyKeys(value: Record<string, unknown>, allowedKeys: string[], path: string, errors: string[]) {
  const allowed = new Set(allowedKeys);
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) {
      errors.push(`${path}: unknown field '${key}'`);
    }
  }
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function validateStringArray(value: unknown, path: string, errors: string[]): value is string[] {
  if (!Array.isArray(value)) {
    errors.push(`${path}: must be an array of strings`);
    return false;
  }

  let valid = true;
  value.forEach((item, index) => {
    if (typeof item !== "string") {
      errors.push(`${path}[${index}]: must be a string`);
      valid = false;
    }
  });

  return valid;
}

function validateEdgeType(value: unknown): value is EdgeType {
  return value === "related" || value === "negate";
}

function validateCard(item: unknown, index: number, errors: string[]): item is DocumentV2["cards"][number] {
  const path = `cards[${index}]`;
  if (!isRecord(item)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(item, ["id", "text", "x", "y", "canonicalId", "sources", "critique", "critiqueTags", "textReviewed"], path, errors);

  let valid = true;
  if (typeof item.id !== "string") {
    errors.push(`${path}.id: must be a string`);
    valid = false;
  }
  if (typeof item.text !== "string") {
    errors.push(`${path}.text: must be a string`);
    valid = false;
  }
  if (!isFiniteNumber(item.x)) {
    errors.push(`${path}.x: must be a finite number`);
    valid = false;
  }
  if (!isFiniteNumber(item.y)) {
    errors.push(`${path}.y: must be a finite number`);
    valid = false;
  }
  if (item.canonicalId !== undefined && typeof item.canonicalId !== "string") {
    errors.push(`${path}.canonicalId: must be a string when provided`);
    valid = false;
  }
  if (item.sources !== undefined && !validateStringArray(item.sources, `${path}.sources`, errors)) {
    valid = false;
  }
  if (item.critique !== undefined && typeof item.critique !== "string") {
    errors.push(`${path}.critique: must be a string when provided`);
    valid = false;
  }
  if (item.critiqueTags !== undefined && !validateStringArray(item.critiqueTags, `${path}.critiqueTags`, errors)) {
    valid = false;
  }
  if (item.textReviewed !== undefined && typeof item.textReviewed !== "boolean") {
    errors.push(`${path}.textReviewed: must be a boolean when provided`);
    valid = false;
  }

  return valid;
}

function validateEdge(item: unknown, index: number, errors: string[]): item is DocumentV2["edges"][number] {
  const path = `edges[${index}]`;
  if (!isRecord(item)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(item, ["id", "fromId", "toId", "fromKind", "toKind", "type"], path, errors);

  let valid = true;
  if (typeof item.id !== "string") {
    errors.push(`${path}.id: must be a string`);
    valid = false;
  }
  if (typeof item.fromId !== "string") {
    errors.push(`${path}.fromId: must be a string`);
    valid = false;
  }
  if (typeof item.toId !== "string") {
    errors.push(`${path}.toId: must be a string`);
    valid = false;
  }
  if (item.fromKind !== undefined && item.fromKind !== "card" && item.fromKind !== "island") {
    errors.push(`${path}.fromKind: must be 'card' or 'island' when provided`);
    valid = false;
  }
  if (item.toKind !== undefined && item.toKind !== "card" && item.toKind !== "island") {
    errors.push(`${path}.toKind: must be 'card' or 'island' when provided`);
    valid = false;
  }
  if (!validateEdgeType(item.type)) {
    errors.push(`${path}.type: must be 'related' or 'negate'`);
    valid = false;
  }

  return valid;
}

function validateIslandShape(value: unknown, path: string, errors: string[]): value is Island["shape"] {
  if (!isRecord(value)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(value, ["kind", "points", "generatedFrom"], path, errors);

  if (value.kind !== "rect" && value.kind !== "polygon") {
    errors.push(`${path}.kind: must be 'rect' or 'polygon'`);
    return false;
  }

  let valid = true;

  if (value.kind === "polygon") {
    if (!Array.isArray(value.points) || value.points.length === 0) {
      errors.push(`${path}.points: must be a non-empty array for polygon`);
      valid = false;
    } else {
      value.points.forEach((point, pointIndex) => {
        const pointPath = `${path}.points[${pointIndex}]`;
        if (!isRecord(point)) {
          errors.push(`${pointPath}: must be an object`);
          valid = false;
          return;
        }

        hasOnlyKeys(point, ["x", "y"], pointPath, errors);

        if (!isFiniteNumber(point.x)) {
          errors.push(`${pointPath}.x: must be a finite number`);
          valid = false;
        }
        if (!isFiniteNumber(point.y)) {
          errors.push(`${pointPath}.y: must be a finite number`);
          valid = false;
        }
      });
    }
  } else if (value.points !== undefined) {
    errors.push(`${path}.points: rect shape must not include points`);
    valid = false;
  }

  if (value.generatedFrom !== undefined) {
    if (!isRecord(value.generatedFrom)) {
      errors.push(`${path}.generatedFrom: must be an object`);
      valid = false;
    } else {
      hasOnlyKeys(value.generatedFrom, ["cardIds", "versionToken"], `${path}.generatedFrom`, errors);

      if (!validateStringArray(value.generatedFrom.cardIds, `${path}.generatedFrom.cardIds`, errors)) {
        valid = false;
      }
      if (typeof value.generatedFrom.versionToken !== "string") {
        errors.push(`${path}.generatedFrom.versionToken: must be a string`);
        valid = false;
      }
    }
  }

  return valid;
}

function validateIsland(item: unknown, index: number, errors: string[]): item is Island {
  const path = `islands[${index}]`;
  if (!isRecord(item)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(
    item,
    [
      "id",
      "cardIds",
      "parentIslandId",
      "collapsed",
      "title",
      "titleReviewed",
      "summaryText",
      "summaryReviewed",
      "summaryGrounding",
      "summaryHistory",
      "imageUrl",
      "imageReviewed",
      "critique",
      "critiqueTags",
      "shape",
      "shapeStale",
    ],
    path,
    errors
  );

  let valid = true;
  if (typeof item.id !== "string") {
    errors.push(`${path}.id: must be a string`);
    valid = false;
  }
  if (!validateStringArray(item.cardIds, `${path}.cardIds`, errors)) {
    valid = false;
  }
  if (item.parentIslandId !== undefined && typeof item.parentIslandId !== "string") {
    errors.push(`${path}.parentIslandId: must be a string when provided`);
    valid = false;
  }
  if (item.collapsed !== undefined && typeof item.collapsed !== "boolean") {
    errors.push(`${path}.collapsed: must be a boolean when provided`);
    valid = false;
  }
  if (item.title !== undefined && typeof item.title !== "string") {
    errors.push(`${path}.title: must be a string when provided`);
    valid = false;
  }
  if (item.titleReviewed !== undefined && typeof item.titleReviewed !== "boolean") {
    errors.push(`${path}.titleReviewed: must be a boolean when provided`);
    valid = false;
  }
  if (item.summaryText !== undefined && typeof item.summaryText !== "string") {
    errors.push(`${path}.summaryText: must be a string when provided`);
    valid = false;
  }
  if (item.summaryReviewed !== undefined && typeof item.summaryReviewed !== "boolean") {
    errors.push(`${path}.summaryReviewed: must be a boolean when provided`);
    valid = false;
  }
  if (item.summaryGrounding !== undefined && !validateStringArray(item.summaryGrounding, `${path}.summaryGrounding`, errors)) {
    valid = false;
  }
  if (item.imageUrl !== undefined && typeof item.imageUrl !== "string") {
    errors.push(`${path}.imageUrl: must be a string when provided`);
    valid = false;
  }
  if (item.imageReviewed !== undefined && typeof item.imageReviewed !== "boolean") {
    errors.push(`${path}.imageReviewed: must be a boolean when provided`);
    valid = false;
  }
  if (item.critique !== undefined && typeof item.critique !== "string") {
    errors.push(`${path}.critique: must be a string when provided`);
    valid = false;
  }
  if (item.critiqueTags !== undefined && !validateStringArray(item.critiqueTags, `${path}.critiqueTags`, errors)) {
    valid = false;
  }
  if (item.shape !== undefined && !validateIslandShape(item.shape, `${path}.shape`, errors)) {
    valid = false;
  }
  if (item.shapeStale !== undefined && typeof item.shapeStale !== "boolean") {
    errors.push(`${path}.shapeStale: must be a boolean when provided`);
    valid = false;
  }

  return valid;
}

function validateRelationSummary(item: unknown, index: number, errors: string[]): item is RelationSummary {
  const path = `relationSummaries[${index}]`;
  if (!isRecord(item)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(
    item,
    [
      "id",
      "createdAt",
      "islandAId",
      "islandBId",
      "relationType",
      "derived",
      "text",
      "reviewed",
      "groundingCardIds",
      "groundingEdgeIds",
      "warnings",
      "sourceSignature",
      "history",
    ],
    path,
    errors
  );

  let valid = true;
  if (typeof item.id !== "string") {
    errors.push(`${path}.id: must be a string`);
    valid = false;
  }
  if (typeof item.createdAt !== "string") {
    errors.push(`${path}.createdAt: must be a string`);
    valid = false;
  }
  if (typeof item.islandAId !== "string") {
    errors.push(`${path}.islandAId: must be a string`);
    valid = false;
  }
  if (typeof item.islandBId !== "string") {
    errors.push(`${path}.islandBId: must be a string`);
    valid = false;
  }
  if (item.relationType !== "related" && item.relationType !== "negate" && item.relationType !== "unknown") {
    errors.push(`${path}.relationType: must be 'related', 'negate', or 'unknown'`);
    valid = false;
  }
  if (typeof item.derived !== "boolean") {
    errors.push(`${path}.derived: must be a boolean`);
    valid = false;
  }
  if (typeof item.text !== "string") {
    errors.push(`${path}.text: must be a string`);
    valid = false;
  }
  if (typeof item.reviewed !== "boolean") {
    errors.push(`${path}.reviewed: must be a boolean`);
    valid = false;
  }
  if (!validateStringArray(item.groundingCardIds, `${path}.groundingCardIds`, errors)) {
    valid = false;
  }
  if (!validateStringArray(item.groundingEdgeIds, `${path}.groundingEdgeIds`, errors)) {
    valid = false;
  }
  if (item.warnings !== undefined && !validateStringArray(item.warnings, `${path}.warnings`, errors)) {
    valid = false;
  }
  if (typeof item.sourceSignature !== "string") {
    errors.push(`${path}.sourceSignature: must be a string`);
    valid = false;
  }

  return valid;
}

function validateNarrative(item: unknown, index: number, errors: string[]): item is Narrative {
  const path = `narratives[${index}]`;
  if (!isRecord(item)) {
    errors.push(`${path}: must be an object`);
    return false;
  }

  hasOnlyKeys(item, ["id", "title", "text", "createdAt", "basedOnReadingOrder", "reviewed", "checks"], path, errors);

  let valid = true;
  if (typeof item.id !== "string") {
    errors.push(`${path}.id: must be a string`);
    valid = false;
  }
  if (typeof item.title !== "string") {
    errors.push(`${path}.title: must be a string`);
    valid = false;
  }
  if (typeof item.text !== "string") {
    errors.push(`${path}.text: must be a string`);
    valid = false;
  }
  if (item.createdAt !== undefined && typeof item.createdAt !== "string") {
    errors.push(`${path}.createdAt: must be a string when provided`);
    valid = false;
  }
  if (item.basedOnReadingOrder !== undefined && !validateStringArray(item.basedOnReadingOrder, `${path}.basedOnReadingOrder`, errors)) {
    valid = false;
  }
  if (typeof item.reviewed !== "boolean") {
    errors.push(`${path}.reviewed: must be a boolean`);
    valid = false;
  }

  return valid;
}

export function validateDocumentV2Strict(value: unknown): ValidateDocumentV2StrictResult {
  const errors: string[] = [];

  if (!isRecord(value)) {
    return { ok: false, errors: ["document: must be a JSON object"] };
  }

  hasOnlyKeys(
    value,
    ["version", "id", "title", "createdAt", "updatedAt", "transform", "cards", "edges", "islands", "readingOrder", "narratives", "relationSummaries"],
    "document",
    errors
  );

  if (value.version !== 2) {
    errors.push("document.version: must be the number 2 (DocumentV2 only)");
  }
  if (typeof value.id !== "string") {
    errors.push("document.id: must be a string");
  }
  if (value.title !== undefined && typeof value.title !== "string") {
    errors.push("document.title: must be a string when provided");
  }
  if (typeof value.createdAt !== "string") {
    errors.push("document.createdAt: must be a string");
  }
  if (typeof value.updatedAt !== "string") {
    errors.push("document.updatedAt: must be a string");
  }

  if (!isRecord(value.transform)) {
    errors.push("document.transform: must be an object");
  } else {
    hasOnlyKeys(value.transform, ["panX", "panY", "zoom"], "document.transform", errors);
    if (!isFiniteNumber(value.transform.panX)) {
      errors.push("document.transform.panX: must be a finite number");
    }
    if (!isFiniteNumber(value.transform.panY)) {
      errors.push("document.transform.panY: must be a finite number");
    }
    if (!isFiniteNumber(value.transform.zoom)) {
      errors.push("document.transform.zoom: must be a finite number");
    }
  }

  if (!Array.isArray(value.cards)) {
    errors.push("document.cards: must be an array");
  } else {
    value.cards.forEach((item, index) => {
      validateCard(item, index, errors);
    });
  }

  if (!Array.isArray(value.edges)) {
    errors.push("document.edges: must be an array");
  } else {
    value.edges.forEach((item, index) => {
      validateEdge(item, index, errors);
    });
  }

  if (!Array.isArray(value.islands)) {
    errors.push("document.islands: must be an array");
  } else {
    value.islands.forEach((item, index) => {
      validateIsland(item, index, errors);
    });
  }

  if (value.readingOrder !== undefined && !validateStringArray(value.readingOrder, "document.readingOrder", errors)) {
    // errors are added in validateStringArray
  }

  if (value.narratives !== undefined) {
    if (!Array.isArray(value.narratives)) {
      errors.push("document.narratives: must be an array when provided");
    } else {
      value.narratives.forEach((item, index) => {
        validateNarrative(item, index, errors);
      });
    }
  }

  if (value.relationSummaries !== undefined) {
    if (!Array.isArray(value.relationSummaries)) {
      errors.push("document.relationSummaries: must be an array when provided");
    } else {
      value.relationSummaries.forEach((item, index) => {
        validateRelationSummary(item, index, errors);
      });
    }
  }

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  return { ok: true, document: value as DocumentV2 };
}
