import { describe, expect, it } from "vitest";

import { applyHilRsRediffPayload } from "./hil_rs_apply";
import { createHilRsClient } from "./hil_rs_client";
import { HIL_RS_CRITIQUE_SCHEMA_VERSION, type HilRsCritiqueInput } from "./hil_rs_contract";
import type { DocumentV2 } from "./types";

const CURRENT: DocumentV2 = {
  id: "doc-current",
  version: 2,
  title: "current",
  createdAt: "2026-05-10T00:00:00.000Z",
  updatedAt: "2026-05-10T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "alpha", x: 0, y: 0 },
    { id: "c2", text: "beta", x: 100, y: 50 },
  ],
  islands: [],
  edges: [],
};

const SUGGESTED: DocumentV2 = {
  ...CURRENT,
  cards: [
    { id: "c1", text: "alpha (edited)", x: 10, y: 15 },
    { id: "c2", text: "beta", x: 100, y: 50 },
    { id: "c3", text: "gamma", x: 230, y: 70 },
  ],
};

describe("hil_rs_client_apply integration", () => {
  it("applies validated rediff payload end-to-end", () => {
    const client = createHilRsClient();
    const critiqueInputs: HilRsCritiqueInput[] = [{
      schemaVersion: HIL_RS_CRITIQUE_SCHEMA_VERSION,
      critiqueId: "crit-1",
      targetRef: "card:c1",
      critiqueType: "feels_off",
      createdAt: "2026-05-10T00:00:00.000Z",
      iteration: 3,
    }];

    const payload = client.previewRediff({
      currentDocument: CURRENT,
      suggestedDocument: SUGGESTED,
      suggestionId: "sg-hil-rs-int-01",
      iteration: 3,
      critiqueInputs,
    });

    expect(payload).not.toBeNull();
    const result = applyHilRsRediffPayload(CURRENT, payload!);
    expect(result.appliedOpIds.length).toBeGreaterThan(0);
    expect(result.skippedOpIds).toHaveLength(0);
    expect(result.document.cards).toHaveLength(3);
    expect(result.document.cards.find((card) => card.id === "c1")?.x).toBe(10);
    expect(result.document.cards.some((card) => card.x === 230 && card.y === 70)).toBe(true);
  });
});
