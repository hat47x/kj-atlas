import { useEffect, useMemo, useState } from "react";
import {
  buildInitialWorkspaceState,
  commitWorkspaceDecision,
  normalizeFilters,
  normalizePresetInput,
  replayPreset,
  rollbackWorkspaceDecision,
  summarizeCandidatePatchDiff,
  syncWorkspaceCandidates,
  type CandidateItem,
  type QueryPreset,
  type QueryScope,
  type WorkspaceDecision,
  type WorkspaceState,
} from "../../domain/patch/workspace/ce3_patch_workspace";

type PatchWorkspacePanelProps = {
  isReadOnly?: boolean;
  candidates: CandidateItem[];
  onDecisionCommitted?: (payload: {
    candidateId: string;
    decision: WorkspaceDecision;
    previousDecision: WorkspaceDecision;
    at: string;
  }) => void;
  onDecisionRolledBack?: (payload: { restoredCandidateIds: string[]; at: string }) => void;
  onPresetSaved?: (preset: QueryPreset) => void;
  onPresetExecuted?: (payload: { query: string; scope: QueryScope; depth: number; filters: string[] }) => void;
};

const PRESET_STORAGE_KEY = "kj-atlas:ce3:patch-workspace-presets:v1";

function loadPresets(): QueryPreset[] {
  if (typeof window === "undefined") {
    return [];
  }

  const raw = window.localStorage.getItem(PRESET_STORAGE_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .filter((item): item is QueryPreset => {
        return item && typeof item === "object"
          && typeof item.id === "string"
          && typeof item.name === "string"
          && (item.scope === "all" || item.scope === "selection" || item.scope === "island")
          && typeof item.depth === "number"
          && Array.isArray(item.filters)
          && item.filters.every((value: unknown) => typeof value === "string");
      })
      .map((item) => ({
        ...item,
        depth: Math.max(1, Math.floor(item.depth)),
        filters: normalizeFilters(item.filters.join(",")),
      }));
  } catch {
    return [];
  }
}

function savePresets(presets: QueryPreset[]): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(PRESET_STORAGE_KEY, JSON.stringify(presets));
}

export function PatchWorkspacePanel({
  candidates,
  isReadOnly = false,
  onDecisionCommitted,
  onDecisionRolledBack,
  onPresetSaved,
  onPresetExecuted,
}: PatchWorkspacePanelProps) {
  const [workspaceState, setWorkspaceState] = useState<WorkspaceState>(() => buildInitialWorkspaceState(candidates));
  const [presets, setPresets] = useState<QueryPreset[]>(() => loadPresets());
  const [presetName, setPresetName] = useState("");
  const [scope, setScope] = useState<QueryScope>("all");
  const [depth, setDepth] = useState(1);
  const [filtersInput, setFiltersInput] = useState("");

  const normalizedFilters = useMemo(() => normalizeFilters(filtersInput), [filtersInput]);
  const activeCandidateId = workspaceState.selectedCandidateId ?? candidates[0]?.id ?? null;
  const activeCandidate = useMemo(
    () => candidates.find((candidate) => candidate.id === activeCandidateId) ?? null,
    [activeCandidateId, candidates]
  );
  const activePreviewSummary = useMemo(
    () => (activeCandidate?.preview ? summarizeCandidatePatchDiff(activeCandidate.preview) : null),
    [activeCandidate]
  );
  const latestAuditByCandidate = useMemo(() => {
    const latest = new Map<string, string>();
    for (const entry of workspaceState.auditLog) {
      const suffix = entry.reason === "rollback" ? " (rollback)" : "";
      latest.set(entry.candidateId, `${entry.from}→${entry.to}${suffix}`);
    }
    return latest;
  }, [workspaceState.auditLog]);

  useEffect(() => {
    setWorkspaceState((previous) => syncWorkspaceCandidates(previous, candidates));
  }, [candidates]);

  const commitDecision = (nextDecision: WorkspaceDecision) => {
    if (isReadOnly || !activeCandidateId) {
      return;
    }
    const now = new Date().toISOString();
    setWorkspaceState((previous) => {
      const previousDecision = previous.decisions[activeCandidateId] ?? "hold";
      const next = commitWorkspaceDecision(previous, activeCandidateId, nextDecision, now);
      if (next !== previous) {
        onDecisionCommitted?.({
          candidateId: activeCandidateId,
          decision: nextDecision,
          previousDecision,
          at: now,
        });
      }
      return next;
    });
  };

  const handleRollback = () => {
    if (isReadOnly) {
      return;
    }
    const now = new Date().toISOString();
    setWorkspaceState((previous) => {
      const next = rollbackWorkspaceDecision(previous, now);
      if (next.phase !== "error") {
        const restoredCandidateIds = Object.keys(next.decisions).filter((candidateId) => {
          const before = previous.decisions[candidateId] ?? "hold";
          const after = next.decisions[candidateId] ?? "hold";
          return before !== after;
        });
        if (restoredCandidateIds.length > 0) {
          onDecisionRolledBack?.({ restoredCandidateIds, at: now });
        }
      }
      return next;
    });
  };

  const handleSavePreset = () => {
    if (isReadOnly) {
      return;
    }

    const trimmedName = presetName.trim();
    if (!trimmedName) {
      setWorkspaceState((previous) => ({ ...previous, failureMessage: "Preset name is required.", phase: "error" }));
      return;
    }

    const nextPreset: QueryPreset = {
      id: crypto.randomUUID(),
      name: trimmedName,
      scope,
      depth: Math.max(1, Math.floor(depth)),
      filters: normalizedFilters,
    };

    const nextPresets = [...presets, nextPreset].sort((left, right) => left.name.localeCompare(right.name));
    setPresets(nextPresets);
    savePresets(nextPresets);
    onPresetSaved?.(nextPreset);
    setWorkspaceState((previous) => ({ ...previous, failureMessage: null }));
  };

  const runPreset = (preset: Pick<QueryPreset, "scope" | "depth" | "filters">) => {
    if (isReadOnly) {
      return;
    }
    const normalizedPreset = normalizePresetInput(preset);
    setWorkspaceState((previous) => {
      const next = replayPreset(previous, normalizedPreset, candidates.length > 0);
      if (next.phase !== "error" && next.lastExecutedQuery) {
        onPresetExecuted?.({
          query: next.lastExecutedQuery,
          scope: normalizedPreset.scope,
          depth: normalizedPreset.depth,
          filters: [...normalizedPreset.filters],
        });
      }
      return next;
    });
  };

  return (
    <section style={{ border: "1px solid #cbd5e1", borderRadius: 8, padding: 12, marginTop: 12, backgroundColor: "#f8fafc" }} data-testid="ce3-workspace-panel">
      <div style={{ fontWeight: 700, marginBottom: 6 }}>CE3 Patch workspace</div>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        Compare candidates, record adopt/reject/hold decisions, and recover with one-click rollback.
      </div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }} data-testid="ce3-perspective-scope">
        Perspective controls remain display-only and are not persisted by CE3 presets.
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, marginBottom: 8 }}>
        <select
          data-testid="ce3-candidate-select"
          value={activeCandidateId ?? ""}
          disabled={isReadOnly || candidates.length === 0}
          onChange={(event) => {
            setWorkspaceState((previous) => ({
              ...previous,
              selectedCandidateId: event.target.value || null,
            }));
          }}
        >
          {candidates.length === 0 ? <option value="">No candidates yet</option> : null}
          {candidates.map((candidate) => (
            <option key={candidate.id} value={candidate.id}>{candidate.label}</option>
          ))}
        </select>
        <div style={{ display: "flex", gap: 6 }}>
          <button type="button" data-testid="ce3-adopt" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("adopt")}>Adopt (partial)</button>
          <button type="button" data-testid="ce3-hold" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("hold")}>Hold</button>
          <button type="button" data-testid="ce3-reject" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("reject")}>Discard</button>
        </div>
      </div>
      <div data-testid="ce3-decision-state" style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>
        Decision state: {activeCandidateId ? workspaceState.decisions[activeCandidateId] ?? "hold" : "none"} (phase: {workspaceState.phase})
      </div>
      <div
        data-testid="ce3-candidate-state-list"
        style={{ border: "1px solid #e2e8f0", borderRadius: 6, backgroundColor: "#ffffff", padding: 8, marginBottom: 8 }}
      >
        <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a", marginBottom: 4 }}>
          Candidate decisions
          <span data-testid="ce3-candidate-count" style={{ marginLeft: 6, color: "#64748b", fontWeight: 500 }}>
            ({candidates.length})
          </span>
        </div>
        {candidates.length === 0 ? <div style={{ fontSize: 11, color: "#64748b" }}>No candidates collected yet.</div> : null}
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            style={{ display: "flex", justifyContent: "space-between", gap: 8, fontSize: 11, color: "#334155", marginBottom: 2 }}
          >
            <span data-testid={`ce3-candidate-state-${candidate.id}`}>
              {candidate.label}: {workspaceState.decisions[candidate.id] ?? "hold"}
            </span>
            <span data-testid={`ce3-candidate-audit-${candidate.id}`} style={{ color: "#64748b" }}>
              {latestAuditByCandidate.get(candidate.id) ?? "no transition"}
            </span>
          </div>
        ))}
      </div>
      <div
        data-testid="ce3-diff-preview"
        style={{ border: "1px dashed #cbd5e1", borderRadius: 6, padding: 8, marginBottom: 8, backgroundColor: "#ffffff" }}
      >
        <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a", marginBottom: 4 }}>Patch diff preview</div>
        {activeCandidate?.preview ? (
          <>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              Source snippets ({activeCandidate.preview.sourceSnippets.length}): {activeCandidate.preview.sourceSnippets.join(" / ")}
            </div>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              Draft patch: {activeCandidate.preview.draftText}
            </div>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              Edited patch: {activeCandidate.preview.editedText ?? activeCandidate.preview.draftText}
            </div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              Token delta: +{activePreviewSummary?.additions ?? 0} / -{activePreviewSummary?.removals ?? 0}
              {activePreviewSummary?.hasChanges ? "" : " (no textual change)"}
            </div>
          </>
        ) : (
          <div style={{ fontSize: 11, color: "#64748b" }}>No patch preview available for the selected candidate.</div>
        )}
      </div>
      <button type="button" data-testid="ce3-rollback" disabled={isReadOnly || workspaceState.rollbackStack.length === 0} onClick={handleRollback}>
        Roll back last workspace decision
      </button>

      <hr style={{ border: 0, borderTop: "1px solid #e2e8f0", margin: "12px 0" }} />

      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>Query preset</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr)) auto", gap: 6, marginBottom: 8 }}>
        <input data-testid="ce3-preset-name" value={presetName} onChange={(event) => setPresetName(event.target.value)} placeholder="Preset name" disabled={isReadOnly} />
        <select data-testid="ce3-preset-scope" value={scope} onChange={(event) => setScope(event.target.value as QueryScope)} disabled={isReadOnly}>
          <option value="all">all</option>
          <option value="selection">selection</option>
          <option value="island">island</option>
        </select>
        <input data-testid="ce3-preset-depth" type="number" min={1} value={depth} onChange={(event) => setDepth(Number(event.target.value))} disabled={isReadOnly} />
        <input
          data-testid="ce3-preset-filters"
          value={filtersInput}
          onChange={(event) => setFiltersInput(event.target.value)}
          placeholder="filters (comma separated)"
          disabled={isReadOnly}
        />
        <button type="button" data-testid="ce3-save-preset" disabled={isReadOnly} onClick={handleSavePreset}>Save preset</button>
      </div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        {presets.length === 0 ? <span style={{ fontSize: 12, color: "#64748b" }}>No saved presets.</span> : null}
        {presets.map((preset) => (
          <button key={preset.id} type="button" data-testid={`ce3-run-preset-${preset.id}`} disabled={isReadOnly} onClick={() => runPreset(preset)}>
            Run {preset.name}
          </button>
        ))}
      </div>
      <button
        type="button"
        data-testid="ce3-run-inline-preset"
        disabled={isReadOnly}
        onClick={() => {
          runPreset({
            scope,
            depth: Math.max(1, Math.floor(depth)),
            filters: normalizedFilters,
          });
        }}
      >
        Run current preset
      </button>
      <div data-testid="ce3-normalized-query" style={{ fontSize: 12, color: "#334155", marginTop: 8 }}>
        Normalized query: {workspaceState.lastExecutedQuery ?? "(not executed)"}
      </div>
      <div data-testid="ce3-audit-log-size" style={{ fontSize: 12, color: "#334155", marginTop: 6 }}>
        Audit transitions: {workspaceState.auditLog.length}
      </div>
      {workspaceState.failureMessage ? (
        <div data-testid="ce3-failure" style={{ marginTop: 8, fontSize: 12, color: "#b91c1c" }}>
          {workspaceState.failureMessage}
        </div>
      ) : null}
      <div style={{ marginTop: 8, fontSize: 11, color: "#64748b" }}>
        Recovery path: if execution fails, recover by collecting candidates again and rolling back the last workspace decision.
      </div>
    </section>
  );
}
