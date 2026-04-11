import { useEffect, useMemo, useState } from "react";
import {
  buildInitialWorkspaceState,
  commitWorkspaceDecision,
  normalizeFilters,
  replayPreset,
  rollbackWorkspaceDecision,
  syncWorkspaceCandidates,
  type CandidateItem,
  type QueryPreset,
  type QueryScope,
  type WorkspaceDecision,
  type WorkspaceState,
} from "../domain/ce3_patch_workspace";

type PatchWorkspacePanelProps = {
  isReadOnly?: boolean;
  candidates: CandidateItem[];
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

export function PatchWorkspacePanel({ candidates, isReadOnly = false }: PatchWorkspacePanelProps) {
  const [workspaceState, setWorkspaceState] = useState<WorkspaceState>(() => buildInitialWorkspaceState(candidates));
  const [presets, setPresets] = useState<QueryPreset[]>(() => loadPresets());
  const [presetName, setPresetName] = useState("");
  const [scope, setScope] = useState<QueryScope>("all");
  const [depth, setDepth] = useState(1);
  const [filtersInput, setFiltersInput] = useState("");

  const normalizedFilters = useMemo(() => normalizeFilters(filtersInput), [filtersInput]);
  const activeCandidateId = workspaceState.selectedCandidateId ?? candidates[0]?.id ?? null;

  useEffect(() => {
    setWorkspaceState((previous) => syncWorkspaceCandidates(previous, candidates));
  }, [candidates]);

  const commitDecision = (nextDecision: WorkspaceDecision) => {
    if (isReadOnly || !activeCandidateId) {
      return;
    }

    setWorkspaceState((previous) => commitWorkspaceDecision(previous, activeCandidateId, nextDecision, new Date().toISOString()));
  };

  const handleRollback = () => {
    setWorkspaceState((previous) => rollbackWorkspaceDecision(previous));
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
    setWorkspaceState((previous) => ({ ...previous, failureMessage: null }));
  };

  const runPreset = (preset: Pick<QueryPreset, "scope" | "depth" | "filters">) => {
    setWorkspaceState((previous) => replayPreset(previous, preset, candidates.length > 0));
  };

  return (
    <section style={{ border: "1px solid #cbd5e1", borderRadius: 8, padding: 12, marginTop: 12, backgroundColor: "#f8fafc" }} data-testid="ce3-workspace-panel">
      <div style={{ fontWeight: 700, marginBottom: 6 }}>CE3 Patch workspace</div>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        Compare candidates, record adopt/reject/hold decisions, and recover with one-click rollback.
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
          <button type="button" data-testid="ce3-adopt" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("adopt")}>Adopt</button>
          <button type="button" data-testid="ce3-hold" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("hold")}>Hold</button>
          <button type="button" data-testid="ce3-reject" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("reject")}>Reject</button>
        </div>
      </div>
      <div data-testid="ce3-decision-state" style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>
        Decision state: {activeCandidateId ? workspaceState.decisions[activeCandidateId] ?? "hold" : "none"} (phase: {workspaceState.phase})
      </div>
      <button type="button" data-testid="ce3-rollback" disabled={isReadOnly || workspaceState.rollbackStack.length === 0} onClick={handleRollback}>
        Roll back last workspace decision
      </button>

      <hr style={{ border: 0, borderTop: "1px solid #e2e8f0", margin: "12px 0" }} />

      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>Query preset</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr)) auto", gap: 6, marginBottom: 8 }}>
        <input data-testid="ce3-preset-name" value={presetName} onChange={(event) => setPresetName(event.target.value)} placeholder="Preset name" />
        <select data-testid="ce3-preset-scope" value={scope} onChange={(event) => setScope(event.target.value as QueryScope)}>
          <option value="all">all</option>
          <option value="selection">selection</option>
          <option value="island">island</option>
        </select>
        <input data-testid="ce3-preset-depth" type="number" min={1} value={depth} onChange={(event) => setDepth(Number(event.target.value))} />
        <input
          data-testid="ce3-preset-filters"
          value={filtersInput}
          onChange={(event) => setFiltersInput(event.target.value)}
          placeholder="filters (comma separated)"
        />
        <button type="button" data-testid="ce3-save-preset" disabled={isReadOnly} onClick={handleSavePreset}>Save preset</button>
      </div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        {presets.length === 0 ? <span style={{ fontSize: 12, color: "#64748b" }}>No saved presets.</span> : null}
        {presets.map((preset) => (
          <button key={preset.id} type="button" data-testid={`ce3-run-preset-${preset.id}`} onClick={() => runPreset(preset)}>
            Run {preset.name}
          </button>
        ))}
      </div>
      <button
        type="button"
        data-testid="ce3-run-inline-preset"
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
