import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "./types";
import { parseInquiryBundleJson, serializeInquiryBundle } from "./inquiry_bundle_io";
import {
  inquiryBundleOriginatesFromDocument,
  recordInquiryRound,
  startInquiryJourney,
} from "./inquiry_journey_session";

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
});
