import { describe, expect, it } from "vitest";
import {
  buildInitialWorkspaceState,
  commitWorkspaceDecision,
  normalizeFilters,
  normalizePresetQuery,
  replayPreset,
  rollbackWorkspaceDecision,
  summarizeCandidatePatchDiff,
  syncWorkspaceCandidates,
} from "./ce3_patch_workspace";

describe("ce3_patch_workspace", () => {
  it("supports hold/adopt/reject transitions and rollback", () => {
    const initial = buildInitialWorkspaceState([
      { id: "cand-1", label: "cand-1" },
      { id: "cand-2", label: "cand-2" },
    ]);

    const adopted = commitWorkspaceDecision(initial, "cand-1", "adopt", "2026-04-11T00:00:00.000Z");
    const rejected = commitWorkspaceDecision(adopted, "cand-2", "reject", "2026-04-11T00:00:01.000Z");
    const rolledBack = rollbackWorkspaceDecision(rejected, "2026-04-11T00:00:02.000Z");

    expect(initial.decisions["cand-1"]).toBe("hold");
    expect(adopted.decisions["cand-1"]).toBe("adopt");
    expect(rejected.decisions["cand-2"]).toBe("reject");
    expect(rejected.auditLog).toHaveLength(2);
    expect(rolledBack.decisions["cand-2"]).toBe("hold");
    expect(rolledBack.auditLog).toHaveLength(3);
    expect(rolledBack.auditLog[2]).toMatchObject({
      candidateId: "cand-2",
      from: "reject",
      to: "hold",
      at: "2026-04-11T00:00:02.000Z",
      reason: "rollback",
    });
    expect(rolledBack.rollbackStack).toHaveLength(1);
    expect(rolledBack.phase).toBe("rollback_ready");
  });

  it("keeps other candidate decisions when rolling back the latest transition", () => {
    const initial = buildInitialWorkspaceState([
      { id: "cand-a", label: "cand-a" },
      { id: "cand-b", label: "cand-b" },
    ]);

    const adoptA = commitWorkspaceDecision(initial, "cand-a", "adopt", "2026-04-11T00:00:00.000Z");
    const rejectB = commitWorkspaceDecision(adoptA, "cand-b", "reject", "2026-04-11T00:00:01.000Z");
    const rolledBack = rollbackWorkspaceDecision(rejectB);

    expect(rolledBack.decisions["cand-a"]).toBe("adopt");
    expect(rolledBack.decisions["cand-b"]).toBe("hold");
    expect(rolledBack.auditLog).toHaveLength(3);
    expect(rolledBack.auditLog[2]).toMatchObject({
      candidateId: "cand-b",
      from: "reject",
      to: "hold",
      reason: "rollback",
    });
  });

  it("supports three candidates and keeps untouched candidate state during rollback", () => {
    const initial = buildInitialWorkspaceState([
      { id: "cand-alpha", label: "cand-alpha" },
      { id: "cand-beta", label: "cand-beta" },
      { id: "cand-gamma", label: "cand-gamma" },
    ]);

    const adoptAlpha = commitWorkspaceDecision(initial, "cand-alpha", "adopt", "2026-04-12T00:00:00.000Z");
    const rejectBeta = commitWorkspaceDecision(adoptAlpha, "cand-beta", "reject", "2026-04-12T00:00:01.000Z");
    const rolledBack = rollbackWorkspaceDecision(rejectBeta);

    expect(rolledBack.decisions["cand-alpha"]).toBe("adopt");
    expect(rolledBack.decisions["cand-beta"]).toBe("hold");
    expect(rolledBack.decisions["cand-gamma"]).toBe("hold");
    expect(rolledBack.auditLog).toHaveLength(3);
    expect(rolledBack.auditLog.map((entry) => entry.candidateId)).toEqual(["cand-alpha", "cand-beta", "cand-beta"]);
    expect(rolledBack.auditLog[2]).toMatchObject({
      candidateId: "cand-beta",
      reason: "rollback",
    });
  });

  it("does not add extra audit transitions when the same decision is re-applied", () => {
    const initial = buildInitialWorkspaceState([{ id: "cand-a", label: "cand-a" }]);
    const adopted = commitWorkspaceDecision(initial, "cand-a", "adopt", "2026-04-11T00:00:00.000Z");
    const adoptedAgain = commitWorkspaceDecision(adopted, "cand-a", "adopt", "2026-04-11T00:00:01.000Z");

    expect(adoptedAgain.decisions["cand-a"]).toBe("adopt");
    expect(adoptedAgain.auditLog).toHaveLength(1);
    expect(adoptedAgain.rollbackStack).toHaveLength(1);
    expect(adoptedAgain.phase).toBe("rollback_ready");
  });

  it("normalizes preset query deterministically", () => {
    expect(normalizeFilters(" b, A,  ,c ")).toEqual(["a", "b", "c"]);
    expect(
      normalizePresetQuery({
        scope: "selection",
        depth: 2.8,
        filters: ["z", "a"],
      })
    ).toBe('{"scope":"selection","depth":2,"filters":["a","z"]}');
    expect(
      normalizePresetQuery({
        scope: "all",
        depth: Number.NaN,
        filters: ["risk"],
      })
    ).toBe('{"scope":"all","depth":1,"filters":["risk"]}');
  });

  it("syncs candidate list without mutating existing decision history", () => {
    const initial = buildInitialWorkspaceState([{ id: "cand-1", label: "cand-1" }]);
    const transitioned = commitWorkspaceDecision(initial, "cand-1", "adopt", "2026-04-11T00:00:00.000Z");
    const synced = syncWorkspaceCandidates(transitioned, [
      { id: "cand-1", label: "cand-1" },
      { id: "cand-3", label: "cand-3" },
    ]);

    expect(synced.decisions["cand-1"]).toBe("adopt");
    expect(synced.decisions["cand-3"]).toBe("hold");
    expect(synced.auditLog).toHaveLength(1);
  });

  it("replays presets and returns recoverable error when no candidates exist", () => {
    const initial = buildInitialWorkspaceState([]);
    const failed = replayPreset(initial, { scope: "all", depth: 1, filters: [] }, false);
    expect(failed.phase).toBe("error");
    expect(failed.failureMessage).toContain("No candidates available");

    const restored = buildInitialWorkspaceState([{ id: "cand-1", label: "cand-1" }]);
    const replayed = replayPreset(restored, { scope: "selection", depth: 2, filters: ["risk", "merge"] }, true);
    expect(replayed.phase).toBe("preset_replayed");
    expect(replayed.lastExecutedQuery).toBe('{"scope":"selection","depth":2,"filters":["merge","risk"]}');
  });

  it("summarizes patch preview token delta for CE3 diff preview", () => {
    const summary = summarizeCandidatePatchDiff({
      sourceSnippets: ["alpha beta", "beta gamma"],
      draftText: "alpha gamma delta",
      editedText: "alpha delta epsilon",
    });

    expect(summary.additions).toBe(2);
    expect(summary.removals).toBe(3);
    expect(summary.hasChanges).toBe(true);
  });
});
