import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "./types";
import { parseInquiryBundleJson, serializeInquiryBundle } from "./inquiry_bundle_io";
import {
  buildInquiryResumeBrief,
  compareInquiryRounds,
  inquiryBundleOriginatesFromDocument,
  recordInquiryRound,
  startInquiryJourney,
  traceInquiryCardLineage,
} from "./inquiry_journey_session";
import { createRepresentativeInquiryBundle } from "./inquiry_journey.fixture";

const CREATED_AT = "2026-07-18T00:00:00.000Z";

function createDocument(cards: DocumentV1["cards"]): DocumentV1 {
  return {
    version: 1,
    id: "doc-inquiry",
    title: "窓口で迷う理由を探る",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands: [],
  };
}

function sequentialIds(): () => string {
  let value = 0;
  return () => String(++value);
}

describe("inquiry journey session", () => {
  it("builds a resume brief from recorded handoff data without changing snapshots", () => {
    const bundle = createRepresentativeInquiryBundle();
    const before = structuredClone(bundle);
    const result = buildInquiryResumeBrief(bundle);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.brief.question).toBe("案内を読んだ後にも残る不明点は何か");
    expect(result.brief.unresolvedQuestions).toEqual(["表示内容と職員説明のどちらが行動判断に影響したか"]);
    expect(result.brief.nextActions).toEqual(["質問した来庁者は案内表示をどこまで読んだか"]);
    expect(result.brief.previousResults).toHaveLength(1);
    expect(result.brief.previousResults[0]).toMatchObject({
      roundId: "round-r3-1",
      stage: "r3_essence_pursuit",
      iteration: 1,
      snapshotId: "snapshot-r3-1",
    });
    expect(result.brief.previousResults[0].cards.some((card) => card.id === "hypothesis-1")).toBe(true);
    expect(bundle).toEqual(before);
    expect(buildInquiryResumeBrief(bundle, "missing")).toEqual({ ok: false, reason: "round_not_found" });
  });

  it("traces a derived card through its source cards and owning rounds", () => {
    const bundle = createRepresentativeInquiryBundle();
    const traced = traceInquiryCardLineage(bundle, {
      snapshotId: "snapshot-r3-1",
      cardId: "hypothesis-1",
    });

    expect(traced.ok).toBe(true);
    if (!traced.ok) return;
    expect(traced.target.round).toMatchObject({ stage: "r3_essence_pursuit", iteration: 1 });
    expect(traced.ancestors.map((node) => [node.address.snapshotId, node.address.cardId, node.viaKind])).toEqual([
      ["snapshot-r2-1", "observation-1", "derived"],
      ["snapshot-r2-1", "information-gap-1", "derived"],
      ["snapshot-origin", "observation-1", "carried"],
    ]);
    expect(traceInquiryCardLineage(bundle, { snapshotId: "missing", cardId: "missing" })).toEqual({
      ok: false,
      reason: "card_not_found",
    });
  });

  it("starts from the current document without changing it and roundtrips strictly", async () => {
    const document = createDocument([{ id: "card-1", text: "同じ質問が繰り返された", x: 0, y: 0 }]);
    const source = structuredClone(document);
    const bundle = await startInquiryJourney(document, { idFactory: sequentialIds(), now: () => CREATED_AT });

    expect(document).toEqual(source);
    expect(bundle.journey.originSnapshotIds).toEqual(["snapshot-1"]);
    expect(bundle.journey.roundRecords).toEqual([]);
    expect(inquiryBundleOriginatesFromDocument(bundle, document.id)).toBe(true);
    expect(inquiryBundleOriginatesFromDocument(bundle, "another-document")).toBe(false);

    const serialized = await serializeInquiryBundle(bundle);
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    expect(await parseInquiryBundleJson(serialized.json)).toEqual({ ok: true, bundle: serialized.bundle });
  });

  it("records repeated stages as separate immutable snapshots and derives low-burden lineage", async () => {
    const ids = sequentialIds();
    const original = createDocument([
      { id: "card-1", text: "案内を見たかは未確認", x: 0, y: 0 },
      { id: "card-retired", text: "混雑だけが原因かもしれない", x: 100, y: 0 },
    ]);
    const started = await startInquiryJourney(original, { idFactory: ids, now: () => CREATED_AT });
    const changed = createDocument([
      { id: "card-1", text: "案内を見たが質問した", x: 20, y: 0 },
      { id: "card-new", text: "次の行動が分からない", x: 100, y: 0 },
    ]);

    const first = await recordInquiryRound(started, changed, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:01:00.000Z",
    });
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    const second = await recordInquiryRound(first.bundle, changed, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:02:00.000Z",
    });
    expect(second.ok).toBe(true);
    if (!second.ok) return;

    expect(second.bundle.journey.roundRecords.map((round) => [round.stage, round.iteration])).toEqual([
      ["r2_situation_grasp", 1],
      ["r2_situation_grasp", 2],
    ]);
    expect(second.bundle.snapshots).toHaveLength(3);
    expect(second.bundle.snapshots[0].document.cards[0].text).toBe("案内を見たかは未確認");
    expect(first.bundle.cardLineage.map((edge) => edge.kind)).toEqual(["edited", "new", "retired"]);
    expect(second.bundle.cardLineage.slice(3).map((edge) => edge.kind)).toEqual(["carried", "carried"]);

    const serialized = await serializeInquiryBundle(second.bundle);
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    expect((await parseInquiryBundleJson(serialized.json)).ok).toBe(true);
  });

  it("compares two recorded outputs without changing either snapshot", async () => {
    const ids = sequentialIds();
    const original = createDocument([{ id: "card-1", text: "案内を見た", x: 0, y: 0 }]);
    const started = await startInquiryJourney(original, { idFactory: ids, now: () => CREATED_AT });
    const first = await recordInquiryRound(started, original, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:01:00.000Z",
    });
    expect(first.ok).toBe(true);
    if (!first.ok) return;

    const revised = createDocument([
      { id: "card-1", text: "案内を見たが迷った", x: 0, y: 0 },
      { id: "card-2", text: "次の行動が分からない", x: 100, y: 0 },
    ]);
    revised.readingOrder = ["card-2", "card-1"];
    const second = await recordInquiryRound(first.bundle, revised, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:02:00.000Z",
    });
    expect(second.ok).toBe(true);
    if (!second.ok) return;

    const before = structuredClone(second.bundle.snapshots);
    const [fromRound, toRound] = second.bundle.journey.roundRecords;
    const comparison = compareInquiryRounds(second.bundle, fromRound.roundId, toRound.roundId);

    expect(comparison).toEqual({
      ok: true,
      summary: {
        cards: 2,
        islands: 0,
        relationSummaries: 0,
        readingOrderChanged: true,
      },
    });
    expect(second.bundle.snapshots).toEqual(before);
    expect(compareInquiryRounds(second.bundle, "missing", toRound.roundId)).toEqual({
      ok: false,
      reason: "round_not_found",
    });
  });

  it("branches from a historical round without replacing the existing descendant", async () => {
    const ids = sequentialIds();
    const original = createDocument([{ id: "card-1", text: "受付で迷った", x: 0, y: 0 }]);
    const started = await startInquiryJourney(original, { idFactory: ids, now: () => CREATED_AT });
    const situation = await recordInquiryRound(started, original, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:01:00.000Z",
    });
    expect(situation.ok).toBe(true);
    if (!situation.ok) return;
    const situationRoundId = situation.bundle.journey.roundRecords[0].roundId;

    const essence = await recordInquiryRound(situation.bundle, original, "r3_essence_pursuit", {
      idFactory: ids,
      now: () => "2026-07-18T00:02:00.000Z",
    });
    expect(essence.ok).toBe(true);
    if (!essence.ok) return;
    const essenceRoundId = essence.bundle.journey.roundRecords[1].roundId;
    const snapshotsBeforeBranch = structuredClone(essence.bundle.snapshots);

    const branchedDocument = createDocument([
      { id: "card-1", text: "受付で迷った", x: 0, y: 0 },
      { id: "card-fieldwork", text: "案内表示の見え方を再確認する", x: 100, y: 0 },
    ]);
    const branch = await recordInquiryRound(essence.bundle, branchedDocument, "r2_situation_grasp", {
      idFactory: ids,
      now: () => "2026-07-18T00:03:00.000Z",
      parentRoundId: situationRoundId,
    });
    expect(branch.ok).toBe(true);
    if (!branch.ok) return;

    const branchRound = branch.bundle.journey.roundRecords[2];
    expect(branchRound.parentRoundIds).toEqual([situationRoundId]);
    expect(branchRound.iteration).toBe(2);
    expect(branch.bundle.journey.headRoundIds).toEqual([essenceRoundId, branchRound.roundId]);
    expect(branch.bundle.journey.defaultHeadRoundId).toBe(branchRound.roundId);
    expect(branch.bundle.snapshots.slice(0, snapshotsBeforeBranch.length)).toEqual(snapshotsBeforeBranch);
    expect(await recordInquiryRound(branch.bundle, branchedDocument, "r2_situation_grasp", {
      parentRoundId: "missing-round",
    })).toEqual({ ok: false, reason: "invalid_round" });
  });
});
