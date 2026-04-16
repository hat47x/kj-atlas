import { describe, expect, it } from "vitest";

import { buildCe2SuggestionCandidates, summarizeCe2ReviewStates } from "./ce2_suggestion_candidates";

describe("ce2_suggestion_candidates", () => {
  it("creates fallback candidate in proposal-only mode", () => {
    const candidates = buildCe2SuggestionCandidates({
      hasSuggestion: true,
      suggestionId: "proposal-42",
    });

    expect(candidates).toEqual([
      {
        proposalId: "proposal-42",
        label: "Current proposal",
        status: "proposed",
        reviewState: "unreviewed",
      },
    ]);
  });

  it("uses explicit candidates and summarizes review states", () => {
    const candidates = buildCe2SuggestionCandidates({
      hasSuggestion: true,
      candidates: [
        {
          proposalId: "proposal-a",
          label: "A",
          status: "proposed",
          reviewState: "unreviewed",
        },
        {
          proposalId: "proposal-b",
          label: "B",
          status: "held",
          reviewState: "human_reviewed",
        },
      ],
    });

    expect(summarizeCe2ReviewStates(candidates)).toEqual({ reviewed: 1, unreviewed: 1 });
  });
});
