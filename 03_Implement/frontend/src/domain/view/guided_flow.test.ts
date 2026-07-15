import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { buildDefaultGuidedFlowSteps } from "./guided_flow";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-claim", text: "claim", x: 0, y: 0, claimType: "claim" },
      { id: "c-fact", text: "fact", x: 10, y: 0, claimType: "fact" },
      { id: "c-hypo", text: "hypothesis", x: 20, y: 0, claimType: "hypothesis" },
      { id: "c-unknown", text: "unknown", x: 30, y: 0, claimType: "unknown" },
      { id: "c-unknown-2", text: "unknown 2", x: 40, y: 0 },
    ],
    edges: [],
    islands: [
      { id: "i-reviewed", cardIds: ["c-fact"], summaryReviewed: true },
      { id: "i-unreviewed", cardIds: ["c-claim"], summaryReviewed: false },
    ],
    evidenceLinks: [
      { id: "ev1", type: "supports", fromCardId: "c-fact", toCardId: "c-claim" },
    ],
  };
}

describe("guided flow", () => {
  it("orders review targets as unreviewed islands then unknown cards", () => {
    const steps = buildDefaultGuidedFlowSteps();
    const reviewStep = steps.find((step) => step.id === "review");
    expect(reviewStep).toBeDefined();

    const targets = reviewStep?.targetSelector(createDocument(), {
      guidedFlowEnabled: true,
      guidedFlowStepId: "review",
      guidedFlowTargetIndex: 0,
    });
    expect(targets).toEqual(["i-unreviewed", "c-unknown", "c-unknown-2"]);
  });

  it("uses evidence gap report for evidence step ordering", () => {
    const steps = buildDefaultGuidedFlowSteps({
      generatedAt: "2024-01-01T00:00:00.000Z",
      stats: {
        totalLinks: 0,
        supportsLinks: 0,
        contradictsLinks: 0,
        hypothesisCount: 0,
        claimCount: 0,
        factCount: 0,
        hypothesesWithNoFactSupport: 0,
        claimsWithNoFactSupport: 0,
        factsUnusedAsEvidence: 0,
        contradictionsWithoutCounterSupport: 0,
      },
      findings: [
        {
          severity: "warn",
          code: "E002",
          title: "Claim lacks fact support",
          detail: "",
          cardIds: ["c-claim"],
          suggestedAction: "",
        },
        {
          severity: "warn",
          code: "E001",
          title: "Hypothesis lacks fact support",
          detail: "",
          cardIds: ["c-hypo"],
          suggestedAction: "",
        },
      ],
    });

    const evidenceStep = steps.find((step) => step.id === "evidence");
    const targets = evidenceStep?.targetSelector(createDocument(), {
      guidedFlowEnabled: true,
      guidedFlowStepId: "evidence",
      guidedFlowTargetIndex: 0,
    });

    expect(targets).toEqual(["c-claim", "c-hypo"]);
  });
});
