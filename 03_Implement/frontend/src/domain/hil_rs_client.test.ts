import { describe, expect, it, vi } from "vitest";

import { createHilRsClient, selectValidatedRediffPayload } from "./hil_rs_client";
import type { DocumentV1 } from "./types";

const BASE_DOCUMENT: DocumentV1 = {
  version: 1,
  id: "doc-1",
  title: "test-doc",
  createdAt: "2026-03-14T00:00:00.000Z",
  updatedAt: "2026-03-14T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    {
      id: "c1",
      text: "card",
      x: 0,
      y: 0,
      critique: "",
      critiqueTags: [],
      textReviewed: false,
      claimType: "fact",
    },
  ],
  islands: [],
  edges: [],
};


describe("hil_rs_client", () => {
  it("uses the stub output when provider is not specified", () => {
    const client = createHilRsClient();
    const critiqueInputs = client.collectCritiqueInputs({
      document: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], critique: "too close", critiqueTags: ["too_close"] }],
      },
      iteration: 1,
      createdAt: "2026-03-14T00:00:00.000Z",
    });

    const payload = client.previewRediff({
      currentDocument: BASE_DOCUMENT,
      suggestedDocument: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], x: 10 }],
      },
      suggestionId: "s1",
      iteration: 1,
      critiqueInputs,
    });

    expect(payload).not.toBeNull();
    expect(payload?.proposalId).toBe("s1");
  });

  it("uses provider payload when it satisfies A1-REDIFF-IF validation", () => {
    const provider = {
      proposeReDiff: vi.fn().mockImplementation((input) => ({ ...input, proposalId: `${input.proposalId}-provider` })),
    };

    const client = createHilRsClient({ rediffProvider: provider });

    const critiqueInputs = client.collectCritiqueInputs({
      document: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], critique: "too close", critiqueTags: ["too_close"] }],
      },
      iteration: 1,
      createdAt: "2026-03-14T00:00:00.000Z",
    });

    const payload = client.previewRediff({
      currentDocument: BASE_DOCUMENT,
      suggestedDocument: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], x: 10 }],
      },
      suggestionId: "s1",
      iteration: 1,
      critiqueInputs,
    });

    expect(provider.proposeReDiff).toHaveBeenCalledTimes(1);
    expect(payload?.proposalId).toBe("s1-provider");
  });


  it("selectValidatedRediffPayload returns draft when provider throws", () => {
    const provider = {
      proposeReDiff: vi.fn().mockImplementation(() => {
        throw new Error("provider unavailable");
      }),
    };

    const client = createHilRsClient();
    const critiqueInputs = client.collectCritiqueInputs({
      document: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], critique: "too close", critiqueTags: ["too_close"] }],
      },
      iteration: 1,
      createdAt: "2026-03-14T00:00:00.000Z",
    });

    const draftPayload = client.previewRediff({
      currentDocument: BASE_DOCUMENT,
      suggestedDocument: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], x: 10 }],
      },
      suggestionId: "s1",
      iteration: 1,
      critiqueInputs,
    });

    expect(draftPayload).not.toBeNull();
    const payload = selectValidatedRediffPayload(draftPayload!, provider);
    expect(provider.proposeReDiff).toHaveBeenCalledTimes(1);
    expect(payload.proposalId).toBe("s1");
  });

  it("falls back to stub payload when provider returns an invalid payload", () => {
    const provider = {
      proposeReDiff: vi.fn().mockReturnValue({ schemaVersion: "1.0.0", proposalId: "", basedOnIteration: 1, diffOps: [], traceKey: "" }),
    };

    const client = createHilRsClient({ rediffProvider: provider });

    const critiqueInputs = client.collectCritiqueInputs({
      document: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], critique: "too close", critiqueTags: ["too_close"] }],
      },
      iteration: 1,
      createdAt: "2026-03-14T00:00:00.000Z",
    });

    const payload = client.previewRediff({
      currentDocument: BASE_DOCUMENT,
      suggestedDocument: {
        ...BASE_DOCUMENT,
        cards: [{ ...BASE_DOCUMENT.cards[0], x: 10 }],
      },
      suggestionId: "s1",
      iteration: 1,
      critiqueInputs,
    });

    expect(provider.proposeReDiff).toHaveBeenCalledTimes(1);
    expect(payload).not.toBeNull();
    expect(payload?.proposalId).toBe("s1");
  });
});
