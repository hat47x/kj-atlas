import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { buildMergeItemsIncremental } from "./merge_items";
import { createCancelableTaskRunner } from "../utils/compute_scheduler";

function makeDoc(prefix: string): DocumentV2 {
  return {
    id: prefix,
    title: prefix,
    cards: Array.from({ length: 20 }, (_, i) => ({ id: `${prefix}-c${i}`, text: `t${i}`, x: 0, y: 0 })),
    islands: [{ id: `${prefix}-i`, title: "is", cardIds: [] }],
    edges: [],
    evidenceLinks: [],
    updatedAt: "2026-01-01T00:00:00.000Z",
  };
}

describe("buildMergeItemsIncremental", () => {
  it("can be cancelled and rerun", async () => {
    const base = makeDoc("a");
    const incoming = makeDoc("b");
    const runner = createCancelableTaskRunner();
    const p = runner.run((ctx) => buildMergeItemsIncremental(base, incoming, ctx));
    runner.cancel();
    const cancelled = await p;
    expect(cancelled.status).toBe("cancelled");

    const rerun = await runner.run((ctx) => buildMergeItemsIncremental(base, incoming, ctx));
    expect(rerun.status).toBe("completed");
  });
});
