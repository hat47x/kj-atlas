import { beforeEach, describe, expect, it, vi } from "vitest";
import type { AgentTaskCorrelation } from "../export/agent_task_export";
import { loadAgentTaskLedger, recordAgentTaskExport, verifyAgentResponseCorrelation } from "./agent_task_ledger";

const correlation: AgentTaskCorrelation = {
  schemaVersion: "agent-task.v1",
  taskId: "task-1",
  createdAt: "2026-08-11T00:00:00.000Z",
  docId: "doc-1",
  baseDocSignature: "doc-1:revision-1",
  bundleHash: "bundle-1",
  queryCanonicalHash: "query-1",
  taskKind: "free_analysis",
  locale: "ja",
};

function storageMock(): Storage {
  const values = new Map<string, string>();
  return {
    get length() { return values.size; },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => { values.delete(key); },
    setItem: (key, value) => { values.set(key, value); },
  };
}

describe("agent task ledger", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { localStorage: storageMock() });
  });

  it("records an export and verifies the exact correlation against the current document", () => {
    recordAgentTaskExport(correlation);
    expect(loadAgentTaskLedger()).toHaveLength(1);
    expect(verifyAgentResponseCorrelation("task-1", correlation, { id: "doc-1", updatedAt: "revision-1" })).toEqual({
      ok: true,
      provenance: "verified-local-export",
    });
  });

  it.each([
    [{ ...correlation, docId: "doc-2" }, "payload.correlation_document_mismatch"],
    [{ ...correlation, baseDocSignature: "doc-1:old" }, "payload.correlation_stale_base"],
    [{ ...correlation, bundleHash: "tampered" }, "payload.correlation_export_mismatch"],
  ])("rejects invalid correlation", (candidate, error) => {
    recordAgentTaskExport(correlation);
    expect(verifyAgentResponseCorrelation("task-1", candidate, { id: "doc-1", updatedAt: "revision-1" })).toEqual({ ok: false, error });
  });

  it("labels legacy responses without claiming authenticity", () => {
    expect(verifyAgentResponseCorrelation("task-1", undefined, { id: "doc-1", updatedAt: "revision-1" })).toEqual({
      ok: true,
      provenance: "unverified-legacy",
      warning: "payload.provenance_unverified_legacy",
    });
  });
});
