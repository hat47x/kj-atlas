import { describe, expect, it } from "vitest";

import { ACTIVE_CARD_LABEL_PRIORITY, cullLabels, LABEL_PRIORITIES, type LabelItem } from "./label_culling";

function item(id: string, priority: number, x: number): LabelItem {
  return {
    id,
    kind: "card",
    priority,
    rect: { x, y: 0, w: 40, h: 20 },
    payload: {},
  };
}

describe("cullLabels", () => {
  it("keeps higher-priority labels when overlapping", () => {
    const result = cullLabels([
      {
        id: "island-title",
        kind: "islandTitle",
        priority: LABEL_PRIORITIES.islandTitle,
        rect: { x: 0, y: 0, w: 80, h: 20 },
        payload: { islandId: "i1" },
      },
      {
        id: "card-label",
        kind: "card",
        priority: LABEL_PRIORITIES.card,
        rect: { x: 4, y: 2, w: 80, h: 20 },
        payload: { cardId: "c1" },
      },
    ]);

    expect(result.accepted.map((label) => label.id)).toEqual(["island-title"]);
    expect(result.acceptedIds.has("card-label")).toBe(false);
  });

  it("is deterministic for equal-priority collisions via id tie-break", () => {
    const a = item("b", 10, 0);
    const b = item("a", 10, 0);

    const result = cullLabels([a, b]);
    expect(result.accepted.map((label) => label.id)).toEqual(["a"]);
  });

  it("keeps non-overlapping labels", () => {
    const result = cullLabels([item("a", 10, 0), item("b", 10, 60)]);
    expect(result.accepted.map((label) => label.id)).toEqual(["a", "b"]);
  });

  // QA-MONKEY-10: an actively worked-on card must beat overlapping plain
  // cards regardless of id ordering (ids embed random UUIDs, so without the
  // boost the winner alternated nondeterministically between runs).
  it("keeps the active card over overlapping plain cards regardless of id order", () => {
    const result = cullLabels([
      item("card:aaaa:label", LABEL_PRIORITIES.card, 0),
      item("card:zzzz:label", ACTIVE_CARD_LABEL_PRIORITY, 0),
    ]);

    expect(result.accepted.map((label) => label.id)).toEqual(["card:zzzz:label"]);
  });

  it("keeps island title and unreviewed badge over the active card when overlapping", () => {
    const result = cullLabels([
      item("card:active:label", ACTIVE_CARD_LABEL_PRIORITY, 0),
      {
        id: "island-title",
        kind: "islandTitle",
        priority: LABEL_PRIORITIES.islandTitle,
        rect: { x: 0, y: 0, w: 40, h: 20 },
        payload: { islandId: "i1" },
      },
    ]);

    expect(result.accepted.map((label) => label.id)).toEqual(["island-title"]);
  });

  it("keeps UNREVIEWED over island summary when overlapping", () => {
    const result = cullLabels([
      {
        id: "summary",
        kind: "islandSummary",
        priority: LABEL_PRIORITIES.islandSummary,
        rect: { x: 0, y: 0, w: 80, h: 20 },
        payload: { islandId: "i1" },
      },
      {
        id: "unreviewed",
        kind: "unreviewed",
        priority: LABEL_PRIORITIES.unreviewed,
        rect: { x: 0, y: 0, w: 80, h: 20 },
        payload: { islandId: "i1" },
      },
    ]);

    expect(result.accepted.map((label) => label.id)).toEqual(["unreviewed"]);
  });
});
