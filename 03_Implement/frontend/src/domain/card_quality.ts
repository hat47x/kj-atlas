import type { Card } from "./types";

// 6 representative fixture kinds, per qualitative_card_quality_requirements.md §7.
export const CARD_QUALITY_FIXTURE_KINDS = [
  "single_center",
  "multi_center",
  "context_poor",
  "quote_interpretation_mixed",
  "minority_or_contradiction",
  "unknown_source",
] as const;
export type CardQualityFixtureKind = (typeof CARD_QUALITY_FIXTURE_KINDS)[number];

// Fixed order per §4.2: "中心的内容、文脈、出典、観察と解釈の順に確認できる".
// This order never changes per-card — Phase B is AI-less self-check, not
// content-driven detection, so there is nothing here that could flag a
// minority/contradiction fixture as needing extra scrutiny (CQ-DIVERSE-01).
export const CARD_QUALITY_QUESTION_KINDS = ["unit", "context", "trace", "status"] as const;
export type CardQualityQuestionKind = (typeof CARD_QUALITY_QUESTION_KINDS)[number];

// No score/rank/pass-fail value exists by construction (CQ-DIVERSE-01, §5).
// "apply" only means "go fix this" (e.g. open the split/edit affordance) —
// this module never mutates Card itself; that stays a manual, T5-level action.
export const CARD_QUALITY_DECISIONS = ["apply", "keep_as_is", "hold_for_now"] as const;
export type CardQualityDecision = (typeof CARD_QUALITY_DECISIONS)[number];

export type CardQualityQuestion = {
  kind: CardQualityQuestionKind;
  // i18n keys, not literal copy — actual bilingual strings land with the
  // Phase B UI (T5); §4.2 requires one concrete "why it helps" sentence
  // per question, not evaluative language ("low quality" etc.).
  promptKey: string;
  rationaleKey: string;
};

const QUESTION_ORDER: readonly CardQualityQuestion[] = CARD_QUALITY_QUESTION_KINDS.map((kind) => ({
  kind,
  promptKey: `cardQuality.question.${kind}.prompt`,
  rationaleKey: `cardQuality.question.${kind}.rationale`,
}));

export type CardQualityAssistState = {
  cardId: string;
  textAtOpen: string;
  originalText?: string;
  queue: readonly CardQualityQuestionKind[];
  currentIndex: number;
  decisions: Partial<Record<CardQualityQuestionKind, CardQualityDecision>>;
  resolved: boolean;
};

/**
 * Opens (or reopens) the quality-assist flow for a card. Only `id`/`text` are
 * read — no other Card field is inspected or required, keeping this usable
 * standalone from KJ_ATLAS_LLM_PROVIDER=none through Phase C.
 *
 * QUX-HUMAN-01: a question the user answered "keep_as_is" is not re-surfaced
 * in the same editing session unless the card text changed since.
 */
export function openCardQualityAssist(
  card: Pick<Card, "id" | "text">,
  priorState?: CardQualityAssistState
): CardQualityAssistState {
  const sameCard = priorState !== undefined && priorState.cardId === card.id;
  const textChanged = sameCard && priorState.textAtOpen !== card.text;
  const carriedDecisions = sameCard && !textChanged ? priorState.decisions : {};
  const queue = CARD_QUALITY_QUESTION_KINDS.filter((kind) => carriedDecisions[kind] !== "keep_as_is");

  return {
    cardId: card.id,
    textAtOpen: card.text,
    originalText:
      sameCard && priorState?.originalText !== card.text
        ? priorState?.originalText
        : undefined,
    queue,
    currentIndex: 0,
    decisions: { ...carriedDecisions },
    resolved: queue.length === 0,
  };
}

export function beginCardQualityRewrite(
  state: CardQualityAssistState,
  currentText: string
): CardQualityAssistState {
  if (state.originalText !== undefined) {
    return state;
  }

  return {
    ...state,
    originalText: currentText,
  };
}

export function cardQualityRestoreTarget(state: CardQualityAssistState): string | undefined {
  return state.originalText;
}

export function currentCardQualityQuestion(state: CardQualityAssistState): CardQualityQuestion | undefined {
  if (state.resolved || state.currentIndex >= state.queue.length) {
    return undefined;
  }
  const kind = state.queue[state.currentIndex];
  return QUESTION_ORDER.find((question) => question.kind === kind);
}

/**
 * Pure state transition: records the decision for the current question and
 * advances the queue. Takes and returns only assist state — it has no way to
 * read or write Card content, so "card unchanged before adoption" (CQ-REV-01,
 * AC-5) holds structurally, not just by convention.
 */
export function answerCardQualityQuestion(
  state: CardQualityAssistState,
  decision: CardQualityDecision
): CardQualityAssistState {
  if (state.resolved || state.currentIndex >= state.queue.length) {
    return state;
  }
  const kind = state.queue[state.currentIndex];
  const nextIndex = state.currentIndex + 1;
  return {
    ...state,
    decisions: { ...state.decisions, [kind]: decision },
    currentIndex: nextIndex,
    resolved: nextIndex >= state.queue.length,
  };
}
