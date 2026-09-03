import type { DocumentV1, MergeSuggestionDecisionEntry } from "./types";
import { resolveRepresentativeOriginTrace } from "./merge_traceability";
import { createRepresentativeMerge } from "./representative_merge";

export type MergeSuggestionApplyErrorCode =
  | "decision_not_recorded"
  | "decision_not_accepted"
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

function sameIds(left: string[], right: string[]): boolean {
  const normalizedLeft = normalizeIds(left);
  const normalizedRight = normalizeIds(right);
  return (
    normalizedLeft.length === normalizedRight.length
    && normalizedLeft.every((id, index) => id === normalizedRight[index])
  );
}

function isSameRecordedDecision(
  recorded: MergeSuggestionDecisionEntry,
  decision: MergeSuggestionDecisionEntry,
): boolean {
  const recordedId = recorded.decisionId ?? recorded.id;
  const decisionId = decision.decisionId ?? decision.id;
  return (
    recordedId === decisionId
    && recorded.groupId === decision.groupId
    && (recorded.action ?? recorded.decision) === (decision.action ?? decision.decision)
    && recorded.editedText === decision.editedText
    && sameIds(recorded.cardIds, decision.cardIds)
  );
}

/**
 * 記録済みの人間による accept 判断を、現在のDocumentへ明示的に適用する。
 *
 * AI提案の生成、採否判断、Document変更は別の段階として保つ。この関数は
 * 「acceptを記録した後に、利用者が実適用を選んだ」第二の操作だけを担う。
 * 適用直前に現在のDocumentを再検査し、判断後に追加されたhold・矛盾・別mergeを
 * 古い提案より優先する。
 *
 * partial は現UIに採用sourceの部分集合を明示する契約がないため適用しない。
 * reject/deferも当然に適用対象外とする。
 */
export function applyRecordedMergeSuggestionDecision(
  document: DocumentV1,
  decision: MergeSuggestionDecisionEntry,
): MergeSuggestionApplyResult {
  const recordedDecision = (document.mergeSuggestionDecisions ?? []).find((entry) =>
    isSameRecordedDecision(entry, decision),
  );
  if (!recordedDecision) {
    return { ok: false, code: "decision_not_recorded" };
  }

  const action = recordedDecision.action ?? recordedDecision.decision;
  if (action !== "accept") {
    return { ok: false, code: "decision_not_accepted" };
  }

  // 現行acceptは提案全体の採用であり、selectedCardIdsは履歴互換用の複製に留まる。
  // partialの部分集合契約が定まるまでは、ここから暗黙の部分適用を導入しない。
  const selectedIds = normalizeIds(recordedDecision.cardIds);
  if (selectedIds.length < 2) {
    return { ok: false, code: "merge_failed" };
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
  const hasNegateRelation = document.edges.some((edge) => {
    const fromKind = edge.fromKind ?? "card";
    const toKind = edge.toKind ?? "card";
    return (
      fromKind === "card"
      && toKind === "card"
      && edge.type === "negate"
      && selectedIdSet.has(edge.fromId)
      && selectedIdSet.has(edge.toId)
    );
  });
  if (hasNegateRelation) {
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

  const representativeText = recordedDecision.editedText.trim();
  if (!representativeText) {
    return { ok: false, code: "representative_text_empty" };
  }

  const merge = createRepresentativeMerge(document, selectedIds, representativeText, {
    // まず最も可逆な形で適用する。元membership/relationはsourceカード側に残し、
    // 必要な代表投影は別の明示操作で追加できる。
    rewireMembershipAndEdges: false,
  });
  if (!merge) {
    return { ok: false, code: "merge_failed" };
  }

  const representativeTrace = resolveRepresentativeOriginTrace(
    merge.nextDocument,
    merge.representativeCardId,
  );
  const decisionId = recordedDecision.decisionId ?? recordedDecision.id;
  const nextDecisions = (merge.nextDocument.mergeSuggestionDecisions ?? []).map((entry) => {
    if ((entry.decisionId ?? entry.id) !== decisionId) {
      return entry;
    }
    return {
      ...entry,
      // 判断時には代表カードがまだ存在しないためfallbackだったsnapshotを、
      // 実適用で生成した代表カードと実際のsource系譜へ同期する。
      representativeCardId: merge.representativeCardId,
      representativeResolvedBy: representativeTrace.representativeResolvedBy,
      sourceCardIds: representativeTrace.sourceCardIds,
      missingSourceCardIds: representativeTrace.missingSourceCardIds,
    };
  });

  return {
    ok: true,
    representativeCardId: merge.representativeCardId,
    sourceCardIds: selectedIds,
    document: {
      ...merge.nextDocument,
      // merge採用は本文レビューの昇格とは別判断であるため、
      // createRepresentativeMerge() の textReviewed=false を維持する。
      mergeSuggestionDecisions: nextDecisions,
    },
  };
}
