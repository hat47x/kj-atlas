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
  type WorkspacePhase,
  type WorkspaceState,
} from "../../domain/patch/workspace/ce3_patch_workspace";
import { t } from "../../i18n/translate";
import { loadQueryPresets, saveQueryPresets } from "../../storage/query_presets";
import type { TenantBrowserStorageScope } from "../../storage/tenant_scope";

type PatchWorkspacePanelProps = {
  isReadOnly?: boolean;
  storageScope?: TenantBrowserStorageScope;
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

function formatWorkspaceDecision(decision: WorkspaceDecision | "none"): string {
  if (decision === "adopt") return t("patch_workspace.decision.adopt");
  if (decision === "reject") return t("patch_workspace.decision.reject");
  if (decision === "none") return t("patch_workspace.decision.none");
  return t("patch_workspace.decision.hold");
}

const QUERY_SCOPES = ["all", "selection", "island"] as const;
function parseQueryScope(raw: string): QueryScope {
  return QUERY_SCOPES.includes(raw as QueryScope) ? (raw as QueryScope) : "all";
}

function formatQueryScope(scope: QueryScope): string {
  if (scope === "selection") return t("patch_workspace.scope.selection");
  if (scope === "island") return t("patch_workspace.scope.island");
  return t("patch_workspace.scope.all");
}

function formatWorkspacePhase(phase: WorkspacePhase): string {
  return t(`patch_workspace.phase.${phase}`);
}

function formatFailureMessage(message: string): string {
  if (message === "No rollback point available.") {
    return t("patch_workspace.failure.no_rollback_point");
  }
  if (message === "No candidates available. Collect candidates before preset execution.") {
    return t("patch_workspace.failure.no_candidates");
  }
  return message;
}

function formatExecutedQuery(query: string): string {
  try {
    const parsed = JSON.parse(query) as Partial<{ scope: QueryScope; depth: number; filters: string[] }>;
    if (
      (parsed.scope === "all" || parsed.scope === "selection" || parsed.scope === "island")
      && typeof parsed.depth === "number"
      && Array.isArray(parsed.filters)
      && parsed.filters.every((filter) => typeof filter === "string")
    ) {
      return t("patch_workspace.executed_query_summary", {
        scope: formatQueryScope(parsed.scope),
        depth: parsed.depth,
        filters: parsed.filters.length > 0 ? parsed.filters.join(", ") : t("patch_workspace.no_filters"),
      });
    }
  } catch {
    // Keep unknown diagnostic values visible.
  }
  return query;
}

export function PatchWorkspacePanel({
  candidates,
  isReadOnly = false,
  storageScope,
  onDecisionCommitted,
  onDecisionRolledBack,
  onPresetSaved,
  onPresetExecuted,
}: PatchWorkspacePanelProps) {
  const [workspaceState, setWorkspaceState] = useState<WorkspaceState>(() => buildInitialWorkspaceState(candidates));
  const [presets, setPresets] = useState<QueryPreset[]>(() => loadQueryPresets(storageScope));
  const [presetName, setPresetName] = useState("");
  const [scope, setScope] = useState<QueryScope>("all");
  const [depth, setDepth] = useState(1);
  const [filtersInput, setFiltersInput] = useState("");

  const normalizedFilters = useMemo(() => normalizeFilters(filtersInput), [filtersInput]);

  useEffect(() => {
    setPresets(loadQueryPresets(storageScope));
    setPresetName("");
    setScope("all");
    setDepth(1);
    setFiltersInput("");
  }, [storageScope?.deployment, storageScope?.principalId, storageScope?.tenantId]);
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
      const suffix = entry.reason === "rollback" ? t("patch_workspace.rollback_suffix") : "";
      latest.set(entry.candidateId, `${t("patch_workspace.transition", {
        from: formatWorkspaceDecision(entry.from),
        to: formatWorkspaceDecision(entry.to),
      })}${suffix}`);
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
      setWorkspaceState((previous) => ({ ...previous, failureMessage: t("patch_workspace.preset_name_required"), phase: "error" }));
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
    saveQueryPresets(nextPresets, storageScope);
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
      <div style={{ fontWeight: 700, marginBottom: 6 }}>{t("patch_workspace.title")}</div>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        {t("patch_workspace.description")}
      </div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }} data-testid="ce3-perspective-scope">
        {t("patch_workspace.perspective_scope")}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, marginBottom: 8 }}>
        <select
          data-testid="ce3-candidate-select"
          aria-label={t("patch_workspace.candidate_select_label")}
          value={activeCandidateId ?? ""}
          disabled={isReadOnly || candidates.length === 0}
          onChange={(event) => {
            setWorkspaceState((previous) => ({
              ...previous,
              selectedCandidateId: event.target.value || null,
            }));
          }}
        >
          {candidates.length === 0 ? <option value="">{t("patch_workspace.no_candidates_yet")}</option> : null}
          {candidates.map((candidate) => (
            <option key={candidate.id} value={candidate.id}>{candidate.label}</option>
          ))}
        </select>
        <div style={{ display: "flex", gap: 6 }}>
          <button type="button" data-testid="ce3-adopt" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("adopt")}>{t("patch_workspace.action.adopt")}</button>
          <button type="button" data-testid="ce3-hold" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("hold")}>{t("patch_workspace.action.hold")}</button>
          <button type="button" data-testid="ce3-reject" disabled={isReadOnly || !activeCandidateId} onClick={() => commitDecision("reject")}>{t("patch_workspace.action.discard")}</button>
        </div>
      </div>
      <div data-testid="ce3-decision-state" style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>
        {t("patch_workspace.decision_state", {
          decision: activeCandidateId ? formatWorkspaceDecision(workspaceState.decisions[activeCandidateId] ?? "hold") : formatWorkspaceDecision("none"),
          phase: formatWorkspacePhase(workspaceState.phase),
        })}
      </div>
      <div
        data-testid="ce3-candidate-state-list"
        style={{ border: "1px solid #e2e8f0", borderRadius: 6, backgroundColor: "#ffffff", padding: 8, marginBottom: 8 }}
      >
        <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a", marginBottom: 4 }}>
          {t("patch_workspace.candidate_decisions")}
          <span data-testid="ce3-candidate-count" style={{ marginLeft: 6, color: "#64748b", fontWeight: 500 }}>
            ({candidates.length})
          </span>
        </div>
        {candidates.length === 0 ? <div style={{ fontSize: 11, color: "#64748b" }}>{t("patch_workspace.no_candidates_collected")}</div> : null}
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            style={{ display: "flex", justifyContent: "space-between", gap: 8, fontSize: 11, color: "#334155", marginBottom: 2 }}
          >
            <span data-testid={`ce3-candidate-state-${candidate.id}`}>
              {candidate.label}: {formatWorkspaceDecision(workspaceState.decisions[candidate.id] ?? "hold")}
            </span>
            <span data-testid={`ce3-candidate-audit-${candidate.id}`} style={{ color: "#64748b" }}>
              {latestAuditByCandidate.get(candidate.id) ?? t("patch_workspace.no_transition")}
            </span>
          </div>
        ))}
      </div>
      <div
        data-testid="ce3-diff-preview"
        style={{ border: "1px dashed #cbd5e1", borderRadius: 6, padding: 8, marginBottom: 8, backgroundColor: "#ffffff" }}
      >
        <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a", marginBottom: 4 }}>{t("patch_workspace.diff_preview")}</div>
        {activeCandidate?.preview ? (
          <>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              {t("patch_workspace.source_snippets", { count: activeCandidate.preview.sourceSnippets.length })}: {activeCandidate.preview.sourceSnippets.join(" / ")}
            </div>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              {t("patch_workspace.draft_patch")}: {activeCandidate.preview.draftText}
            </div>
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 4 }}>
              {t("patch_workspace.edited_patch")}: {activeCandidate.preview.editedText ?? activeCandidate.preview.draftText}
            </div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              {t("patch_workspace.token_delta", { additions: activePreviewSummary?.additions ?? 0, removals: activePreviewSummary?.removals ?? 0 })}
              {activePreviewSummary?.hasChanges ? "" : t("patch_workspace.no_textual_change_suffix")}
            </div>
          </>
        ) : (
          <div style={{ fontSize: 11, color: "#64748b" }}>{t("patch_workspace.no_patch_preview")}</div>
        )}
      </div>
      <button type="button" data-testid="ce3-rollback" disabled={isReadOnly || workspaceState.rollbackStack.length === 0} onClick={handleRollback}>
        {t("patch_workspace.rollback")}
      </button>

      <hr style={{ border: 0, borderTop: "1px solid #e2e8f0", margin: "12px 0" }} />

      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>{t("patch_workspace.query_preset")}</div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>{t("patch_workspace.device_local_hint")}</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr)) auto", gap: 6, marginBottom: 8 }}>
        <input data-testid="ce3-preset-name" value={presetName} onChange={(event) => setPresetName(event.target.value)} placeholder={t("patch_workspace.preset_name")} disabled={isReadOnly} />
        <select data-testid="ce3-preset-scope" aria-label={t("patch_workspace.preset_scope_label")} value={scope} onChange={(event) => setScope(parseQueryScope(event.target.value))} disabled={isReadOnly}>
          <option value="all">{formatQueryScope("all")}</option>
          <option value="selection">{formatQueryScope("selection")}</option>
          <option value="island">{formatQueryScope("island")}</option>
        </select>
        <input data-testid="ce3-preset-depth" aria-label={t("patch_workspace.preset_depth_label")} type="number" min={1} value={depth} onChange={(event) => setDepth(Number(event.target.value))} disabled={isReadOnly} />
        <input
          data-testid="ce3-preset-filters"
          value={filtersInput}
          onChange={(event) => setFiltersInput(event.target.value)}
          placeholder={t("patch_workspace.filters_placeholder")}
          disabled={isReadOnly}
        />
        <button type="button" data-testid="ce3-save-preset" disabled={isReadOnly} onClick={handleSavePreset}>{t("patch_workspace.save_preset")}</button>
      </div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        {presets.length === 0 ? <span style={{ fontSize: 12, color: "#64748b" }}>{t("patch_workspace.no_saved_presets")}</span> : null}
        {presets.map((preset) => (
          <button key={preset.id} type="button" data-testid={`ce3-run-preset-${preset.id}`} disabled={isReadOnly} onClick={() => runPreset(preset)}>
            {t("patch_workspace.run_preset", { name: preset.name })}
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
        {t("patch_workspace.run_current_preset")}
      </button>
      <div data-testid="ce3-normalized-query" style={{ fontSize: 12, color: "#334155", marginTop: 8 }}>
        {t("patch_workspace.normalized_query", {
          query: workspaceState.lastExecutedQuery
            ? formatExecutedQuery(workspaceState.lastExecutedQuery)
            : t("patch_workspace.not_executed"),
        })}
      </div>
      <div data-testid="ce3-audit-log-size" style={{ fontSize: 12, color: "#334155", marginTop: 6 }}>
        {t("patch_workspace.audit_transitions", { count: workspaceState.auditLog.length })}
      </div>
      {workspaceState.failureMessage ? (
        <div data-testid="ce3-failure" style={{ marginTop: 8, fontSize: 12, color: "#b91c1c" }}>
          {formatFailureMessage(workspaceState.failureMessage)}
        </div>
      ) : null}
      <div style={{ marginTop: 8, fontSize: 11, color: "#64748b" }}>
        {t("patch_workspace.recovery_path")}
      </div>
    </section>
  );
}
