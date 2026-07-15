import { describe, expect, it } from "vitest";

import {
  CARD_QUALITY_DECISIONS,
  CARD_QUALITY_QUESTION_KINDS,
  answerCardQualityQuestion,
  currentCardQualityQuestion,
  openCardQualityAssist,
  type CardQualityAssistState,
} from "./card_quality";
import { CARD_QUALITY_FIXTURES, findCardQualityFixture } from "./card_quality.fixture";

function resolveAll(state: CardQualityAssistState, decisionForKind: (kind: string) => "apply" | "keep_as_is" | "hold_for_now"): CardQualityAssistState {
  let next = state;
  while (!next.resolved) {
    const question = currentCardQualityQuestion(next);
    if (!question) {
      break;
    }
    next = answerCardQualityQuestion(next, decisionForKind(question.kind));
  }
  return next;
}

describe("card quality fixtures", () => {
  it("covers all 6 representative kinds from qualitative_card_quality_requirements.md §7", () => {
    const kinds = CARD_QUALITY_FIXTURES.map((fixture) => fixture.kind).sort();
    expect(kinds).toEqual(
      [
        "context_poor",
        "minority_or_contradiction",
        "multi_center",
        "quote_interpretation_mixed",
        "single_center",
        "unknown_source",
      ].sort()
    );
  });
});

describe("CARD_QUALITY_DECISIONS", () => {
  it("never includes a score, rank, or destructive verb (CQ-DIVERSE-01, §5)", () => {
    const forbidden = ["score", "rank", "pass", "fail", "delete", "merge", "downgrade", "priority", "confidence"];
    for (const decision of CARD_QUALITY_DECISIONS) {
      for (const word of forbidden) {
        expect(decision.toLowerCase()).not.toContain(word);
      }
    }
  });
});

describe("openCardQualityAssist / answerCardQualityQuestion", () => {
  it("presents the fixed unit -> context -> trace -> status order for every fixture kind, with no special-casing", () => {
    for (const fixture of CARD_QUALITY_FIXTURES) {
      const state = openCardQualityAssist(fixture.card);
      expect(state.queue).toEqual(CARD_QUALITY_QUESTION_KINDS);
      expect(state.resolved).toBe(false);
    }
  });

  it("keeps the minority/contradiction fixture on the identical queue as any other fixture (no auto-flagging as low quality)", () => {
    const minority = openCardQualityAssist(findCardQualityFixture("minority_or_contradiction").card);
    const singleCenter = openCardQualityAssist(findCardQualityFixture("single_center").card);
    expect(minority.queue).toEqual(singleCenter.queue);
  });

  it("does not resolve until all 4 questions are answered", () => {
    const card = findCardQualityFixture("multi_center").card;
    let state = openCardQualityAssist(card);

    for (let index = 0; index < CARD_QUALITY_QUESTION_KINDS.length - 1; index += 1) {
      expect(state.resolved).toBe(false);
      state = answerCardQualityQuestion(state, "hold_for_now");
    }
    expect(state.resolved).toBe(false);

    state = answerCardQualityQuestion(state, "hold_for_now");
    expect(state.resolved).toBe(true);
    expect(currentCardQualityQuestion(state)).toBeUndefined();
  });

  it("never mutates the card (AC-5: no change before a decision is adopted)", () => {
    const card = Object.freeze({ ...findCardQualityFixture("quote_interpretation_mixed").card });

    let state = openCardQualityAssist(card);
    expect(() => {
      state = resolveAll(state, () => "apply");
    }).not.toThrow();

    expect(card.text).toBe(findCardQualityFixture("quote_interpretation_mixed").card.text);
  });

  it("does not re-surface a kept-as-is question in the same session unless the text changed (QUX-HUMAN-01)", () => {
    const card = findCardQualityFixture("context_poor").card;
    let state = openCardQualityAssist(card);
    state = answerCardQualityQuestion(state, "keep_as_is"); // unit
    state = resolveAll(state, () => "hold_for_now");
    expect(state.decisions.unit).toBe("keep_as_is");

    const reopenedSameText = openCardQualityAssist(card, state);
    expect(reopenedSameText.queue).not.toContain("unit");

    const editedCard = { ...card, text: `${card.text} 追記した。` };
    const reopenedAfterEdit = openCardQualityAssist(editedCard, state);
    expect(reopenedAfterEdit.queue).toContain("unit");
  });

  it("is a pure data-flow module with no LLM provider dependency (KJ_ATLAS_LLM_PROVIDER=none equivalence)", () => {
    // The whole flow must work with nothing but the fixture + these exports —
    // no provider, network, or async call is reachable from this module.
    const card = findCardQualityFixture("unknown_source").card;
    const resolved = resolveAll(openCardQualityAssist(card), () => "keep_as_is");
    expect(resolved.resolved).toBe(true);
    expect(Object.keys(resolved.decisions).sort()).toEqual([...CARD_QUALITY_QUESTION_KINDS].sort());
  });
});
