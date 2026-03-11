import { describe, expect, it } from "vitest";

import fixtureRaw from "../../tests/fixtures/hil-rs/stub-client.base.json?raw";
import { createHilRsStubClient } from "./hil_rs_stub_client";
import type { DocumentV2 } from "./types";

const FIXTURE_DOC = JSON.parse(fixtureRaw) as DocumentV2;

describe("hil_rs_stub_client", () => {
  it("builds critique inputs from fixture without coupling to runtime API", () => {
    const client = createHilRsStubClient();

    const critiques = client.collectCritiqueInputs({
      document: FIXTURE_DOC,
      iteration: 3,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    expect(critiques).toHaveLength(2);
    expect(critiques.map((item) => item.targetRef)).toEqual(["card:c1", "island:i1"]);
  });

  it("produces reversible rediff preview from fixed fixture + suggestion", () => {
    const client = createHilRsStubClient();

    const critiques = client.collectCritiqueInputs({
      document: FIXTURE_DOC,
      iteration: 3,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    const suggestedDocument: DocumentV2 = {
      ...FIXTURE_DOC,
      cards: FIXTURE_DOC.cards.map((card) => (card.id === "c1" ? { ...card, x: 120, y: 140 } : card)),
      updatedAt: "2026-03-11T00:00:00.000Z",
    };

    const payload = client.previewRediff({
      currentDocument: FIXTURE_DOC,
      suggestedDocument,
      suggestionId: "suggestion-3",
      iteration: 3,
      critiqueInputs: critiques,
    });

    expect(payload).not.toBeNull();
    expect(payload?.basedOnIteration).toBe(3);
    expect(payload?.diffOps).toEqual([
      {
        opId: "op:move:c1",
        opType: "move",
        targetRef: "card:c1",
        before: { x: 0, y: 0 },
        after: { x: 120, y: 140 },
      },
    ]);
  });
});
