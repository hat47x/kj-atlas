import type { DocumentV2 } from "../domain/types";
import { resolveKnownEdgeType } from "../domain/types";
import { SafeModePolicy } from "../domain/policy/safe_mode";
import { canonicalizeJson } from "../domain/patch/patch_fingerprint";

// EXT-CONN-01 (ADR-0054 stage 1): the transport-independent read-only
// projection core for the external-connection layer. A future MCP server
// (stdio first, then streamable HTTP + OAuth 2.1) is a THIN adapter over
// this module -- ADR-0054 keeps the projection IR transport-independent so
// the MCP layer can be swapped without a contract change (issue AC-5).
//
// Why this lives next to agent_task_export.ts and reuses SafeModePolicy
// verbatim: the redaction boundary is the safety-bearing part. Porting it
// into a second language (e.g. the Python backend) would risk the SafeMode
// rules drifting between surfaces, silently widening exposure. The MCP
// process shares THIS module instead (monorepo import, or a later hoist to
// a shared package -- a structural follow-up, not a contract change).
//
// External read surface == the "share" SafeMode context: the content leaves
// the app boundary to an outside agent, so with SafeMode ON no card text is
// exposed (only structure/counts). Anti-scoring (ADR-0001/ADR-0049 §4.2):
// no score/rank/confidence/priority is ever emitted, in the output or the
// hashed payload.

export const CONTEXT_PROJECTION_CONSTRAINTS = [
  "reviewed-only",
  "evidence",
  "contradiction",
  "summary",
] as const;

export type ContextProjectionConstraint = (typeof CONTEXT_PROJECTION_CONSTRAINTS)[number];

export type ProjectedCard = {
  id: string;
  claimType: string | null;
  /** Exposed only when the card is reviewed AND SafeMode is OFF; otherwise a redaction placeholder. */
  text: string;
  reviewed: boolean;
  /** True when the real text was withheld (unreviewed and/or SafeMode). */
  redacted: boolean;
};

export type ProjectedRelation = { from: string; to: string; type: string };
export type ProjectedLink = { from: string; to: string };

export type ContextProjectionV1 = {
  schemaVersion: "context-projection.v1";
  docId: string;
  /** `${doc.id}:${doc.updatedAt}` -- same shape agent-task.v1 uses. */
  baseDocSignature: string;
  constraint: ContextProjectionConstraint;
  safeMode: boolean;
  cards: ProjectedCard[];
  islands: Array<{ id: string; title: string }>;
  relations: ProjectedRelation[];
  evidence: ProjectedLink[];
  contradictions: ProjectedLink[];
  counts: { reviewed: number; unreviewed: number; redacted: number };
  /** sha256 hex over the canonical-JSON projection payload (deterministic; excludes no-op fields). */
  bundleHash: string;
};

export type ContextProjectionInput = {
  doc: DocumentV2;
  constraint: ContextProjectionConstraint;
  safeMode: boolean;
};

async function sha256Hex(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(input);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

function isReviewed(card: DocumentV2["cards"][number]): boolean {
  return card.textReviewed === true;
}

/**
 * A card's real text is exposed only at the external read surface when it is
 * reviewed and SafeMode is OFF. This mirrors agent_task_export's "share"
 * boundary exactly so the two external surfaces cannot drift.
 */
function projectCardText(
  card: DocumentV2["cards"][number],
  safeMode: boolean,
): { text: string; redacted: boolean } {
  const canExpose = SafeModePolicy.canExposeText("card.text", "share", safeMode) && isReviewed(card);
  if (canExpose) {
    return { text: card.text, redacted: false };
  }
  return { text: SafeModePolicy.summarizeForSafeMode(card.text), redacted: true };
}

const byFromThenTo = (a: ProjectedLink, b: ProjectedLink): number =>
  a.from === b.from ? a.to.localeCompare(b.to) : a.from.localeCompare(b.from);

/**
 * Build a read-only, constraint-scoped, SafeMode-respecting projection of the
 * document for an external agent. Pure and deterministic given the inputs.
 */
export async function buildContextProjection(input: ContextProjectionInput): Promise<ContextProjectionV1> {
  const { doc, constraint, safeMode } = input;

  const allCards = [...doc.cards].sort((a, b) => a.id.localeCompare(b.id));
  const reviewedCount = allCards.filter(isReviewed).length;
  const unreviewedCount = allCards.length - reviewedCount;

  const evidenceLinks = doc.evidenceLinks ?? [];
  const supports = evidenceLinks
    .filter((link) => link.type === "supports")
    .map((link) => ({ from: link.fromCardId, to: link.toCardId }))
    .sort(byFromThenTo);
  const contradicts = evidenceLinks
    .filter((link) => link.type === "contradicts")
    .map((link) => ({ from: link.fromCardId, to: link.toCardId }))
    .sort(byFromThenTo);

  // Decide which cards appear as nodes for the requested constraint.
  let cardIdsInScope: Set<string>;
  if (constraint === "summary") {
    cardIdsInScope = new Set();
  } else if (constraint === "reviewed-only") {
    cardIdsInScope = new Set(allCards.filter(isReviewed).map((card) => card.id));
  } else if (constraint === "evidence") {
    cardIdsInScope = new Set(supports.flatMap((link) => [link.from, link.to]));
  } else {
    // contradiction
    cardIdsInScope = new Set(contradicts.flatMap((link) => [link.from, link.to]));
  }

  let redactedCount = 0;
  const cards: ProjectedCard[] = allCards
    .filter((card) => cardIdsInScope.has(card.id))
    .map((card) => {
      const reviewed = isReviewed(card);
      const projected = projectCardText(card, safeMode);
      if (projected.redacted) redactedCount += 1;
      return {
        id: card.id,
        claimType: card.claimType ?? null,
        text: projected.text,
        reviewed,
        redacted: projected.redacted,
      };
    });

  const islands = [...doc.islands]
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((island) => ({ id: island.id, title: island.title ?? "(無題)" }));

  // Relations are only meaningful when both endpoints are in scope. For
  // summary they are always in scope of the full doc (structure only).
  const relationScope: (id: string) => boolean =
    constraint === "summary" ? () => true : (id) => cardIdsInScope.has(id);
  const relations: ProjectedRelation[] = doc.edges
    .filter((edge) => relationScope(edge.fromId) && relationScope(edge.toId))
    .map((edge) => ({ from: edge.fromId, to: edge.toId, type: resolveKnownEdgeType(edge.type) }))
    .sort((a, b) => (a.from === b.from ? a.to.localeCompare(b.to) : a.from.localeCompare(b.from)));

  // The evidence/contradiction link lists are surfaced for the constraint
  // that asked for them (and for summary as structure).
  const evidence = constraint === "evidence" || constraint === "summary" ? supports : [];
  const contradictions = constraint === "contradiction" || constraint === "summary" ? contradicts : [];

  // Hash payload: structural only, never any numeric quality field. Card text
  // is included ONLY when it was actually exposed (redacted placeholders would
  // otherwise let a SafeMode toggle change the hash for the same real content
  // -- but exposure state IS part of what was shared, so we hash id + reviewed
  // + redacted + the exposed text, and never the withheld original).
  const hashPayload = {
    schemaVersion: "context-projection.v1",
    docId: doc.id,
    baseDocSignature: `${doc.id}:${doc.updatedAt}`,
    constraint,
    safeMode,
    cards: cards.map((card) => ({
      id: card.id,
      claimType: card.claimType,
      reviewed: card.reviewed,
      redacted: card.redacted,
      text: card.redacted ? null : card.text,
    })),
    islands,
    relations,
    evidence,
    contradictions,
    counts: { reviewed: reviewedCount, unreviewed: unreviewedCount, redacted: redactedCount },
  };
  const bundleHash = await sha256Hex(canonicalizeJson(hashPayload));

  return {
    schemaVersion: "context-projection.v1",
    docId: doc.id,
    baseDocSignature: `${doc.id}:${doc.updatedAt}`,
    constraint,
    safeMode,
    cards,
    islands,
    relations,
    evidence,
    contradictions,
    counts: { reviewed: reviewedCount, unreviewed: unreviewedCount, redacted: redactedCount },
    bundleHash,
  };
}
