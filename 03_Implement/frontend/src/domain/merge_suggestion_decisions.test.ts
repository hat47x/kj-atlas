import { describe, expect, it } from "vitest";

import {
  appendMergeSuggestionDecision,
  getLatestMergeSuggestionDecisionByGroup,
  listMergeSuggestionDecisionsByGroup,
  restoreMergeSuggestionDecisionsBySnapshot,
} from "./merge_suggestion_decisions";
import type { DocumentV1 } from "./types";

function createBaseDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "alpha", x: 0, y: 0 },
      { id: "c2", text: "Alpha", x: 100, y: 0 },
      { id: "c3", text: "Alpha context", x: 200, y: 0 },
    ],
    edges: [],
    islands: [],
  };
}

describe("merge_suggestion_decisions", () => {
  it("keeps append order accept->partial->reject->defer and restores same order for contract snapshot", () => {
    const base = createBaseDocument();
    const appends: Array<{ id: string; decision: "accept" | "partial" | "reject" | "defer"; editedText: string }> = [
      { id: "d1", decision: "accept", editedText: "alpha accept" },
      { id: "d2", decision: "partial", editedText: "alpha partial" },
      { id: "d3", decision: "reject", editedText: "alpha reject" },
      { id: "d4", decision: "defer", editedText: "alpha defer" },
    ];

    const updated = appends.reduce<DocumentV1>((doc, append, index) => {
      const next = appendMergeSuggestionDecision(
        doc,
        {
          groupId: "g1",
          decision: append.decision,
          cardIds: append.decision === "partial" ? ["c1", "c2", "c3"] : ["c1", "c2"],
          selectedCardIds: append.decision === "partial" ? ["c1", "c2"] : undefined,
          mergedTextDraft: "alpha",
          editedText: append.editedText,
        },
        {
          idFactory: () => append.id,
          now: `2026-01-0${index + 2}T00:00:00.000Z`,
        }
      );

      // R3-tier-1: every append now snapshots a representative/source resolution
      // (fallback here — c1/c2 have no repOf/mergedIntoCardId/sources of their own).
      expect(next.mergeSuggestionDecisions?.at(-1)).toMatchObject({
        representativeCardId: "c1",
        representativeResolvedBy: "fallback",
      });
      return next;
    }, base);

    const restored = restoreMergeSuggestionDecisionsBySnapshot(updated.mergeSuggestionDecisions, "CTR-2B-02-DECISION-LOG-V1");
    expect(restored.map((entry) => entry.action)).toEqual(["accept", "partial", "reject", "defer"]);
    expect(restored.map((entry) => entry.id)).toEqual(["d1", "d2", "d3", "d4"]);
  });

  it("appends decision entries with deterministic card id ordering", () => {
    const result = appendMergeSuggestionDecision(
      createBaseDocument(),
      {
        groupId: "g1",
        decision: "accept",
        cardIds: ["c2", "c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha canonical",
        decisionReason: "Human-reviewed: normalize duplicates",
      },
      { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
    );

    expect(result.mergeSuggestionDecisions).toEqual([
      {
        id: "d1",
        decisionId: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        decidedBy: "human",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha canonical",
        note: "Human-reviewed: normalize duplicates",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        rationale: undefined,
        representativeCardId: "c1",
        representativeResolvedBy: "fallback",
        sourceCardIds: ["c2"],
        missingSourceCardIds: [],
      },
    ]);
  });

  it("records a valid partial decision with a strict selected subset", () => {
    const result = appendMergeSuggestionDecision(
      createBaseDocument(),
      {
        groupId: "g-partial",
        decision: "partial",
        cardIds: ["c3", "c1", "c2"],
        selectedCardIds: ["c2", "c1"],
        mergedTextDraft: "alpha",
        editedText: "alpha partial",
      },
      { idFactory: () => "d-partial", now: "2026-01-02T00:00:00.000Z" },
    );

    expect(result.mergeSuggestionDecisions?.at(-1)).toMatchObject({
      decision: "partial",
      cardIds: ["c1", "c2", "c3"],
      selectedCardIds: ["c1", "c2"],
      representativeCardId: "c1",
    });
  });

  it("rejects partial decisions without a true subset", () => {
    const base = createBaseDocument();
    const common = {
      groupId: "g-partial",
      decision: "partial" as const,
      cardIds: ["c1", "c2", "c3"],
      mergedTextDraft: "alpha",
      editedText: "alpha partial",
    };

    expect(() => appendMergeSuggestionDecision(base, common)).toThrowError("partial decision requires selectedCardIds");
    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1"] })).toThrowError(
      "partial selectedCardIds must contain at least two ids",
    );
    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1", "c2", "c3"] })).toThrowError(
      "partial selectedCardIds must be a strict subset of cardIds",
    );
    expect(() => appendMergeSuggestionDecision(base, { ...common, selectedCardIds: ["c1", "outside"] })).toThrowError(
      "partial selectedCardIds must be a subset of cardIds",
    );
  });

  it("returns latest decision per group", () => {
    const decisions: DocumentV1["mergeSuggestionDecisions"] = [
      {
        id: "d1",
        groupId: "g1",
        decision: "defer",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
      },
      {
        id: "d2",
        groupId: "g1",
        decision: "partial",
        decidedAt: "2026-01-03T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha partial",
      },
      {
        id: "d3",
        groupId: "g2",
        decision: "reject",
        decidedAt: "2026-01-01T00:00:00.000Z",
        cardIds: ["c3", "c4"],
        mergedTextDraft: "beta",
        editedText: "beta",
      },
    ];

    const latest = getLatestMergeSuggestionDecisionByGroup(decisions);

    expect(latest.get("g1")?.id).toBe("d2");
    expect(latest.get("g2")?.id).toBe("d3");
  });

  it("fails fast when groupId is empty", () => {
    expect(() =>
      appendMergeSuggestionDecision(
        createBaseDocument(),
        {
          groupId: "   ",
          decision: "accept",
          cardIds: ["c1"],
          mergedTextDraft: "alpha",
          editedText: "alpha",
        },
        { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
      )
    ).toThrowError("groupId must be a non-empty string");
  });

  it("fails fast when cardIds are empty after normalization", () => {
    expect(() =>
      appendMergeSuggestionDecision(
        createBaseDocument(),
        {
          groupId: "g1",
          decision: "accept",
          cardIds: [],
          mergedTextDraft: "alpha",
          editedText: "alpha",
        },
        { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
      )
    ).toThrowError("cardIds must contain at least one id");
  });

  it("fails fast when editedText is empty", () => {
    expect(() =>
      appendMergeSuggestionDecision(
        createBaseDocument(),
        {
          groupId: "g1",
          decision: "partial",
          cardIds: ["c1"],
          mergedTextDraft: "alpha",
          editedText: " ",
        },
        { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
      )
    ).toThrowError("editedText must be a non-empty string");
  });

  it("fails fast when decision is outside contract enum", () => {
    expect(() =>
      appendMergeSuggestionDecision(
        createBaseDocument(),
        {
          groupId: "g1",
          decision: "accept-ish" as unknown as "accept",
          cardIds: ["c1"],
          mergedTextDraft: "alpha",
          editedText: "alpha",
        },
        { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
      )
    ).toThrowError("decision must be one of accept|partial|reject|defer");
  });

  it("lists decision history by group without auto-confirming representative merge", () => {
    const decisions: DocumentV1["mergeSuggestionDecisions"] = [
      {
        id: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d2",
        groupId: "g1",
        decision: "defer",
        action: "defer",
        decidedAt: "2026-01-03T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1"],
        mergedTextDraft: "alpha",
        editedText: "alpha pending",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d3",
        groupId: "g2",
        decision: "reject",
        action: "reject",
        decidedAt: "2026-01-04T00:00:00.000Z",
        cardIds: ["c3", "c4"],
        selectedCardIds: ["c3", "c4"],
        mergedTextDraft: "beta",
        editedText: "beta",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      },
    ];

    expect(listMergeSuggestionDecisionsByGroup(decisions, "g1").map((entry) => entry.id)).toEqual(["d1", "d2"]);
  });

  it("restores only contract-valid actions for a given snapshot version", () => {
    const decisions: DocumentV1["mergeSuggestionDecisions"] = [
      {
        id: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d2",
        groupId: "g1",
        decision: "partial",
        action: "partial",
        decidedAt: "2026-01-03T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1"],
        mergedTextDraft: "alpha",
        editedText: "alpha pending",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d3",
        groupId: "g1",
        decision: "reject",
        action: "invalid" as unknown as "reject",
        decidedAt: "2026-01-04T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha no",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "system",
      },
      {
        id: "d4",
        groupId: "g1",
        decision: "defer",
        action: "defer",
        decidedAt: "2026-01-05T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha defer",
        snapshotVersion: "OTHER-SNAPSHOT",
      },
    ];

    expect(restoreMergeSuggestionDecisionsBySnapshot(decisions, "CTR-2B-02-DECISION-LOG-V1").map((entry) => entry.id)).toEqual([
      "d1",
      "d2",
    ]);
  });

  it("restores entries in append order without re-sorting by timestamps", () => {
    const decisions: DocumentV1["mergeSuggestionDecisions"] = [
      {
        id: "d2",
        groupId: "g1",
        decision: "partial",
        action: "partial",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
      {
        id: "d0",
        groupId: "g1",
        decision: "defer",
        action: "defer",
        decidedAt: "2026-01-01T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        decidedBy: "human",
      },
    ];

    expect(restoreMergeSuggestionDecisionsBySnapshot(decisions, "CTR-2B-02-DECISION-LOG-V1").map((entry) => entry.id)).toEqual([
      "d2",
      "d1",
      "d0",
    ]);
  });

  it("fails fast when restore is requested with an undefined snapshot contract", () => {
    expect(() =>
      restoreMergeSuggestionDecisionsBySnapshot([], "CTR-2B-02-DECISION-LOG-V2")
    ).toThrowError(
      "snapshotVersion must match CTR-2B-02-DECISION-LOG-V1; contract deviations must be routed to A1"
    );
  });
});
