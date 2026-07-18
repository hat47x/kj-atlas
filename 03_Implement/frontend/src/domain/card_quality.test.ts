import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  CARD_QUALITY_DECISIONS,
  CARD_QUALITY_QUESTION_KINDS,
  answerCardQualityQuestion,
  beginCardQualityRewrite,
  cardQualityRestoreTarget,
  currentCardQualityQuestion,
  openCardQualityAssist,
  type CardQualityAssistState,
  type CardQualityDecision,
} from "./card_quality";
import { CARD_QUALITY_FIXTURES, findCardQualityFixture } from "./card_quality.fixture";

/** Read frontend source file text for source-string contract checks (T6, per core_value_guard.test.ts's idiom). */
function readSource(relativePath: string): string {
  return readFileSync(resolve(__dirname, "..", relativePath), "utf-8");
}

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

  // T6: 提案採用前の不変条件、少数・矛盾保持、SafeMode、provider noneをunit/integrationで固定する。
  it("never mutates any of the 6 representative fixtures, under every decision, including the most aggressive path (AC-5)", () => {
    const decisionSequences: CardQualityDecision[][] = [
      ["apply", "apply", "apply", "apply"],
      ["keep_as_is", "keep_as_is", "keep_as_is", "keep_as_is"],
      ["hold_for_now", "apply", "keep_as_is", "hold_for_now"],
    ];

    for (const fixture of CARD_QUALITY_FIXTURES) {
      const originalCard = { ...fixture.card };
      for (const sequence of decisionSequences) {
        const frozenCard = Object.freeze({ ...fixture.card });
        let state = openCardQualityAssist(frozenCard);
        let index = 0;
        while (!state.resolved) {
          state = answerCardQualityQuestion(state, sequence[index] ?? "hold_for_now");
          index += 1;
        }
        expect(frozenCard).toEqual(originalCard);
      }
    }
  });

  it("preserves the minority/contradiction fixture verbatim even when every question is answered 'apply' (CQ-DIVERSE-01)", () => {
    const fixture = findCardQualityFixture("minority_or_contradiction");
    const frozenCard = Object.freeze({ ...fixture.card });
    resolveAll(openCardQualityAssist(frozenCard), () => "apply");
    expect(frozenCard.critiqueTags).toEqual(fixture.card.critiqueTags);
    expect(frozenCard.text).toBe(fixture.card.text);
  });
});

describe("card quality rewrite restoration", () => {
  it("keeps the original text as the restoration target", () => {
    const state = beginCardQualityRewrite(
      openCardQualityAssist(findCardQualityFixture("multi_center").card),
      "original wording"
    );

    expect(cardQualityRestoreTarget(state)).toBe("original wording");
  });

  it("returns undefined before a rewrite begins", () => {
    const state = openCardQualityAssist(findCardQualityFixture("single_center").card);
    expect(cardQualityRestoreTarget(state)).toBeUndefined();
  });

  it("preserves the first original text when rewrite begins more than once", () => {
    const initial = openCardQualityAssist(findCardQualityFixture("multi_center").card);
    const first = beginCardQualityRewrite(initial, "first original");
    const second = beginCardQualityRewrite(first, "later edited text");

    expect(second).toBe(first);
    expect(cardQualityRestoreTarget(second)).toBe("first original");
  });

  it("clears the restoration target when the restored card is opened again", () => {
    const card = findCardQualityFixture("multi_center").card;
    const rewriting = beginCardQualityRewrite(openCardQualityAssist(card), card.text);
    const reopenedAfterRestore = openCardQualityAssist(card, rewriting);

    expect(cardQualityRestoreTarget(reopenedAfterRestore)).toBeUndefined();
  });
});

describe("card_quality.ts source boundary (T6: SafeMode / provider-none)", () => {
  const source = readSource("domain/card_quality.ts");

  it("has no runtime import — only a type-only import of Card, so there is zero external I/O surface", () => {
    const importLines = source.match(/^import .+$/gm) ?? [];
    for (const line of importLines) {
      expect(line).toMatch(/^import type /);
    }
  });

  it("never references an LLM/AI provider, network call, or storage API (KJ_ATLAS_LLM_PROVIDER=none holds trivially)", () => {
    const forbidden = ["Provider", "fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "axios", "worker"];
    for (const word of forbidden) {
      expect(source).not.toContain(word);
    }
  });

  it("never reads Card.meta.source, Card.critique, or any other SafeMode-governed free-text field", () => {
    // The assist only ever touches `id`/`text` (for identity/session-continuity
    // comparisons) — it must never branch on or forward the actual card content,
    // which is exactly the surface SafeMode redaction/export boundaries govern.
    expect(source).not.toContain(".meta");
    expect(source).not.toContain(".critique");
    expect(source).not.toContain(".claimType");
  });
});
