import { describe, expect, it } from "vitest";

import fixtureRaw from "../../tests/fixtures/hil-rs/stub-client.base.json?raw";
import {
  HIL_RS_CONTRACT_IDS,
  HIL_RS_CRITIQUE_REQUIRED_FIELDS,
  HIL_RS_CRITIQUE_SCHEMA_VERSION,
  HIL_RS_REDIFF_SCHEMA_VERSION,
  HIL_RS_REVIEW_AUDIT_FIELDS,
  HIL_RS_REVIEW_ATTRIBUTION_SCHEMA_VERSION,
  validateHilRsCritiqueInput,
  validateHilRsRediffPayload,
} from "./hil_rs_contract";
import { createHilRsStubClient } from "./hil_rs_stub_client";
import type { DocumentV1 } from "./types";

const FIXTURE_DOC = JSON.parse(fixtureRaw) as DocumentV1;

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

  it("Phase2(A2) mock validation: fixture/stub payload keeps fixed contract signature", () => {
    const client = createHilRsStubClient();

    const critiques = client.collectCritiqueInputs({
      document: FIXTURE_DOC,
      iteration: 3,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    expect(HIL_RS_CONTRACT_IDS).toEqual({
      critique: "A1-CRITIQUE-IF",
      rediff: "A1-REDIFF-IF",
      attribution: "A1-ATTR-IF",
      error: "A1-ERROR-IF",
    });
    expect(HIL_RS_CRITIQUE_SCHEMA_VERSION).toBe("1.0.0");
    expect(HIL_RS_REDIFF_SCHEMA_VERSION).toBe("1.0.0");
    expect(HIL_RS_REVIEW_ATTRIBUTION_SCHEMA_VERSION).toBe("1.0.0");
    expect([...HIL_RS_CRITIQUE_REQUIRED_FIELDS]).toEqual([
      "critiqueId",
      "targetRef",
      "critiqueType",
      "createdAt",
      "iteration",
    ]);
    expect([...HIL_RS_REVIEW_AUDIT_FIELDS]).toEqual(["reviewState", "reviewedAt", "reviewerRef", "auditRecordedAt"]);

    for (const critique of critiques) {
      expect(validateHilRsCritiqueInput(critique)).toBe(true);
      expect(critique.schemaVersion).toBe(HIL_RS_CRITIQUE_SCHEMA_VERSION);
      expect(Object.keys(critique).sort()).toEqual(
        Object.keys(critique)
          .filter((key) =>
            [
              "schemaVersion",
              "critiqueId",
              "targetRef",
              "critiqueType",
              "createdAt",
              "iteration",
              "comment",
              "constraintHints",
            ].includes(key),
          )
          .sort(),
      );
    }

    const suggestedDocument: DocumentV1 = {
      ...FIXTURE_DOC,
      cards: FIXTURE_DOC.cards.map((card) => (card.id === "c1" ? { ...card, x: 120, y: 140 } : card)),
      updatedAt: "2026-03-11T00:00:00.000Z",
    };
    const rediff = client.previewRediff({
      currentDocument: FIXTURE_DOC,
      suggestedDocument,
      suggestionId: "suggestion-3",
      iteration: 3,
      critiqueInputs: critiques,
    });

    expect(rediff).not.toBeNull();
    expect(validateHilRsRediffPayload(rediff)).toBe(true);
  });

  it("produces reversible rediff preview from fixed fixture + suggestion", () => {
    const client = createHilRsStubClient();

    const critiques = client.collectCritiqueInputs({
      document: FIXTURE_DOC,
      iteration: 3,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    const suggestedDocument: DocumentV1 = {
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
    expect(payload?.schemaVersion).toBe("1.0.0");
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
