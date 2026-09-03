import { describe, expect, it, vi } from "vitest";

import { parseDocumentJson } from "../import/document_import";
import { resolveDecisionOriginTrace } from "./merge_traceability";
import { applyMergeSuggestionHumanDecision } from "./merge_suggestion_apply";
import type { DocumentV1 } from "./types";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-merge-accept",
    title: "merge accept",
    createdAt: "2026-09-03T00:00:00.000Z",
    updatedAt: "2026-09-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "c1",
        text: "利用者は待ち時間を長く感じている",
        x: 0,
        y: 0,
        textReviewed: true,
        claimType: "fact",
        meta: { source: "interview-1" },
      },
      {
        id: "c2",
        text: "待ち時間の長さが不満として語られた",
        x: 100,
        y: 0,
        textReviewed: true,
        claimType: "fact",
        meta: { source: "interview-2" },
      },
      { id: "context", text: "受付の説明は丁寧だった", x: 200, y: 0, textReviewed: true },
    ],
    edges: [
      { id: "e1", fromId: "c1", toId: "context", fromKind: "card", toKind: "card", type: "related" },
    ],
    islands: [
      { id: "i1", cardIds: ["c1", "c2"], title: "待ち時間", titleReviewed: true },
    ],
    readingOrder: ["i1"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const suggestion = {
  groupId: "g1",
  cardIds: ["c2", "c1"],
  mergedTextDraft: "待ち時間が不満として語られた",
  editedText: "利用者は待ち時間の長さを不満として語った",
  rationale: "近接した観察を統合する候補",
};

describe("applyMergeSuggestionHumanDecision", () => {
  it("accept applies one representative, records its decision snapshot, and survives JSON reload", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000101");

    const result = applyMergeSuggestionHumanDecision(
      createDocument(),
      suggestion,
      "accept",
      { decisionReason: "元の二つの観察へ戻して確認した" },
      {
        decisionIdFactory: () => "decision-1",
        now: "2026-09-03T10:20:00.000Z",
      }
    );

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    expect(result.appliedRepresentativeCardId).toBe("00000000-0000-0000-0000-000000000101");
    const representative = result.nextDocument.cards.find(
      (card) => card.id === result.appliedRepresentativeCardId
    );
    expect(representative).toMatchObject({
      text: suggestion.editedText,
      repOf: ["c1", "c2"],
      sources: ["c1", "c2"],
      claimType: "fact",
      textReviewed: false,
    });
    expect(result.nextDocument.cards.find((card) => card.id === "c1")).toMatchObject({
      text: "利用者は待ち時間を長く感じている",
      mergedIntoCardId: result.appliedRepresentativeCardId,
      canonicalId: result.appliedRepresentativeCardId,
      meta: { source: "interview-1" },
    });
    expect(result.nextDocument.cards.find((card) => card.id === "c2")).toMatchObject({
      text: "待ち時間の長さが不満として語られた",
      mergedIntoCardId: result.appliedRepresentativeCardId,
      canonicalId: result.appliedRepresentativeCardId,
      meta: { source: "interview-2" },
    });

    // Accepting merged wording does not silently accept a topology rewrite.
    expect(result.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2"]);
    expect(result.nextDocument.edges).toEqual(createDocument().edges);

    const decision = result.nextDocument.mergeSuggestionDecisions?.at(-1);
    expect(decision).toMatchObject({
      id: "decision-1",
      decision: "accept",
      selectedCardIds: ["c1", "c2"],
      representativeCardId: result.appliedRepresentativeCardId,
      representativeResolvedBy: "repOf",
      sourceCardIds: ["c1", "c2"],
      missingSourceCardIds: [],
      note: "元の二つの観察へ戻して確認した",
    });

    const reloaded = parseDocumentJson(JSON.stringify(result.nextDocument));
    expect(reloaded.ok).toBe(true);
    if (!reloaded.ok) {
      return;
    }

    const trace = resolveDecisionOriginTrace(reloaded.document, ["c1", "c2"]);
    expect(trace).toEqual({
      representativeCardId: result.appliedRepresentativeCardId,
      sourceCardIds: ["c1", "c2"],
      missingSourceCardIds: [],
      representativeResolvedBy: "repOf",
    });
    expect(reloaded.document.mergeSuggestionDecisions?.at(-1)?.representativeCardId).toBe(
      result.appliedRepresentativeCardId
    );
  });

  it("partial stays decision-only because no accepted subset is defined", () => {
    const before = createDocument();
    const result = applyMergeSuggestionHumanDecision(
      before,
      suggestion,
      "partial",
      { decisionReason: "一部だけ採用したいが対象カードはまだ選んでいない" },
      { decisionIdFactory: () => "decision-partial", now: "2026-09-03T10:21:00.000Z" }
    );

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }
    expect(result.appliedRepresentativeCardId).toBeUndefined();
    expect(result.nextDocument.cards).toEqual(before.cards);
    expect(result.nextDocument.mergeSuggestionDecisions?.at(-1)).toMatchObject({
      id: "decision-partial",
      decision: "partial",
      representativeResolvedBy: "fallback",
    });
  });

  it("reject and defer never apply a representative", () => {
    for (const decision of ["reject", "defer"] as const) {
      const before = createDocument();
      const result = applyMergeSuggestionHumanDecision(
        before,
        suggestion,
        decision,
        { decisionReason: `${decision} reason` },
        { decisionIdFactory: () => `decision-${decision}`, now: "2026-09-03T10:22:00.000Z" }
      );
      expect(result.ok).toBe(true);
      if (result.ok) {
        expect(result.appliedRepresentativeCardId).toBeUndefined();
        expect(result.nextDocument.cards).toEqual(before.cards);
      }
    }
  });

  it("accept fails atomically when the merge is no longer safe", () => {
    const held = createDocument();
    held.cards = held.cards.map((card) =>
      card.id === "c2" ? { ...card, holdState: "held" as const } : card
    );

    const result = applyMergeSuggestionHumanDecision(
      held,
      suggestion,
      "accept",
      { decisionReason: "accept" },
      { decisionIdFactory: () => "must-not-be-used", now: "2026-09-03T10:23:00.000Z" }
    );

    expect(result).toEqual({ ok: false, reason: "merge_not_applicable" });
    expect(held.mergeSuggestionDecisions).toEqual([]);
    expect(held.cards.some((card) => card.mergedIntoCardId)).toBe(false);
  });
});
