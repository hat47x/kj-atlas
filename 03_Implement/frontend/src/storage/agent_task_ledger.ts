import type { AgentTaskCorrelation } from "../export/agent_task_export";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const STORAGE_KEY = "kj-atlas/agent-task-ledger-v1";
const MAX_ENTRIES = 100;

export type AgentTaskLedgerEntry = AgentTaskCorrelation & { exportedAt: string };
export type AgentResponseProvenance = "verified-local-export" | "unverified-legacy";

function key(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(STORAGE_KEY, scope) : STORAGE_KEY;
}

function available(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function loadAgentTaskLedger(scope?: TenantBrowserStorageScope): AgentTaskLedgerEntry[] {
  if (!available()) return [];
  try {
    const value = JSON.parse(window.localStorage.getItem(key(scope)) ?? "[]") as unknown;
    if (!Array.isArray(value)) return [];
    return value.filter((entry): entry is AgentTaskLedgerEntry => Boolean(
      entry && typeof entry === "object" && typeof (entry as AgentTaskLedgerEntry).taskId === "string"
      && typeof (entry as AgentTaskLedgerEntry).docId === "string" && typeof (entry as AgentTaskLedgerEntry).bundleHash === "string",
    )).slice(-MAX_ENTRIES);
  } catch {
    return [];
  }
}

export function recordAgentTaskExport(correlation: AgentTaskCorrelation, scope?: TenantBrowserStorageScope): void {
  if (!available()) return;
  const entries = loadAgentTaskLedger(scope).filter((entry) => entry.taskId !== correlation.taskId);
  entries.push({ ...correlation, exportedAt: new Date().toISOString() });
  try {
    window.localStorage.setItem(key(scope), JSON.stringify(entries.slice(-MAX_ENTRIES)));
  } catch {
    // The export still succeeds when browser storage is unavailable or full.
  }
}

export type CorrelationVerification =
  | { ok: true; provenance: "verified-local-export" }
  | { ok: true; provenance: "unverified-legacy"; warning: string }
  | { ok: false; error: string };

export function verifyAgentResponseCorrelation(
  taskId: string,
  correlation: AgentTaskCorrelation | undefined,
  currentDoc: { id: string; updatedAt: string },
  scope?: TenantBrowserStorageScope,
): CorrelationVerification {
  if (!correlation) return { ok: true, provenance: "unverified-legacy", warning: "payload.provenance_unverified_legacy" };
  if (correlation.taskId !== taskId) return { ok: false, error: "payload.correlation_taskId_mismatch" };
  if (correlation.docId !== currentDoc.id) return { ok: false, error: "payload.correlation_document_mismatch" };
  if (correlation.baseDocSignature !== `${currentDoc.id}:${currentDoc.updatedAt}`) {
    return { ok: false, error: "payload.correlation_stale_base" };
  }
  const recorded = loadAgentTaskLedger(scope).find((entry) => entry.taskId === taskId);
  if (!recorded) return { ok: false, error: "payload.correlation_unknown_task" };
  const fields: (keyof AgentTaskCorrelation)[] = [
    "schemaVersion", "taskId", "createdAt", "docId", "baseDocSignature", "bundleHash", "queryCanonicalHash", "taskKind", "locale",
  ];
  if (fields.some((field) => recorded[field] !== correlation[field])) {
    return { ok: false, error: "payload.correlation_export_mismatch" };
  }
  return { ok: true, provenance: "verified-local-export" };
}
