import type { DocumentV1, MergeSuggestionDecisionEntry } from "./types";
import { createRepresentativeMerge } from "./representative_merge";

export type MergeSuggestionApplyErrorCode =
  | "decision_not_adoptable"
  | "selection_not_subset"
  | "selection_too_small"
  | "source_card_missing"
  | "source_card_held"
  | "source_card_already_merged"
  | "source_card_already_canonicalized"
  | "claim_type_conflict"
  | "negate_conflict"
  | "contradiction_evidence_conflict"
  | "representative_text_empty"
  | "merge_failed";

export type MergeSuggestionApplyResult =
  | {
      ok: true;
      document: DocumentV1;
      representativeCardId: string;
      sourceCardIds: string[];
    }
  | {
      ok: false;
      code: MergeSuggestionApplyErrorCode;
    };

function normalizeIds(ids: string[]): string[] {
  return [...new Set(ids)].sort((left, right) => left.localeCompare(right));
}

function pairKey(left: string, right: string): string {
  return left <= right ? `${left}\u0000${right}` : `${right}\u0000${left}`;
}

/**
 * Materialize a previously recorded human merge decision.
 *
 * Recording accept/partial and mutating the document stay deliberately separate:
 * proposal-only means the model never applies its own suggestion, and a human can
 * record a judgement without immediately changing the graph. This function is the
 * second, explicit action. It re-checks the CURRENT document so a hold, conflict or
 * prior merge added after the decision wins over the older proposal.
 *
 * The safe first application mode does not rewire islands, edges or evidence. Source
 * cards remain in the document with all of their original fields and relationships;
 * each receives mergedIntoCardId, while the new representative carries repOf. This
 * keeps the complete source text/provenance/residual meaning available for return
 * checking instead of replacing it with the synthesized text.
 */
export function applyRecordedMergeSuggestionDecision(
  document: DocumentV1,
  decision: MergeSuggestionDecisionEntry,
): MergeSuggestionApplyResult {
  const action = decision.action ?? decision.decision;
  if (action !== "accept" && action !== "partial") {
    return { ok: false, code: "decision_not_adoptable" };
  }

  const proposalIds = normalizeIds(decision.cardIds);
  const proposalIdSet = new Set(proposalIds);
  const selectedIds = normalizeIds(
    decision.selectedCardIds && decision.selectedCardIds.length > 0
      ? decision.selectedCardIds
      : proposalIds,
  );

  if (selectedIds.some((cardId) => !proposalIdSet.has(cardId))) {
    return { ok: false, code: "selection_not_subset" };
  }
  if (selectedIds.length < 2) {
    return { ok: false, code: "selection_too_small" };
  }

  const cardsById = new Map(document.cards.map((card) => [card.id, card]));
  const sourceCards = selectedIds.map((cardId) => cardsById.get(cardId));
  if (sourceCards.some((card) => card === undefined)) {
    return { ok: false, code: "source_card_missing" };
  }

  const concreteCards = sourceCards.filter((card): card is NonNullable<typeof card> => card !== undefined);
  if (concreteCards.some((card) => card.holdState !== undefined)) {
    return { ok: false, code: "source_card_held" };
  }
  if (concreteCards.some((card) => card.mergedIntoCardId !== undefined)) {
    return { ok: false, code: "source_card_already_merged" };
  }
  if (concreteCards.some((card) => card.canonicalId !== undefined)) {
    return { ok: false, code: "source_card_already_canonicalized" };
  }

  const knownClaimTypes = new Set(
    concreteCards
      .map((card) => card.claimType)
      .filter((claimType): claimType is NonNullable<typeof claimType> => claimType !== undefined),
  );
  if (knownClaimTypes.size > 1) {
    return { ok: false, code: "claim_type_conflict" };
  }

  const selectedIdSet = new Set(selectedIds);
  const negatePairs = new Set(
    document.edges
      .filter((edge) => {
        const fromKind = edge.fromKind ?? "card";
        const toKind = edge.toKind ?? "card";
        return (
          fromKind === "card"
          && toKind === "card"
          && edge.type === "negate"
          && selectedIdSet.has(edge.fromId)
          && selectedIdSet.has(edge.toId)
        );
      })
      .map((edge) => pairKey(edge.fromId, edge.toId)),
  );
  if (negatePairs.size > 0) {
    return { ok: false, code: "negate_conflict" };
  }

  const hasContradictionEvidence = (document.evidenceLinks ?? []).some(
    (link) =>
      link.type === "contradicts"
      && selectedIdSet.has(link.fromCardId)
      && selectedIdSet.has(link.toCardId),
  );
  if (hasContradictionEvidence) {
    return { ok: false, code: "contradiction_evidence_conflict" };
  }

  const representativeText = decision.editedText.trim();
  if (!representativeText) {
    return { ok: false, code: "representative_text_empty" };
  }

  const merge = createRepresentativeMerge(document, selectedIds, representativeText, {
    // Lossless-first: source membership and relations remain attached to source
    // cards. The representative is an additional derived card, never a rewrite.
    rewireMembershipAndEdges: false,
  });
  if (!merge) {
    return { ok: false, code: "merge_failed" };
  }

  return {
    ok: true,
    representativeCardId: merge.representativeCardId,
    sourceCardIds: selectedIds,
    document: {
      ...merge.nextDocument,
      cards: merge.nextDocument.cards.map((card) =>
        card.id === merge.representativeCardId
          ? { ...card, textReviewed: true }
          : card,
      ),
    },
  };
}
