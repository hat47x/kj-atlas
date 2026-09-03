import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";
import { createRepresentativeMerge } from "./representative_merge";
import type { DocumentV1 } from "./types";

export type MergeSuggestionForDecision = {
  groupId: string;
  cardIds: string[];
  mergedTextDraft: string;
  editedText: string;
  rationale?: string;
};

export type ApplyMergeSuggestionDecisionResult =
  | {
      ok: true;
      nextDocument: DocumentV1;
      appliedRepresentativeCardId?: string;
    }
  | {
      ok: false;
      reason: "merge_not_applicable";
    };

/**
 * Apply one trusted human decision to a merge suggestion without introducing a
 * second source of merge semantics.
 *
 * `accept` is the only decision that mutates the card graph: it first creates
 * the representative card with `createRepresentativeMerge()`, then records the
 * decision against that post-merge document. This ordering makes the decision
 * snapshot point at the representative that was actually created. Both steps
 * are pure document transformations, so a failed merge leaves no accepted
 * decision behind.
 *
 * `partial` deliberately remains decision-only. The current UI does not define
 * which subset of `cardIds` was accepted, so applying an arbitrary subset would
 * manufacture a human decision that was never made. `reject` and `defer` are
 * also record-only by definition.
 *
 * AI acceptance does not automatically rewire island membership or relations.
 * Accepting the merged wording is a narrower human decision than accepting a
 * topology rewrite. The manual representative-card flow remains the explicit
 * place for that additional structural choice.
 */
export function applyMergeSuggestionHumanDecision(
  document: DocumentV1,
  suggestion: MergeSuggestionForDecision,
  decision: MergeSuggestionDecision,
  input: {
    decisionReason?: string;
  },
  options?: {
    decisionIdFactory?: () => string;
    now?: string;
  }
): ApplyMergeSuggestionDecisionResult {
  let decisionDocument = document;
  let appliedRepresentativeCardId: string | undefined;

  if (decision === "accept") {
    const merge = createRepresentativeMerge(
      document,
      suggestion.cardIds,
      suggestion.editedText,
      { rewireMembershipAndEdges: false }
    );
    if (!merge) {
      return { ok: false, reason: "merge_not_applicable" };
    }
    decisionDocument = merge.nextDocument;
    appliedRepresentativeCardId = merge.representativeCardId;
  }

  const nextDocument = appendMergeSuggestionDecision(
    decisionDocument,
    {
      groupId: suggestion.groupId,
      decision,
      cardIds: suggestion.cardIds,
      mergedTextDraft: suggestion.mergedTextDraft,
      editedText: suggestion.editedText,
      rationale: suggestion.rationale,
      decisionReason: input.decisionReason,
    },
    {
      idFactory: options?.decisionIdFactory,
      now: options?.now,
    }
  );

  return {
    ok: true,
    nextDocument,
    ...(appliedRepresentativeCardId ? { appliedRepresentativeCardId } : {}),
  };
}
