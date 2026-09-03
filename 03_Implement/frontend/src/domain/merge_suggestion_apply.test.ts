import { describe, expect, it, vi } from "vitest";

import type { DocumentV1, MergeSuggestionDecisionEntry } from "./types";
import { applyRecordedMergeSuggestionDecision } from "./merge_suggestion_apply";

function documentFixture(): DocumentV1 {
  return {
    version: 1,
    id: "doc-merge-apply",
    createdAt: "2026-09-03T00:00:00.000Z",
    updatedAt: "2026-09-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "c1",
        text: "利用者は待ち時間を負担に感じる",
        x: 0,
        y: 0,
        textReviewed: true,
        claimType: "claim",
        sources: ["raw-a"],
      },
      {
        id: "c2",
        text: "待ち時間は利用継続を妨げる",
        x: 20,
        y: 20,
        textReviewed: true,
        claimType: "claim",
        sources: ["raw-b"],
      },
      {
        id: "c3",
        text: "別の観察",
        x: 40,
        y: 40,
        textReviewed: true,
        claimType: "claim",
      },
    ],
    edges: [{ id: "e1", fromId: "c1", toId: "c3", type: "causal" }],
    evidenceLinks: [
      { id: "ev1", type: "supports", fromCardId: "c2", toCardId: "c3" },
    ],
    islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
    readingOrder: ["i1"],
    narratives: [],
  };
}

function decision(overrides: Partial<MergeSuggestionDecisionEntry> = {}): MergeSuggestionDecisionEntry {
  return {
    id: "d1",
    decisionId: "d1",
    groupId: "g1",
    decision: "accept",
    action: "accept",
    decidedAt: "2026-09-03T00:01:00.000Z",
    decidedBy: "human",
    cardIds: ["c1", "c2"],
    selectedCardIds: ["c1", "c2"],
    mergedTextDraft: "待ち時間は利用継続の負担になる",
    editedText: "待ち時間は利用継続の負担になる",
    snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
    ...overrides,
  };
}

describe("applyRecordedMergeSuggestionDecision", () => {
  it("materializes an accepted representative without deleting source meaning or graph context", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000101");
    const before = documentFixture();

    const result = applyRecordedMergeSuggestionDecision(before, decision());

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const representative = result.document.cards.find((card) => card.id === result.representativeCardId);
    expect(representative).toMatchObject({
      id: "00000000-0000-0000-0000-000000000101",
      text: "待ち時間は利用継続の負担になる",
      textReviewed: true,
      repOf: ["c1", "c2"],
    });

    // Source cards remain complete and point to the derived representative.
    expect(result.document.cards.find((card) => card.id === "c1")).toMatchObject({
      text: before.cards[0]?.text,
      sources: ["raw-a"],
      mergedIntoCardId: result.representativeCardId,
    });
    expect(result.document.cards.find((card) => card.id === "c2")).toMatchObject({
      text: before.cards[1]?.text,
      sources: ["raw-b"],
      mergedIntoCardId: result.representativeCardId,
    });

    // Lossless-first application does not rewrite the source graph. These are
    // the residual/context records needed to return from the representative.
    expect(result.document.islands).toEqual(before.islands);
    expect(result.document.edges).toEqual(before.edges);
    expect(result.document.evidenceLinks).toEqual(before.evidenceLinks);
    expect(result.document.readingOrder).toEqual(before.readingOrder);
  });

  it("uses the human-selected subset for a partial decision", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000102");
    const before = documentFixture();
    before.cards.push({
      id: "c4",
      text: "補助的な類似所見",
      x: 60,
      y: 60,
      textReviewed: true,
      claimType: "claim",
    });

    const result = applyRecordedMergeSuggestionDecision(
      before,
      decision({
        decision: "partial",
        action: "partial",
        cardIds: ["c1", "c2", "c4"],
        selectedCardIds: ["c1", "c2"],
      }),
    );

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.sourceCardIds).toEqual(["c1", "c2"]);
    expect(result.document.cards.find((card) => card.id === "c4")?.mergedIntoCardId).toBeUndefined();
  });

  it("does not materialize reject/defer decisions", () => {
    expect(
      applyRecordedMergeSuggestionDecision(
        documentFixture(),
        decision({ decision: "reject", action: "reject" }),
      ),
    ).toEqual({ ok: false, code: "decision_not_adoptable" });
  });

  it("re-checks a hold added after the recorded decision", () => {
    const current = documentFixture();
    current.cards = current.cards.map((card) =>
      card.id === "c2" ? { ...card, holdState: "held" as const } : card,
    );

    expect(applyRecordedMergeSuggestionDecision(current, decision())).toEqual({
      ok: false,
      code: "source_card_held",
    });
  });

  it("re-checks explicit contradictions added after the recorded decision", () => {
    const withNegate = documentFixture();
    withNegate.edges = [
      ...withNegate.edges,
      { id: "neg", fromId: "c1", toId: "c2", type: "negate" },
    ];
    expect(applyRecordedMergeSuggestionDecision(withNegate, decision())).toEqual({
      ok: false,
      code: "negate_conflict",
    });

    const withEvidence = documentFixture();
    withEvidence.evidenceLinks = [
      ...(withEvidence.evidenceLinks ?? []),
      { id: "contra", type: "contradicts", fromCardId: "c1", toCardId: "c2" },
    ];
    expect(applyRecordedMergeSuggestionDecision(withEvidence, decision())).toEqual({
      ok: false,
      code: "contradiction_evidence_conflict",
    });
  });

  it("refuses stale lineage and invalid partial selections", () => {
    const alreadyMerged = documentFixture();
    alreadyMerged.cards = alreadyMerged.cards.map((card) =>
      card.id === "c1" ? { ...card, mergedIntoCardId: "old-representative" } : card,
    );
    expect(applyRecordedMergeSuggestionDecision(alreadyMerged, decision())).toEqual({
      ok: false,
      code: "source_card_already_merged",
    });

    expect(
      applyRecordedMergeSuggestionDecision(
        documentFixture(),
        decision({
          decision: "partial",
          action: "partial",
          selectedCardIds: ["c1"],
        }),
      ),
    ).toEqual({ ok: false, code: "selection_too_small" });
  });
});
