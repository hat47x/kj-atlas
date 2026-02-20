import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { buildMergeItems } from "./merge_items";
import { applySelectedMergeItemsAtomic, preflightMerge } from "./merge_apply";

const FIXTURE_ROOT = resolve(__dirname, "../../tests/fixtures/review-selective-merge");

function loadFixture(name: string): DocumentV2 {
  return JSON.parse(readFileSync(resolve(FIXTURE_ROOT, name), "utf8")) as DocumentV2;
}

describe("review diff selective merge fixtures", () => {
  it("applies evidence.add and preserves resulting evidence link", () => {
    const base = loadFixture("evidence-add.base.json");
    const incoming = loadFixture("evidence-add.incoming.json");
    const evidenceItem = buildMergeItems(base, incoming).find((item) => item.kind === "evidence.add" && item.entityRef.id === "e1");

    expect(evidenceItem).toBeDefined();
    const result = applySelectedMergeItemsAtomic(base, base, incoming, evidenceItem ? [evidenceItem] : []);
    expect(result.ok).toBe(true);

    if (result.ok) {
      expect((result.document.evidenceLinks ?? []).some((link) => link.id === "e1" && link.type === "supports")).toBe(true);
    }
  });

  it("applies claimType unknown -> fact from selected card.field change", () => {
    const base = loadFixture("claim-type.base.json");
    const incoming = loadFixture("claim-type.incoming.json");
    const claimTypeItem = buildMergeItems(base, incoming).find(
      (item) => item.kind === "card.field" && item.entityRef.id === "c1" && item.field === "claimType"
    );

    expect(claimTypeItem).toBeDefined();
    const result = applySelectedMergeItemsAtomic(base, base, incoming, claimTypeItem ? [claimTypeItem] : []);
    expect(result.ok).toBe(true);

    if (result.ok) {
      expect(result.document.cards.find((card) => card.id === "c1")?.claimType).toBe("fact");
    }
  });

  it("blocks dangling evidence during preflight with V/P error and leaves document unchanged", () => {
    const base = loadFixture("dangling-evidence.base.json");
    const incoming = loadFixture("dangling-evidence.incoming.json");
    const selected = buildMergeItems(base, incoming).filter((item) => item.kind === "evidence.add");
    const before = JSON.stringify(base);

    const preflight = preflightMerge(base, selected, incoming);
    expect(preflight.ok).toBe(false);
    if (!preflight.ok) {
      expect(preflight.errors.some((error) => error.code === "SCHEMA:incoming")).toBe(true);
      expect(preflight.errors.some((error) => error.message.includes("[V004]") || error.message.includes("[V005]"))).toBe(true);
    }

    const result = applySelectedMergeItemsAtomic(base, base, incoming, selected);
    expect(result.ok).toBe(false);
    expect(JSON.stringify(base)).toBe(before);
  });
});
