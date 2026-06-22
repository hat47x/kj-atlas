import type { Document } from "./types";
import type { HilRsDiffOp, HilRsRediffPayload } from "./hil_rs_contract";

export type HilRsApplyResult = {
  document: Document;
  appliedOpIds: string[];
  skippedOpIds: string[];
};

const REVIEW_PROTECTED_KEYS = new Set([
  "textReviewed",
  "reviewed",
  "reviewState",
  "reviewedAt",
  "reviewerRef",
  "reviewAttribution",
]);

function hasReviewProtectedField(value: unknown): boolean {
  if (Array.isArray(value)) {
    return value.some(hasReviewProtectedField);
  }
  if (typeof value !== "object" || value === null) {
    return false;
  }
  return Object.entries(value).some(
    ([key, nested]) => REVIEW_PROTECTED_KEYS.has(key) || hasReviewProtectedField(nested),
  );
}

function parseTargetRef(targetRef: string): { kind: "card" | "island"; id: string } | null {
  const [kind, id] = targetRef.split(":");
  if ((kind !== "card" && kind !== "island") || !id) return null;
  return { kind, id };
}

function cloneDocument(document: Document): Document {
  if (document.version === 1) {
    return {
      ...document,
      cards: document.cards.map((card) => ({ ...card })),
      edges: document.edges.map((edge) => ({ ...edge })),
    };
  }

  return {
    ...document,
    cards: document.cards.map((card) => ({ ...card })),
    islands: document.islands.map((island) => ({ ...island, cardIds: [...island.cardIds] })),
    edges: document.edges.map((edge) => ({ ...edge })),
  };
}

function applyCardOp(document: Document, op: HilRsDiffOp): boolean {
  const target = parseTargetRef(op.targetRef);
  if (!target || target.kind !== "card") return false;
  if (hasReviewProtectedField(op.before) || hasReviewProtectedField(op.after)) return false;
  const index = document.cards.findIndex((card) => card.id === target.id);

  if (op.opType === "add") {
    if (index !== -1 || !op.after || typeof op.after !== "object") return false;
    document.cards.push(op.after as Document["cards"][number]);
    return true;
  }

  if (op.opType === "remove") {
    if (index === -1) return false;
    document.cards.splice(index, 1);
    return true;
  }

  if (op.opType === "move") {
    if (index === -1 || !op.after || typeof op.after !== "object") return false;
    const next = op.after as Partial<Document["cards"][number]>;
    if (typeof next.x !== "number" || typeof next.y !== "number") return false;
    document.cards[index] = { ...document.cards[index], x: next.x, y: next.y };
    return true;
  }

  return false;
}

export function applyHilRsRediffPayload(document: Document, payload: HilRsRediffPayload): HilRsApplyResult {
  const next = cloneDocument(document);
  const appliedOpIds: string[] = [];
  const skippedOpIds: string[] = [];

  for (const op of payload.diffOps) {
    const applied = applyCardOp(next, op);
    if (applied) {
      appliedOpIds.push(op.opId);
    } else {
      skippedOpIds.push(op.opId);
    }
  }

  next.updatedAt = new Date().toISOString();
  return { document: next, appliedOpIds, skippedOpIds };
}
