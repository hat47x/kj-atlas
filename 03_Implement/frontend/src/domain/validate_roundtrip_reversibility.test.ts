import { describe, expect, it } from "vitest";

import { validateAndUpgradeImportedDocument } from "./validate";
import { validateDocumentV2Strict } from "./validate_doc";

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

// DOMAIN-KJ-01 (schemas.md §3.3.2): 未知エッジ種別の保全。修正前の validate.ts は
// 既知enum以外の type を持つエッジを取り込み時に silent 破棄しており、旧クライアント
// 経由のラウンドトリップで新語彙（causal/mutual/equivalence や将来の種別）の関係線が
// 消失する実データ損失だった。寛容(import)・厳格(契約検証)の両モードで保全を固定する。
describe("edge type vocabulary and unknown-type preservation (DOMAIN-KJ-01)", () => {
  const cardsPair = [
    { id: "c1", text: "A", x: 0, y: 0 },
    { id: "c2", text: "B", x: 10, y: 10 },
  ];

  it("imports all five known edge types without loss (lenient mode)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: cardsPair,
      edges: [
        { id: "e1", fromId: "c1", toId: "c2", type: "related" },
        { id: "e2", fromId: "c1", toId: "c2", type: "negate" },
        { id: "e3", fromId: "c1", toId: "c2", type: "causal" },
        { id: "e4", fromId: "c1", toId: "c2", type: "mutual" },
        { id: "e5", fromId: "c1", toId: "c2", type: "equivalence" },
      ],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.edges.map((edge) => edge.type)).toEqual([
      "related",
      "negate",
      "causal",
      "mutual",
      "equivalence",
    ]);
  });

  it("preserves an UNKNOWN edge type string verbatim instead of discarding the edge (lenient mode)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: cardsPair,
      edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "future-vocab-2030" }],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.edges).toHaveLength(1);
    expect(result.document.edges[0]?.type).toBe("future-vocab-2030");
  });

  it("still drops an edge whose type is missing, non-string, or empty (structurally invalid)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: cardsPair,
      edges: [
        { id: "e1", fromId: "c1", toId: "c2" },
        { id: "e2", fromId: "c1", toId: "c2", type: 42 },
        { id: "e3", fromId: "c1", toId: "c2", type: "" },
      ],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.edges).toEqual([]);
  });

  it("strict mode also accepts known-new and unknown edge types (AC-3: both modes preserve)", () => {
    const strict = validateDocumentV2Strict({
      ...baseDoc,
      title: "strict",
      cards: cardsPair,
      edges: [
        { id: "e1", fromId: "c1", toId: "c2", type: "causal" },
        { id: "e2", fromId: "c1", toId: "c2", type: "future-vocab-2030" },
      ],
      islands: [],
    });

    expect(strict.ok).toBe(true);
  });

  it("strict mode still rejects an empty edge type string", () => {
    const strict = validateDocumentV2Strict({
      ...baseDoc,
      title: "strict",
      cards: cardsPair,
      edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "" }],
      islands: [],
    });

    expect(strict.ok).toBe(false);
    if (strict.ok) return;
    expect(strict.errors.join("\n")).toContain("edges[0].type");
  });

  it("normalizes an unknown relationSummary relationType to 'unknown' instead of dropping the summary", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: cardsPair,
      edges: [],
      islands: [],
      relationSummaries: [
        {
          id: "rs1",
          createdAt: "2026-06-21T00:00:00.000Z",
          islandAId: "isl_a",
          islandBId: "isl_b",
          relationType: "future-vocab-2030",
          derived: true,
          text: "summary text survives",
          reviewed: false,
          groundingCardIds: [],
          groundingEdgeIds: [],
          sourceSignature: "sig-x",
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.relationSummaries).toHaveLength(1);
    expect(result.document.relationSummaries?.[0]?.relationType).toBe("unknown");
    expect(result.document.relationSummaries?.[0]?.text).toBe("summary text survives");
  });

  it("accepts the new known relationTypes on relation summaries (lenient mode)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: cardsPair,
      edges: [],
      islands: [],
      relationSummaries: [
        {
          id: "rs1",
          createdAt: "2026-06-21T00:00:00.000Z",
          islandAId: "isl_a",
          islandBId: "isl_b",
          relationType: "causal",
          derived: true,
          text: "causal summary",
          reviewed: false,
          groundingCardIds: [],
          groundingEdgeIds: [],
          sourceSignature: "sig-c",
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.relationSummaries?.[0]?.relationType).toBe("causal");
  });
});

// DOMAIN-TRACE-01 (schemas.md §15): Card.meta（通し番号・原データ遡及）の往復保全と、
// meta 内の未知キーの fail-closed 破棄。未知キーの扱いが DOMAIN-KJ-01（未知エッジ種別の
// 保全）と意図的に逆であることに注意 — 主体メタ（起票者等）が CARD-META-UI-01 の確定前に
// import 経由で永続化される抜け道を塞ぐ（同Issue AC-5）。
describe("Card.meta trace fields (DOMAIN-TRACE-01)", () => {
  it("preserves seq and source through lenient import", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0, meta: { seq: 42, source: "インタビューA 12行目" } }],
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.cards[0]?.meta).toEqual({ seq: 42, source: "インタビューA 12行目" });
  });

  it("drops UNKNOWN meta keys fail-closed while keeping the known ones (§15.3, inverse of DOMAIN-KJ-01)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [
        {
          id: "c1",
          text: "A",
          x: 0,
          y: 0,
          meta: { seq: 1, source: "memo", createdBy: "alice@example.com", ownerRef: "user:1" },
        },
      ],
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.cards[0]?.meta).toEqual({ seq: 1, source: "memo" });
    expect((result.document.cards[0]?.meta as Record<string, unknown>).createdBy).toBeUndefined();
  });

  it("drops invalid seq/source values and the whole meta when nothing valid remains, keeping the card", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [
        { id: "c1", text: "A", x: 0, y: 0, meta: { seq: "not-a-number", source: "" } },
        { id: "c2", text: "B", x: 10, y: 10, meta: { seq: Infinity } },
        { id: "c3", text: "C", x: 20, y: 20, meta: "bogus" },
      ],
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.cards).toHaveLength(3);
    expect(result.document.cards[0]?.meta).toBeUndefined();
    expect(result.document.cards[1]?.meta).toBeUndefined();
    expect(result.document.cards[2]?.meta).toBeUndefined();
  });

  it("strict mode accepts valid meta and rejects unknown meta keys", () => {
    const valid = validateDocumentV2Strict({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0, meta: { seq: 3, source: "field note p.2" } }],
      edges: [],
      islands: [],
    });
    expect(valid.ok).toBe(true);

    const invalid = validateDocumentV2Strict({
      ...baseDoc,
      cards: [{ id: "c1", text: "A", x: 0, y: 0, meta: { seq: 3, createdBy: "alice" } }],
      edges: [],
      islands: [],
    });
    expect(invalid.ok).toBe(false);
    if (invalid.ok) return;
    expect(invalid.errors.join("\n")).toContain("cards[0].meta");
  });
});

describe("contradictionSignalDecisions (DOMAIN-EXPR-04)", () => {
  it("preserves valid decisions through lenient import", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [],
      edges: [],
      islands: [],
      contradictionSignalDecisions: [
        { signatureKey: "C001:island:a|island:b", status: "accepted", decidedAt: "2026-07-08T00:00:00.000Z" },
        { signatureKey: "C004:island:c", status: "rejected", decidedAt: "2026-07-08T00:00:01.000Z" },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.contradictionSignalDecisions).toEqual([
      { signatureKey: "C001:island:a|island:b", status: "accepted", decidedAt: "2026-07-08T00:00:00.000Z" },
      { signatureKey: "C004:island:c", status: "rejected", decidedAt: "2026-07-08T00:00:01.000Z" },
    ]);
  });

  it("drops malformed entries fail-closed while keeping valid ones", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [],
      edges: [],
      islands: [],
      contradictionSignalDecisions: [
        { signatureKey: "C001:x", status: "accepted", decidedAt: "2026-07-08T00:00:00.000Z" },
        { signatureKey: "", status: "accepted", decidedAt: "2026-07-08T00:00:00.000Z" },
        { signatureKey: "C002:y", status: "proposed", decidedAt: "2026-07-08T00:00:00.000Z" },
        { signatureKey: "C003:z", status: "accepted" },
        "bogus",
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.contradictionSignalDecisions).toEqual([
      { signatureKey: "C001:x", status: "accepted", decidedAt: "2026-07-08T00:00:00.000Z" },
    ]);
  });

  it("omits the field entirely when every entry is malformed (matches undefined default)", () => {
    const result = validateAndUpgradeImportedDocument({
      ...baseDoc,
      cards: [],
      edges: [],
      islands: [],
      contradictionSignalDecisions: [{ signatureKey: "", status: "unknown-status", decidedAt: 1 }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.contradictionSignalDecisions).toBeUndefined();
  });

  it("strict mode accepts valid decisions and rejects an invalid status", () => {
    const valid = validateDocumentV2Strict({
      ...baseDoc,
      cards: [],
      edges: [],
      islands: [],
      contradictionSignalDecisions: [{ signatureKey: "C001:x", status: "held", decidedAt: "2026-07-08T00:00:00.000Z" }],
    });
    expect(valid.ok).toBe(true);

    const invalid = validateDocumentV2Strict({
      ...baseDoc,
      cards: [],
      edges: [],
      islands: [],
      contradictionSignalDecisions: [{ signatureKey: "C001:x", status: "proposed", decidedAt: "2026-07-08T00:00:00.000Z" }],
    });
    expect(invalid.ok).toBe(false);
    if (invalid.ok) return;
    expect(invalid.errors.join("\n")).toContain("contradictionSignalDecisions[0].status");
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
