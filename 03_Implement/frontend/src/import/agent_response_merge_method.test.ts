import { describe, expect, it } from "vitest";

import { parseAgentResponse } from "./agent_response_import";

function payload(content: Record<string, unknown>) {
  return JSON.stringify({
    schemaVersion: "agent-response.v1",
    taskId: "task-1",
    proposals: [{
      proposalId: "p1",
      kind: "merge_candidate",
      targetRef: { cardIds: ["c1", "c2"] },
      content,
      rationale: "意味を保って統合する",
    }],
  });
}

describe("external merge candidate mergeMethod", () => {
  it.each(["near_duplicate", "kernel_fusion"] as const)("keeps explicit %s", (mergeMethod) => {
    const result = parseAgentResponse(payload({ mergedText: "統合案", mergeMethod }), "lenient");
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.response.proposals[0]?.content.mergeMethod).toBe(mergeMethod);
  });

  it.each([undefined, "unknown_method"])("does not infer %s", (mergeMethod) => {
    const content = mergeMethod === undefined ? { mergedText: "統合案" } : { mergedText: "統合案", mergeMethod };
    const result = parseAgentResponse(payload(content), "lenient");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.response.proposals).toHaveLength(0);
      expect(result.warnings.some((warning) => warning.includes("merge_candidate_missing_or_invalid_merge_method"))).toBe(true);
    }
  });
});
