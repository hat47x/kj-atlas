import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { buildMergeItems } from "./merge_items";
import { applySelectedMergeItemsAtomic, preflightMerge } from "./merge_apply";
import evidenceAddBaseRaw from "../../tests/fixtures/review-selective-merge/evidence-add.base.json?raw";
import evidenceAddIncomingRaw from "../../tests/fixtures/review-selective-merge/evidence-add.incoming.json?raw";
import claimTypeBaseRaw from "../../tests/fixtures/review-selective-merge/claim-type.base.json?raw";
import claimTypeIncomingRaw from "../../tests/fixtures/review-selective-merge/claim-type.incoming.json?raw";
import danglingEvidenceBaseRaw from "../../tests/fixtures/review-selective-merge/dangling-evidence.base.json?raw";
import danglingEvidenceIncomingRaw from "../../tests/fixtures/review-selective-merge/dangling-evidence.incoming.json?raw";

const fixtureByName = {
  "evidence-add.base.json": evidenceAddBaseRaw,
  "evidence-add.incoming.json": evidenceAddIncomingRaw,
  "claim-type.base.json": claimTypeBaseRaw,
  "claim-type.incoming.json": claimTypeIncomingRaw,
  "dangling-evidence.base.json": danglingEvidenceBaseRaw,
  "dangling-evidence.incoming.json": danglingEvidenceIncomingRaw,
} as const;

type FixtureName = keyof typeof fixtureByName;

function loadFixture(name: FixtureName): DocumentV1 {
  return JSON.parse(fixtureByName[name]) as DocumentV1;
}

describe("review diff selective merge fixtures", () => {
  it("applies evidence.add and preserves resulting evidence link", () => {
    const base = loadFixture("evidence-add.base.json");
    const incoming = loadFixture("evidence-add.incoming.json");

    expect(base.cards).toHaveLength(2);

    const evidenceItem = buildMergeItems(base, incoming).find((item) => item.kind === "evidence.add" && item.entityRef.id === "e1");
    expect(evidenceItem).toBeDefined();

    const result = applySelectedMergeItemsAtomic(base, base, incoming, [evidenceItem!]);
    expect(result.ok).toBe(true);

    if (result.ok) {
      expect(result.document.evidenceLinks).toEqual([
        { id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" },
      ]);
    }
  });

  it("applies claimType unknown -> fact from selected card.field change", () => {
    const base = loadFixture("claim-type.base.json");
    const incoming = loadFixture("claim-type.incoming.json");

    expect(base.cards.find((card) => card.id === "c1")?.claimType).toBe("unknown");

    const claimTypeItem = buildMergeItems(base, incoming).find(
      (item) => item.kind === "card.field" && item.entityRef.id === "c1" && item.field === "claimType"
    );
    expect(claimTypeItem).toBeDefined();

    const result = applySelectedMergeItemsAtomic(base, base, incoming, [claimTypeItem!]);
    expect(result.ok).toBe(true);

    if (result.ok) {
      expect(result.document.cards.find((card) => card.id === "c1")?.claimType).toBe("fact");
    }
  });

  it("blocks dangling evidence during preflight with V/P error and leaves document unchanged", () => {
    const base = loadFixture("dangling-evidence.base.json");
    const incoming = loadFixture("dangling-evidence.incoming.json");
    const selected = buildMergeItems(base, incoming).filter((item) => item.kind === "evidence.add");
    const before = loadFixture("dangling-evidence.base.json");

    const preflight = preflightMerge(base, selected, incoming);
    expect(preflight.ok).toBe(false);
    if (!preflight.ok) {
      expect(preflight.errors).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ code: "SCHEMA:incoming" }),
          expect.objectContaining({ code: "SCHEMA:incoming", message: expect.stringContaining("[V005] evidenceLinks[0].toCardId") }),
        ])
      );
    }

    const result = applySelectedMergeItemsAtomic(base, base, incoming, selected);
    expect(result.ok).toBe(false);
    expect(base).toEqual(before);
  });
});
