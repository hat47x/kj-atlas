import { describe, expect, it, vi } from "vitest";

import { appendMergeSuggestionDecision } from "./merge_suggestion_decisions";
import { applyRecordedMergeSuggestionDecision } from "./merge_suggestion_apply";
import { resolveRepresentativeOriginTrace } from "./merge_traceability";
import type { DocumentV1, MergeSuggestionDecisionEntry } from "./types";

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
        meta: { source: "interview-01:line-12" },
      },
      {
        id: "c2",
        text: "待ち時間は利用継続を妨げる",
        x: 20,
        y: 20,
        textReviewed: true,
        claimType: "claim",
        meta: { source: "interview-02:line-08" },
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

function recordDecision(
  document: DocumentV1,
  decision: "accept" | "partial" | "reject" | "defer" = "accept",
): { document: DocumentV1; decision: MergeSuggestionDecisionEntry } {
  const nextDocument = appendMergeSuggestionDecision(
    document,
    {
      groupId: "g1",
      decision,
      cardIds: decision === "partial" ? ["c1", "c2", "c3"] : ["c1", "c2"],
      selectedCardIds: decision === "partial" ? ["c1", "c2"] : undefined,
      mergedTextDraft: "待ち時間は利用継続の負担になる",
      editedText: "待ち時間は利用継続の負担になる",
      mergeMethod: "near_duplicate",
      decisionReason: "二つの記述の差を残したうえで代表表現として採用する",
    },
    {
      idFactory: () => "d1",
      now: "2026-09-03T00:01:00.000Z",
    },
  );
  const recorded = nextDocument.mergeSuggestionDecisions?.at(-1);
  if (!recorded) throw new Error("decision fixture was not recorded");
  return { document: nextDocument, decision: recorded };
}

describe("applyRecordedMergeSuggestionDecision", () => {
  it("applies a recorded accept without deleting source meaning and updates the decision snapshot", () => {
    const before = documentFixture();
    const recorded = recordDecision(before);
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000101");

    const result = applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision);

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const representative = result.document.cards.find((card) => card.id === result.representativeCardId);
    expect(representative).toMatchObject({
      id: "00000000-0000-0000-0000-000000000101",
      text: "待ち時間は利用継続の負担になる",
      textReviewed: false,
      repOf: ["c1", "c2"],
      sources: ["c1", "c2"],
    });

    expect(result.document.cards.find((card) => card.id === "c1")).toMatchObject({
      text: before.cards[0]?.text,
      meta: { source: "interview-01:line-12" },
      mergedIntoCardId: result.representativeCardId,
      canonicalId: result.representativeCardId,
    });
    expect(result.document.cards.find((card) => card.id === "c2")).toMatchObject({
      text: before.cards[1]?.text,
      meta: { source: "interview-02:line-08" },
      mergedIntoCardId: result.representativeCardId,
      canonicalId: result.representativeCardId,
    });

    // 最も可逆な初期適用では、source側の構造を変更しない。
    expect(result.document.islands).toEqual(before.islands);
    expect(result.document.edges).toEqual(before.edges);
    expect(result.document.evidenceLinks).toEqual(before.evidenceLinks);
    expect(result.document.readingOrder).toEqual(before.readingOrder);

    const appliedDecision = result.document.mergeSuggestionDecisions?.find((entry) => entry.id === "d1");
    expect(appliedDecision).toMatchObject({
      representativeCardId: result.representativeCardId,
      representativeResolvedBy: "repOf",
      sourceCardIds: ["c1", "c2"],
      missingSourceCardIds: [],
    });
  });

  it("survives a JSON save/reload round trip with source lineage and external raw-data references intact", () => {
    const recorded = recordDecision(documentFixture());
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000102");

    const result = applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision);
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const reloaded = JSON.parse(JSON.stringify(result.document)) as DocumentV1;
    const trace = resolveRepresentativeOriginTrace(reloaded, result.representativeCardId);

    expect(trace).toMatchObject({
      representativeCardId: result.representativeCardId,
      representativeResolvedBy: "repOf",
      sourceCardIds: ["c1", "c2"],
      missingSourceCardIds: [],
    });
    expect(reloaded.cards.find((card) => card.id === "c1")?.meta?.source).toBe("interview-01:line-12");
    expect(reloaded.cards.find((card) => card.id === "c2")?.meta?.source).toBe("interview-02:line-08");
  });

  it("applies only the human-selected subset for a recorded partial decision", () => {
    const before = documentFixture();
    const recorded = recordDecision(before, "partial");
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000103");

    const result = applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision);
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.sourceCardIds).toEqual(["c1", "c2"]);
    expect(result.document.cards.find((card) => card.id === "c1")?.mergedIntoCardId).toBe(result.representativeCardId);
    expect(result.document.cards.find((card) => card.id === "c2")?.mergedIntoCardId).toBe(result.representativeCardId);
    expect(result.document.cards.find((card) => card.id === "c3")).toEqual(before.cards.find((card) => card.id === "c3"));
    expect(result.document.mergeSuggestionDecisions?.at(-1)).toMatchObject({
      decision: "partial",
      selectedCardIds: ["c1", "c2"],
      sourceCardIds: ["c1", "c2"],
      representativeCardId: result.representativeCardId,
    });
  });

  it("refuses ambiguous legacy partial decisions and still refuses reject/defer", () => {
    const base = documentFixture();
    const legacyMissing = {
      id: "legacy-missing",
      decisionId: "legacy-missing",
      groupId: "g1",
      decision: "partial" as const,
      action: "partial" as const,
      decidedAt: "2026-09-03T00:01:00.000Z",
      cardIds: ["c1", "c2", "c3"],
      mergedTextDraft: "draft",
      editedText: "draft",
    };
    const missingDoc = { ...base, mergeSuggestionDecisions: [legacyMissing] };
    expect(applyRecordedMergeSuggestionDecision(missingDoc, legacyMissing)).toEqual({
      ok: false, code: "partial_selection_missing",
    });

    const legacyFull = { ...legacyMissing, id: "legacy-full", decisionId: "legacy-full", selectedCardIds: ["c1", "c2", "c3"] };
    const fullDoc = { ...base, mergeSuggestionDecisions: [legacyFull] };
    expect(applyRecordedMergeSuggestionDecision(fullDoc, legacyFull)).toEqual({
      ok: false, code: "partial_selection_invalid",
    });

    for (const decision of ["reject", "defer"] as const) {
      const recorded = recordDecision(documentFixture(), decision);
      expect(applyRecordedMergeSuggestionDecision(recorded.document, recorded.decision)).toEqual({
        ok: false,
        code: "decision_not_accepted",
      });
    }
  });

  it("refuses an unrecorded decision object", () => {
    const recorded = recordDecision(documentFixture());
    const forged: MergeSuggestionDecisionEntry = {
      ...recorded.decision,
      id: "other-id",
      decisionId: "other-id",
    };

    expect(applyRecordedMergeSuggestionDecision(recorded.document, forged)).toEqual({
      ok: false,
      code: "decision_not_recorded",
    });
  });

  it("re-checks holds, stale lineage and contradictions after the decision was recorded", () => {
    const held = recordDecision(documentFixture());
    held.document.cards = held.document.cards.map((card) =>
      card.id === "c2" ? { ...card, holdState: "held" as const } : card,
    );
    expect(applyRecordedMergeSuggestionDecision(held.document, held.decision)).toEqual({
      ok: false,
      code: "source_card_held",
    });

    const alreadyMerged = recordDecision(documentFixture());
    alreadyMerged.document.cards = alreadyMerged.document.cards.map((card) =>
      card.id === "c1" ? { ...card, mergedIntoCardId: "old-representative" } : card,
    );
    expect(applyRecordedMergeSuggestionDecision(alreadyMerged.document, alreadyMerged.decision)).toEqual({
      ok: false,
      code: "source_card_already_merged",
    });

    const negate = recordDecision(documentFixture());
    negate.document.edges = [
      ...negate.document.edges,
      { id: "neg", fromId: "c1", toId: "c2", type: "negate" },
    ];
    expect(applyRecordedMergeSuggestionDecision(negate.document, negate.decision)).toEqual({
      ok: false,
      code: "negate_conflict",
    });

    const contradicts = recordDecision(documentFixture());
    contradicts.document.evidenceLinks = [
      ...(contradicts.document.evidenceLinks ?? []),
      { id: "contra", type: "contradicts", fromCardId: "c1", toCardId: "c2" },
    ];
    expect(applyRecordedMergeSuggestionDecision(contradicts.document, contradicts.decision)).toEqual({
      ok: false,
      code: "contradiction_evidence_conflict",
    });
  });
});
