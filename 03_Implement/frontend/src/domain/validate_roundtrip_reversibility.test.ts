import { describe, expect, it } from "vitest";

import { validateAndUpgradeImportedDocument } from "./validate";

// ADR-0048 D3 可逆性監査(ultracode workflow, 58エージェント)が確認した
// silent データ損失の回帰防止。いずれも import(validateAndUpgradeImportedDocument)
// 経由で有効な文書フィールドが無条件に欠落していた欠陥で、修正前は本テストが失敗する。
//
// 対象: DocumentV2 の5フィールド(readingOrder/narratives/relationSummaries/
// patchApplyLog/mergeSuggestionDecisions)、Island の6フィールド(titleReviewed/
// summaryText/summaryReviewed/summaryGrounding/summaryHistory/imageReviewed)、
// EvidenceLink.contradictionState。

const baseDoc = {
  version: 2 as const,
  id: "doc_reversibility",
  createdAt: "2026-06-21T00:00:00.000Z",
  updatedAt: "2026-06-21T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
};

describe("validateAndUpgradeImportedDocument: round-trip reversibility (ADR-0048 D3)", () => {
  it("preserves the 5 DocumentV2-level fields that were silently dropped (validate.ts:507-526)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [],
      readingOrder: ["c1"],
      narratives: [
        {
          id: "n1",
          title: "Narrative one",
          text: "reviewed narrative body",
          reviewed: true,
          createdAt: "2026-06-21T00:00:00.000Z",
          basedOnReadingOrder: ["c1"],
        },
      ],
      relationSummaries: [
        {
          id: "rs1",
          createdAt: "2026-06-21T00:00:00.000Z",
          islandAId: "isl_a",
          islandBId: "isl_b",
          relationType: "related",
          derived: false,
          text: "island relation summary",
          reviewed: true,
          groundingCardIds: ["c1"],
          groundingEdgeIds: [],
          sourceSignature: "sig-1",
        },
      ],
      patchApplyLog: [
        {
          id: "log1",
          createdAt: "2026-06-21T00:00:00.000Z",
          patchVersion: "1",
          appliedOpIds: ["op1"],
          stats: {
            upsertCards: 1,
            deleteCards: 0,
            upsertIslands: 0,
            deleteIslands: 0,
            upsertEdges: 0,
            deleteEdges: 0,
            upsertRelationSummaries: 0,
            deleteRelationSummaries: 0,
            upsertEvidenceLinks: 0,
            deleteEvidenceLinks: 0,
          },
        },
      ],
      mergeSuggestionDecisions: [
        {
          id: "dec1",
          groupId: "group1",
          decision: "accept",
          decidedAt: "2026-06-21T00:00:00.000Z",
          cardIds: ["c1"],
          mergedTextDraft: "draft text",
          editedText: "human-edited final text",
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.readingOrder).toEqual(["c1"]);
    expect(result.document.narratives?.[0]?.text).toBe("reviewed narrative body");
    expect(result.document.narratives?.[0]?.reviewed).toBe(true);
    expect(result.document.relationSummaries?.[0]?.text).toBe("island relation summary");
    expect(result.document.patchApplyLog?.[0]?.appliedOpIds).toEqual(["op1"]);
    expect(result.document.mergeSuggestionDecisions?.[0]?.editedText).toBe("human-edited final text");
  });

  it("preserves Island summary/review-state fields that were silently dropped (validate.ts parseIslands push)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "isl1",
          cardIds: ["c1"],
          titleReviewed: true,
          summaryText: "AI-generated island summary",
          summaryReviewed: true,
          summaryGrounding: ["c1"],
          summaryHistory: [
            {
              id: "hist1",
              createdAt: "2026-06-21T00:00:00.000Z",
              fromText: null,
              toText: "AI-generated island summary",
              fromReviewed: null,
              toReviewed: true,
              changeKind: "ai",
            },
          ],
          imageReviewed: true,
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const island = result.document.islands[0];
    expect(island?.titleReviewed).toBe(true);
    expect(island?.summaryText).toBe("AI-generated island summary");
    expect(island?.summaryReviewed).toBe(true);
    expect(island?.summaryGrounding).toEqual(["c1"]);
    expect(island?.summaryHistory?.[0]?.changeKind).toBe("ai");
    expect(island?.imageReviewed).toBe(true);
  });

  it("preserves EvidenceLink.contradictionState (DOMAIN-EXPR-04) that was silently dropped (validate.ts parseEvidenceLinks)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [
        { id: "c1", text: "A", x: 0, y: 0 },
        { id: "c2", text: "B", x: 10, y: 10 },
      ],
      edges: [],
      islands: [],
      evidenceLinks: [
        {
          id: "ev1",
          type: "contradicts",
          fromCardId: "c1",
          toCardId: "c2",
          contradictionState: "resolved",
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.evidenceLinks?.[0]?.contradictionState).toBe("resolved");
  });

  it("drops an out-of-enum contradictionState rather than crashing (defensive parsing)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [
        { id: "c1", text: "A", x: 0, y: 0 },
        { id: "c2", text: "B", x: 10, y: 10 },
      ],
      edges: [],
      islands: [],
      evidenceLinks: [
        { id: "ev1", type: "contradicts", fromCardId: "c1", toCardId: "c2", contradictionState: "bogus" },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.evidenceLinks?.[0]?.contradictionState).toBeUndefined();
  });
});

// validate.ts:118-119 の非対称性の回帰防止: cards が非配列/不正なら import 全体を
// 中断するのに対し、edges/islands(DocumentV2 の必須フィールド)は非配列でも
// parseEdges/parseIslands が silent に [] を返すだけで import は「成功」扱いに
// なっていた(既存データが警告なく全消失)。cards と同じ fail-closed 挙動に統一。
describe("validateAndUpgradeImportedDocument: malformed required arrays abort import (ADR-0048 D3)", () => {
  it("rejects a document whose edges field is present but not an array, instead of silently dropping all edges", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: "corrupted",
      islands: [],
    });

    expect(result.ok).toBe(false);
  });

  it("rejects a document whose islands field is present but not an array, instead of silently dropping all islands", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: { not: "an array" },
    });

    expect(result.ok).toBe(false);
  });

  it("still imports normally when edges/islands are simply absent (legitimate default, no regression)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.edges).toEqual([]);
    expect(result.document.islands).toEqual([]);
  });
});
