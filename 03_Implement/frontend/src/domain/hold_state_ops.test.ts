import { describe, expect, it } from "vitest";
import type { Card } from "./types";
import { updateCardHoldState } from "./hold_state_ops";

const cards: Card[] = [
  { id: "card-1", text: "one", x: 0, y: 0 },
  { id: "card-2", text: "two", x: 10, y: 10, holdState: "held" },
];

describe("updateCardHoldState", () => {
  it("sets a selected hold state without changing other cards", () => {
    const result = updateCardHoldState(cards, "card-1", "pending");

    expect(result[0]).toEqual({ ...cards[0], holdState: "pending" });
    expect(result[1]).toBe(cards[1]);
  });

  it("restores active state by removing the optional field", () => {
    const result = updateCardHoldState(cards, "card-2", "active");

    expect(result[1]).toEqual({ id: "card-2", text: "two", x: 10, y: 10 });
    expect("holdState" in result[1]).toBe(false);
  });

  it("preserves object identity when the selection is unchanged", () => {
    const result = updateCardHoldState(cards, "card-2", "held");

    expect(result[0]).toBe(cards[0]);
    expect(result[1]).toBe(cards[1]);
  });
});
